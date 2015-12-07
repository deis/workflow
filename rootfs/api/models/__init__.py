# -*- coding: utf-8 -*-

"""
Data models for the Deis API.
"""

from __future__ import unicode_literals
import etcd
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


logger = logging.getLogger(__name__)


def log_event(app, msg, level=logging.INFO):
    # controller needs to know which app this log comes from
    logger.log(level, "{}: {}".format(app.id, msg))
    app.log(msg, level)


def get_etcd_client():
    if not hasattr(get_etcd_client, "client"):
        # wire up etcd publishing if we can connect
        try:
            get_etcd_client.client = etcd.Client(
                host=settings.ETCD_HOST,
                port=int(settings.ETCD_PORT)
            )

            get_etcd_client.client.get('/deis')
        except etcd.EtcdException:
            logger.warn('Cannot synchronize with etcd cluster')
            get_etcd_client.client = None

    return get_etcd_client.client


# define update/delete callbacks for synchronizing
# models with the configuration management backend

def _etcd_purge_user(**kwargs):
    try:
        url = '/deis/builder/users/{}'.format(kwargs['instance'].username)
        get_etcd_client().delete(url, dir=True, recursive=True)
    except KeyError:
        # If _etcd_publish_key() wasn't called, there is no user dir to delete.
        pass


# Log significant app-related events and handle in etcd if needed

# User handling
# automatically generate a new token on creation
@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


if get_etcd_client():
    post_delete.connect(_etcd_purge_user, sender=get_user_model(), dispatch_uid='api.models')

# Load in all models
from app import App  # noqa
from build import Build  # noqa
from certificate import Certificate  # noqa
from config import Config  # noqa
from container import Container  # noqa
from domain import Domain  # noqa
from key import Key  # noqa
from push import Push  # noqa
from release import Release  # noqa
