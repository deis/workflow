from __future__ import unicode_literals
import logging

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.conf import settings

# local models
from api.models import get_etcd_client, log_event
from api.models.audit import AuditedModel

logger = logging.getLogger(__name__)

# define update/delete callbacks for synchronizing
# models with the configuration management backend


def _log_domain_added(**kwargs):
    if kwargs.get('created'):
        domain = kwargs['instance']
        msg = "domain {} added".format(domain)
        log_event(domain.app, msg)


def _log_domain_removed(**kwargs):
    domain = kwargs['instance']
    msg = "domain {} removed".format(domain)
    log_event(domain.app, msg)


def _etcd_publish_domains(**kwargs):
    domain = kwargs['instance']
    get_etcd_client().write('/deis/domains/{}'.format(domain), domain.app)


def _etcd_purge_domains(**kwargs):
    domain = kwargs['instance']
    try:
        get_etcd_client().delete('/deis/domains/{}'.format(domain),
                                 prevExist=True, dir=True, recursive=True)
    except KeyError:
        pass


@python_2_unicode_compatible
class Domain(AuditedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    domain = models.TextField(blank=False, null=False, unique=True)

    class Meta:
        db_table = 'domain'
        app_label = 'api'

    def __str__(self):
        return self.domain

# Log significant app-related events and handle in etcd if needed
post_save.connect(_log_domain_added, sender=Domain, dispatch_uid='api.models.log')
post_delete.connect(_log_domain_removed, sender=Domain, dispatch_uid='api.models.log')
if get_etcd_client():
    post_save.connect(_etcd_publish_domains, sender=Domain, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_domains, sender=Domain, dispatch_uid='api.models')
