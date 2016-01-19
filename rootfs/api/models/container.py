import logging

from django.conf import settings
from django.db import models

from api.models import UuidAuditedModel, log_event

logger = logging.getLogger(__name__)


def close_db_connections(func, *args, **kwargs):
    """
    Decorator to explicitly close db connections during threaded execution

    Note this is necessary to work around:
    https://code.djangoproject.com/ticket/22420
    """
    def _close_db_connections(*args, **kwargs):
        ret = None
        try:
            ret = func(*args, **kwargs)
        finally:
            from django.db import connections
            for conn in connections.all():
                conn.close()
        return ret
    return _close_db_connections


class Container(UuidAuditedModel):
    """
    Docker container used to securely host an application process.
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    release = models.ForeignKey('Release')
    type = models.CharField(max_length=128, blank=False)
    num = models.PositiveIntegerField()

    @property
    def state(self):
        return self._scheduler.state(self.job_id).name

    def short_name(self):
        return "{}.{}.{}".format(self.app.id, self.type, self.num)
    short_name.short_description = 'Name'

    def __str__(self):
        return self.short_name()

    class Meta:
        get_latest_by = '-created'
        ordering = ['created']

    @property
    def job_id(self):
        version = "v{}".format(self.release.version)
        return "{self.app.id}_{version}.{self.type}.{self.num}".format(**locals())

    def _get_command(self):
        try:
            # if this is not procfile-based app, ensure they cannot break out
            # and run arbitrary commands on the host
            # FIXME: remove slugrunner's hardcoded entrypoint
            if self.release.build.dockerfile or not self.release.build.sha:
                return "bash -c '{}'".format(self.release.build.procfile[self.type])
            else:
                return 'start {}'.format(self.type)
        # if the key is not present or if a parent attribute is None
        except (KeyError, TypeError, AttributeError):
            # handle special case for Dockerfile deployments
            return '' if self.type == 'cmd' else 'start {}'.format(self.type)

    _command = property(_get_command)

    def clone(self, release):
        c = Container.objects.create(owner=self.owner,
                                     app=self.app,
                                     release=release,
                                     type=self.type,
                                     num=self.num)
        return c

    @close_db_connections
    def create(self):
        image = self.release.image
        kwargs = {'memory': self.release.config.memory,
                  'cpu': self.release.config.cpu,
                  'tags': self.release.config.tags,
                  'envs': self.release.config.values}
        try:
            self._scheduler.create(
                name=self.job_id,
                image=image,
                command=self._command,
                **kwargs
            )
        except Exception as e:
            err = '{} (create): {}'.format(self.job_id, e)
            log_event(self.app, err, logging.ERROR)
            raise

    @close_db_connections
    def start(self):
        try:
            self._scheduler.start(self.job_id)
        except Exception as e:
            err = '{} (start): {}'.format(self.job_id, e)
            log_event(self.app, err, logging.WARNING)
            raise

    @close_db_connections
    def stop(self):
        try:
            self._scheduler.stop(self.job_id)
        except Exception as e:
            err = '{} (stop): {}'.format(self.job_id, e)
            log_event(self.app, err, logging.ERROR)
            raise

    @close_db_connections
    def destroy(self):
        try:
            self._scheduler.destroy(self.job_id)
        except Exception as e:
            err = '{} (destroy): {}'.format(self.job_id, e)
            log_event(self.app, err, logging.ERROR)
            raise

    def run(self, command):
        """Run a one-off command"""
        if self.release.build is None:
            raise EnvironmentError('No build associated with this release '
                                   'to run this command')
        image = self.release.image
        entrypoint = '/bin/bash'
        # if this is a procfile-based app, switch the entrypoint to slugrunner's default
        # FIXME: remove slugrunner's hardcoded entrypoint
        if self.release.build.procfile and \
           self.release.build.sha and not \
           self.release.build.dockerfile:
            entrypoint = '/runner/init'
            command = "'{}'".format(command)
        else:
            command = "-c '{}'".format(command)
        try:
            rc, output = self._scheduler.run(self.job_id, image, entrypoint, command)
            return rc, output
        except Exception as e:
            err = '{} (run): {}'.format(self.job_id, e)
            log_event(self.app, err, logging.ERROR)
            raise
