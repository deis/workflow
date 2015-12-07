from __future__ import unicode_literals
import base64

from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.conf import settings

# local models
from api.utils import fingerprint
from api.models import get_etcd_client
from api.models.audit import UuidAuditedModel


def validate_base64(value):
    """Check that value contains only valid base64 characters."""
    try:
        base64.b64decode(value.split()[1])
    except Exception as e:
        raise ValidationError(e)


# define update/delete callbacks for synchronizing
# models with the configuration management backend

def _etcd_publish_key(**kwargs):
    key = kwargs['instance']
    url = '/deis/builder/users/{}/{}'.format(key.owner.username, fingerprint(key.public))
    get_etcd_client().write(url, key.public)


def _etcd_purge_key(**kwargs):
    key = kwargs['instance']
    try:
        url = '/deis/builder/users/{}/{}'.format(key.owner.username, fingerprint(key.public))
        get_etcd_client().delete(url)
    except KeyError:
        pass


@python_2_unicode_compatible
class Key(UuidAuditedModel):
    """An SSH public key."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    id = models.CharField(max_length=128)
    public = models.TextField(unique=True, validators=[validate_base64])
    fingerprint = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'SSH Key'
        unique_together = (('owner', 'fingerprint'))
        db_table = 'key'
        app_label = 'api'

    def __str__(self):
        return "{}...{}".format(self.public[:18], self.public[-31:])

    def save(self, *args, **kwargs):
        self.fingerprint = fingerprint(self.public)
        return super(Key, self).save(*args, **kwargs)

if get_etcd_client():
    post_save.connect(_etcd_publish_key, sender=Key, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_key, sender=Key, dispatch_uid='api.models')
