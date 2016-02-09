# -*- coding: utf-8 -*-

"""
Data models for the Deis API.
"""
import etcd
import importlib
import logging
import uuid
import morph
import re

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from api.utils import fingerprint, dict_merge


logger = logging.getLogger(__name__)


class AlreadyExists(EnvironmentError):
    pass


def log_event(app, msg, level=logging.INFO):
    # controller needs to know which app this log comes from
    logger.log(level, "{}: {}".format(app.id, msg))
    app.log(msg, level)


def validate_label(value):
    """
    Check that the value follows the kubernetes name constraints
    http://kubernetes.io/v1.1/docs/design/identifiers.html
    """
    match = re.match(r'^[a-z0-9-]+$', value)
    if not match:
        raise ValidationError("Can only contain a-z (lowercase), 0-9 and hypens")


def get_etcd_client():
    if not hasattr(get_etcd_client, "client"):
        # wire up etcd publishing if we can connect
        try:
            get_etcd_client.client = etcd.Client(
                host=settings.ETCD_HOST,
                port=int(settings.ETCD_PORT))
            get_etcd_client.client.get('/deis')
        except etcd.EtcdException:
            logger.log(logging.WARNING, 'Cannot synchronize with etcd cluster')
            get_etcd_client.client = None
    return get_etcd_client.client


class AuditedModel(models.Model):
    """Add created and updated fields to a model."""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Mark :class:`AuditedModel` as abstract."""
        abstract = True

    @property
    def _scheduler(self):
        mod = importlib.import_module(settings.SCHEDULER_MODULE)
        return mod.SchedulerClient(settings.SCHEDULER_URL)

    def _fetch_service_config(self, app):
        # Get the service from k8s to attach the domain correctly
        svc = self._scheduler._get_service(app, app).json()
        # Get minimum structure going if it is missing on the service
        if 'metadata' not in svc or 'annotations' not in svc['metadata']:
            default = {'metadata': {'annotations': {}}}
            svc = dict_merge(svc, default)

        return svc

    def _load_service_config(self, app, component):
        # fetch setvice definition with minimum structure
        svc = self._fetch_service_config(app)

        # always assume a .deis.io/ ending
        component = "%s.deis.io/" % component

        # Filter to only include values for the component and strip component out of it
        # Processes dots into a nested structure
        config = morph.unflatten(morph.pick(svc['metadata']['annotations'], prefix=component))

        return config

    def _save_service_config(self, app, component, data):
        # fetch setvice definition with minimum structure
        svc = self._fetch_service_config(app)

        # always assume a .deis.io ending
        component = "%s.deis.io/" % component

        # add component to data and flatten
        data = {"%s%s" % (component, key): value for key, value in list(data.items())}
        svc['metadata']['annotations'].update(morph.flatten(data))

        # Update the k8s service for the application with new domain information
        self._scheduler._update_service(app, app, svc)


class UuidAuditedModel(AuditedModel):
    """Add a UUID primary key to an :class:`AuditedModel`."""

    uuid = models.UUIDField('UUID',
                            default=uuid.uuid4,
                            primary_key=True,
                            editable=False,
                            auto_created=True,
                            unique=True)

    class Meta:
        """Mark :class:`UuidAuditedModel` as abstract."""
        abstract = True


from .app import App, validate_id_is_docker_compatible, validate_reserved_names, validate_app_structure  # noqa
from .container import Container  # noqa
from .push import Push  # noqa
from .key import Key, validate_base64  # noqa
from .certificate import Certificate, validate_certificate  # noqa
from .domain import Domain  # noqa
from .release import Release  # noqa
from .config import Config  # noqa
from .build import Build  # noqa

# define update/delete callbacks for synchronizing
# models with the configuration management backend


def _log_build_created(**kwargs):
    if kwargs.get('created'):
        build = kwargs['instance']
        # log only to the controller; this event will be logged in the release summary
        logger.info("{}: build {} created".format(build.app, build))


def _log_release_created(**kwargs):
    if kwargs.get('created'):
        release = kwargs['instance']
        # log only to the controller; this event will be logged in the release summary
        logger.info("{}: release {} created".format(release.app, release))
        # append release lifecycle logs to the app
        release.app.log(release.summary)


def _log_config_updated(**kwargs):
    config = kwargs['instance']
    # log only to the controller; this event will be logged in the release summary
    logger.info("{}: config {} updated".format(config.app, config))


def _log_domain_added(**kwargs):
    if kwargs.get('created'):
        domain = kwargs['instance']
        msg = "domain {} added".format(domain)
        log_event(domain.app, msg)


def _log_domain_removed(**kwargs):
    domain = kwargs['instance']
    msg = "domain {} removed".format(domain)
    log_event(domain.app, msg)


def _log_cert_added(**kwargs):
    if kwargs.get('created'):
        cert = kwargs['instance']
        logger.info("cert {} added".format(cert))


def _log_cert_removed(**kwargs):
    cert = kwargs['instance']
    logger.info("cert {} removed".format(cert))


def _etcd_publish_key(**kwargs):
    key = kwargs['instance']
    _etcd_client.write('/deis/builder/users/{}/{}'.format(
        key.owner.username, fingerprint(key.public)), key.public)


def _etcd_purge_key(**kwargs):
    key = kwargs['instance']
    try:
        _etcd_client.delete('/deis/builder/users/{}/{}'.format(
            key.owner.username, fingerprint(key.public)))
    except KeyError:
        pass


def _etcd_purge_user(**kwargs):
    username = kwargs['instance'].username
    try:
        _etcd_client.delete(
            '/deis/builder/users/{}'.format(username), dir=True, recursive=True)
    except KeyError:
        # If _etcd_publish_key() wasn't called, there is no user dir to delete.
        pass


def _etcd_publish_app(**kwargs):
    appname = kwargs['instance']
    try:
        _etcd_client.write('/deis/services/{}'.format(appname), None, dir=True)
    except KeyError:
        # Ignore error when the directory already exists.
        pass


def _etcd_purge_app(**kwargs):
    appname = kwargs['instance']
    try:
        _etcd_client.delete('/deis/services/{}'.format(appname), dir=True, recursive=True)
    except KeyError:
        pass


# Log significant app-related events
post_save.connect(_log_build_created, sender=Build, dispatch_uid='api.models.log')
post_save.connect(_log_release_created, sender=Release, dispatch_uid='api.models.log')
post_save.connect(_log_config_updated, sender=Config, dispatch_uid='api.models.log')
post_save.connect(_log_domain_added, sender=Domain, dispatch_uid='api.models.log')
post_save.connect(_log_cert_added, sender=Certificate, dispatch_uid='api.models.log')
post_delete.connect(_log_domain_removed, sender=Domain, dispatch_uid='api.models.log')
post_delete.connect(_log_cert_removed, sender=Certificate, dispatch_uid='api.models.log')


# automatically generate a new token on creation
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


_etcd_client = get_etcd_client()


if _etcd_client:
    post_save.connect(_etcd_publish_key, sender=Key, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_key, sender=Key, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_user, sender=settings.AUTH_USER_MODEL, dispatch_uid='api.models')  # noqa
    post_save.connect(_etcd_publish_app, sender=App, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_app, sender=App, dispatch_uid='api.models')
