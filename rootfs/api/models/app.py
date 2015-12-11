from __future__ import unicode_literals
import importlib
import logging
import re
import time
from threading import Thread
import requests

# Django
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.db import models as db_models
from django.db.models import Count, Max
from django.db.models.signals import post_delete, post_save
from django.conf import settings
from json_field.fields import JSONField

# local models
from api import utils, exceptions
from api.models import log_event, get_etcd_client
from api.models.audit import UuidAuditedModel
from api.models.config import Config
from api.models.container import Container
from api.models.release import Release

logger = logging.getLogger(__name__)


def validate_id_is_docker_compatible(value):
    """
    Check that the ID follows docker's image name constraints
    """
    match = re.match(r'^[a-z0-9-]+$', value)
    if not match:
        raise ValidationError("App IDs can only contain [a-z0-9-].")


def validate_reserved_names(value):
    """A value cannot use some reserved names."""
    if value in settings.DEIS_RESERVED_NAMES:
        raise ValidationError('{} is a reserved name.'.format(value))


def validate_app_structure(value):
    """Error if the dict values aren't ints >= 0."""
    try:
        if any(int(v) < 0 for v in value.viewvalues()):
            raise ValueError("Must be greater than or equal to zero")
    except ValueError, err:
        raise ValidationError(err)


def select_app_name():
    """Select a unique randomly generated app name"""
    name = utils.generate_app_name()

    while App.objects.filter(id=name).exists():
        name = utils.generate_app_name()

    return name


# define update/delete callbacks for synchronizing
# models with the configuration management backend


def _etcd_publish_app(**kwargs):
    appname = kwargs['instance']
    try:
        get_etcd_client().write('/deis/services/{}'.format(appname), None, dir=True)
    except KeyError:
        # Ignore error when the directory already exists.
        pass


def _etcd_purge_app(**kwargs):
    appname = kwargs['instance']
    try:
        get_etcd_client().delete('/deis/services/{}'.format(appname), dir=True, recursive=True)
    except KeyError:
        pass


@python_2_unicode_compatible
class App(UuidAuditedModel):
    """
    Application used to service requests on behalf of end-users
    """

    validators = [validate_id_is_docker_compatible, validate_reserved_names]
    owner = db_models.ForeignKey(settings.AUTH_USER_MODEL)
    id = db_models.SlugField(max_length=24, unique=True, default=select_app_name,
                             validators=validators)
    structure = JSONField(default={}, blank=True, validators=[validate_app_structure])

    class Meta:
        permissions = (('use_app', 'Can use app'),)
        db_table = 'app'
        app_label = 'api'

    @property
    def _scheduler(self):
        mod = importlib.import_module(settings.SCHEDULER_MODULE)
        return mod.SchedulerClient()

    def __str__(self):
        return self.id

    @property
    def url(self):
        return self.id + '.' + settings.DEIS_DOMAIN

    def _get_job_id(self, container_type):
        app = self.id
        release = self.release_set.latest()
        version = "v{}".format(release.version)
        job_id = "{app}_{version}.{container_type}".format(**locals())
        return job_id

    def _get_command(self, container_type):
        try:
            # if this is not procfile-based app, ensure they cannot break out
            # and run arbitrary commands on the host
            # FIXME: remove slugrunner's hardcoded entrypoint
            release = self.release_set.latest()
            if release.build.dockerfile or not release.build.sha:
                return "bash -c '{}'".format(release.build.procfile[container_type])

            return 'start {}'.format(container_type)
        # if the key is not present or if a parent attribute is None
        except (KeyError, TypeError, AttributeError):
            # handle special case for Dockerfile deployments
            return '' if container_type == 'cmd' else 'start {}'.format(container_type)

    def log(self, message, level=logging.INFO):
        """Logs a message in the context of this application.

        This prefixes log messages with an application "tag" that the customized deis-logspout will
        be on the lookout for.  When it's seen, the message-- usually an application event of some
        sort like releasing or scaling, will be considered as "belonging" to the application
        instead of the controller and will be handled accordingly.
        """
        logger.log(level, "[{}]: {}".format(self.id, message))

    def create(self, *args, **kwargs):
        """Create a new application with an initial config and release"""
        config = Config.objects.create(owner=self.owner, app=self)
        Release.objects.create(version=1, owner=self.owner, app=self, config=config, build=None)

    def delete(self, *args, **kwargs):
        """Delete this application including all containers"""
        try:
            # attempt to remove containers from the scheduler
            self._destroy_containers([c for c in self.container_set.exclude(type='run')])
        except RuntimeError:
            pass

        self._clean_app_logs()
        return super(App, self).delete(*args, **kwargs)

    def restart(self, **kwargs):
        to_restart = self.container_set.all()
        if kwargs.get('type'):
            to_restart = to_restart.filter(type=kwargs.get('type'))

        if kwargs.get('num'):
            to_restart = to_restart.filter(num=kwargs.get('num'))

        self._restart_containers(to_restart)
        return to_restart

    def _clean_app_logs(self):
        """Delete application logs stored by the logger component"""
        try:
            url = 'http://{}:{}/{}/'.format(settings.LOGGER_HOST, settings.LOGGER_PORT, self.id)
            requests.delete(url)
        except Exception as e:
            # Ignore errors deleting application logs.  An error here should not interfere with
            # the overall success of deleting an application, but we should log it.
            err = 'Error deleting existing application logs: {}'.format(e)
            log_event(self, err, logging.WARNING)

    def scale(self, user, structure):  # noqa
        """Scale containers up or down to match requested structure."""
        if self.release_set.latest().build is None:
            raise EnvironmentError('No build associated with this release')

        requested_structure = structure.copy()
        release = self.release_set.latest()
        # test for available process types
        available_process_types = release.build.procfile or {}
        for container_type in requested_structure:
            if container_type == 'cmd':
                continue  # allow docker cmd types in case we don't have the image source

            if container_type not in available_process_types:
                raise EnvironmentError(
                    'Container type {} does not exist in application'.format(container_type))

        msg = '{} scaled containers '.format(user.username) + ' '.join(
            "{}={}".format(k, v) for k, v in requested_structure.items())
        log_event(self, msg)
        # iterate and scale by container type (web, worker, etc)
        changed = False
        to_add, to_remove = [], []
        scale_types = {}

        # iterate on a copy of the container_type keys
        for container_type in requested_structure.keys():
            containers = list(self.container_set.filter(type=container_type).order_by('created'))
            # increment new container nums off the most recent container
            results = self.container_set.filter(type=container_type).aggregate(Max('num'))
            container_num = (results.get('num__max') or 0) + 1
            requested = requested_structure.pop(container_type)
            diff = requested - len(containers)
            if diff == 0:
                continue

            changed = True
            scale_types[container_type] = requested
            while diff < 0:
                c = containers.pop()
                to_remove.append(c)
                diff += 1

            while diff > 0:
                # create a database record
                c = Container.objects.create(owner=self.owner,
                                             app=self,
                                             release=release,
                                             type=container_type,
                                             num=container_num)
                to_add.append(c)
                container_num += 1
                diff -= 1

        if changed:
            if "scale" in dir(self._scheduler):
                self._scale_containers(scale_types, to_remove)
            else:
                if to_add:
                    self._start_containers(to_add)

                if to_remove:
                    self._destroy_containers(to_remove)

        # save new structure to the database
        vals = self.container_set.exclude(type='run').values(
            'type').annotate(Count('pk')).order_by()
        new_structure = structure.copy()
        new_structure.update({v['type']: v['pk__count'] for v in vals})
        self.structure = new_structure
        self.save()
        return changed

    def _scale_containers(self, scale_types, to_remove):
        release = self.release_set.latest()
        for scale_type in scale_types:
            image = release.image
            version = "v{}".format(release.version)
            kwargs = {
                'memory': release.config.memory,
                'cpu': release.config.cpu,
                'tags': release.config.tags,
                'version': version,
                'aname': self.id,
                'num': scale_types[scale_type]
            }

            job_id = self._get_job_id(scale_type)
            command = self._get_command(scale_type)
            try:
                self._scheduler.scale(
                    name=job_id,
                    image=image,
                    command=command,
                    **kwargs)
            except Exception as e:
                err = '{} (scale): {}'.format(job_id, e)
                log_event(self, err, logging.ERROR)
                raise
        [c.delete() for c in to_remove]

    def _start_containers(self, to_add):
        """Creates and starts containers via the scheduler"""
        if not to_add:
            return

        create_threads = [Thread(target=c.create) for c in to_add]
        start_threads = [Thread(target=c.start) for c in to_add]
        [t.start() for t in create_threads]
        [t.join() for t in create_threads]
        if any(c.state != 'created' for c in to_add):
            err = 'aborting, failed to create some containers'
            log_event(self, err, logging.ERROR)
            self._destroy_containers(to_add)
            raise RuntimeError(err)

        [t.start() for t in start_threads]
        [t.join() for t in start_threads]
        if set([c.state for c in to_add]) != set(['up']):
            err = 'warning, some containers failed to start'
            log_event(self, err, logging.WARNING)

        # if the user specified a health check, try checking to see if it's running
        try:
            config = self.config_set.latest()
            if 'HEALTHCHECK_URL' in config.values.keys():
                self._healthcheck(to_add, config.values)
        except Config.DoesNotExist:
            pass

    def _healthcheck(self, containers, config):
        # if at first it fails, back off and try again at 10%, 50% and 100% of INITIAL_DELAY
        intervals = [1.0, 0.1, 0.5, 1.0]
        # HACK (bacongobbler): we need to wait until publisher has a chance to publish each
        # service to etcd, which can take up to 20 seconds.
        time.sleep(20)
        for i in xrange(len(intervals)):
            delay = int(config.get('HEALTHCHECK_INITIAL_DELAY', 0))
            try:
                # sleep until the initial timeout is over
                if delay > 0:
                    time.sleep(delay * intervals[i])
                to_healthcheck = [c for c in containers if c.type in ['web', 'cmd']]
                self._do_healthcheck(to_healthcheck, config)
                break
            except exceptions.HealthcheckException as e:
                try:
                    next_delay = delay * intervals[i+1]
                    msg = "{}; trying again in {} seconds".format(e, next_delay)
                    log_event(self, msg, logging.WARNING)
                except IndexError:
                    log_event(self, e, logging.WARNING)
        else:
            self._destroy_containers(containers)
            msg = "aborting, app containers failed to respond to health check"
            log_event(self, msg, logging.ERROR)
            raise RuntimeError(msg)

    def _do_healthcheck(self, containers, config):
        path = config.get('HEALTHCHECK_URL', '/')
        timeout = int(config.get('HEALTHCHECK_TIMEOUT', 1))
        if not get_etcd_client():
            raise exceptions.HealthcheckException('no etcd client available')

        for container in containers:
            try:
                key = "/deis/services/{self}/{container.job_id}".format(**locals())
                url = "http://{}{}".format(get_etcd_client().get(key).value, path)
                response = requests.get(url, timeout=timeout)
                if response.status_code != requests.codes.OK:
                    raise exceptions.HealthcheckException(
                        "app failed health check (got '{}', expected: '200')".format(
                            response.status_code))
            except (requests.Timeout, requests.ConnectionError, KeyError) as e:
                raise exceptions.HealthcheckException(
                    'failed to connect to container ({})'.format(e))

    def _restart_containers(self, to_restart):
        """Restarts containers via the scheduler"""
        if not to_restart:
            return

        stop_threads = [Thread(target=c.stop) for c in to_restart]
        start_threads = [Thread(target=c.start) for c in to_restart]
        [t.start() for t in stop_threads]
        [t.join() for t in stop_threads]
        if any(c.state != 'created' for c in to_restart):
            err = 'warning, some containers failed to stop'
            log_event(self, err, logging.WARNING)

        [t.start() for t in start_threads]
        [t.join() for t in start_threads]
        if any(c.state != 'up' for c in to_restart):
            err = 'warning, some containers failed to start'
            log_event(self, err, logging.WARNING)

    def _destroy_containers(self, to_destroy):
        """Destroys containers via the scheduler"""
        if not to_destroy:
            return

        destroy_threads = [Thread(target=c.destroy) for c in to_destroy]
        [t.start() for t in destroy_threads]
        [t.join() for t in destroy_threads]
        [c.delete() for c in to_destroy if c.state == 'destroyed']
        if any(c.state != 'destroyed' for c in to_destroy):
            err = 'aborting, failed to destroy some containers'
            log_event(self, err, logging.ERROR)
            raise RuntimeError(err)

    def deploy(self, user, release):
        """Deploy a new release to this application"""
        existing = self.container_set.exclude(type='run')
        new = []
        scale_types = set()
        for e in existing:
            n = e.clone(release)
            n.save()
            new.append(n)
            scale_types.add(e.type)

        if new and "deploy" in dir(self._scheduler):
            self._deploy_app(scale_types, release, existing)
        else:
            self._start_containers(new)

            # destroy old containers
            if existing:
                self._destroy_containers(existing)

        # perform default scaling if necessary
        if self.structure == {} and release.build is not None:
            self._default_scale(user, release)

    def _deploy_app(self, scale_types, release, existing):
        for scale_type in scale_types:
            image = release.image
            version = "v{}".format(release.version)
            kwargs = {
                'memory': release.config.memory,
                'cpu': release.config.cpu,
                'tags': release.config.tags,
                'aname': self.id,
                'num': 0,
                'version': version
            }
            job_id = self._get_job_id(scale_type)
            command = self._get_command(scale_type)
            try:
                self._scheduler.deploy(
                    name=job_id,
                    image=image,
                    command=command,
                    **kwargs
                )
            except Exception as e:
                err = '{} (deploy): {}'.format(job_id, e)
                log_event(self, err, logging.ERROR)
                raise
        [c.delete() for c in existing]

    def _default_scale(self, user, release):
        """Scale to default structure based on release type"""
        # if there is no SHA, assume a docker image is being promoted
        if not release.build.sha:
            structure = {'cmd': 1}

        # if a dockerfile exists without a procfile, assume docker workflow
        elif release.build.dockerfile and not release.build.procfile:
            structure = {'cmd': 1}

        # if a procfile exists without a web entry, assume docker workflow
        elif release.build.procfile and 'web' not in release.build.procfile:
            structure = {'cmd': 1}

        # default to heroku workflow
        else:
            structure = {'web': 1}

        self.scale(user, structure)

    def logs(self, log_lines=str(settings.LOG_LINES)):
        """Return aggregated log data for this application."""
        try:
            url = "http://{}:{}/{}?log_lines={}".format(settings.LOGGER_HOST,
                                                        settings.LOGGER_PORT,
                                                        self.id,
                                                        log_lines)
            r = requests.get(url)
        # Handle HTTP request errors
        except requests.exceptions.RequestException as e:
            logger.error("Error accessing deis-logger using url '{}': {}".format(url, e))
            raise e

        # Handle logs empty or not found
        if r.status_code == 204 or r.status_code == 404:
            logger.info("GET {} returned a {} status code".format(url, r.status_code))
            raise EnvironmentError('Could not locate logs')

        # Handle unanticipated status codes
        if r.status_code != 200:
            logger.error("Error accessing deis-logger: GET {} returned a {} status code"
                         .format(url, r.status_code))

            raise EnvironmentError('Error accessing deis-logger')

        return r.content

    def run(self, user, command):
        """Run a one-off command in an ephemeral app container."""
        if self.release_set.latest().build is None:
            raise EnvironmentError('No build associated with this release to run this command')
        # TODO: add support for interactive shell
        msg = "{} runs '{}'".format(user.username, command)
        log_event(self, msg)
        c_num = max([c.num for c in self.container_set.filter(type='run')] or [0]) + 1

        # create database record for run process
        c = Container.objects.create(owner=self.owner,
                                     app=self,
                                     release=self.release_set.latest(),
                                     type='run',
                                     num=c_num)

        # SECURITY: shell-escape user input
        escaped_command = command.replace("'", "'\\''")
        return c.run(escaped_command)


# handle etcd add / remove
if get_etcd_client():
    post_save.connect(_etcd_publish_app, sender=App, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_app, sender=App, dispatch_uid='api.models')
