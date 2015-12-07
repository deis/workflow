from __future__ import unicode_literals
import logging

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.conf import settings
from json_field.fields import JSONField


# local models
from api.models import get_etcd_client
from api.models.audit import UuidAuditedModel

logger = logging.getLogger(__name__)


# define update/delete callbacks for synchronizing
# models with the configuration management backend


def _log_config_updated(**kwargs):
    config = kwargs['instance']
    # log only to the controller; this event will be logged in the release summary
    logger.info("{}: config {} updated".format(config.app, config))


def _etcd_publish_config(**kwargs):
    config = kwargs['instance']
    # we purge all existing config when adding the newest instance. This is because
    # deis config:unset would remove an existing value, but not delete the
    # old config object
    try:
        get_etcd_client().delete('/deis/config/{}'.format(config.app),
                                 prevExist=True, dir=True, recursive=True)
    except KeyError:
        pass

    for key, value in config.values.iteritems():
        get_etcd_client().write(
            '/deis/config/{}/{}'.format(
                config.app,
                unicode(key).encode('utf-8').lower()
            ), unicode(value).encode('utf-8')
        )


def _etcd_purge_config(**kwargs):
    config = kwargs['instance']
    try:
        get_etcd_client().delete('/deis/config/{}'.format(config.app),
                                 prevExist=True, dir=True, recursive=True)
    except KeyError:
        pass


@python_2_unicode_compatible
class Config(UuidAuditedModel):
    """
    Set of configuration values applied as environment variables
    during runtime execution of the Application.
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    values = JSONField(default={}, blank=True)
    memory = JSONField(default={}, blank=True)
    cpu = JSONField(default={}, blank=True)
    tags = JSONField(default={}, blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
        unique_together = (('app', 'uuid'),)
        db_table = 'config'
        app_label = 'api'

    def __str__(self):
        return "{}-{}".format(self.app.id, self.uuid[:7])

    def save(self, **kwargs):
        """merge the old config with the new"""
        try:
            previous_config = self.app.config_set.latest()
            for attr in ['cpu', 'memory', 'tags', 'values']:
                # Guard against migrations from older apps without fixes to
                # JSONField encoding.
                try:
                    data = getattr(previous_config, attr).copy()
                except AttributeError:
                    data = {}

                try:
                    new_data = getattr(self, attr).copy()
                except AttributeError:
                    new_data = {}

                data.update(new_data)
                # remove config keys if we provided a null value
                [data.pop(k) for k, v in new_data.viewitems() if v is None]
                setattr(self, attr, data)
        except Config.DoesNotExist:
            pass

        return super(Config, self).save(**kwargs)

# Log significant app-related events and handle in etcd if needed
post_save.connect(_log_config_updated, sender=Config, dispatch_uid='api.models.log')
if get_etcd_client():
    post_save.connect(_etcd_publish_config, sender=Config, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_config, sender=Config, dispatch_uid='api.models')
