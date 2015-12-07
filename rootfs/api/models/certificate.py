from __future__ import unicode_literals
import logging
from datetime import datetime
from OpenSSL import crypto

from django.core.exceptions import ValidationError, SuspiciousOperation
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.conf import settings

# local models
from api.models import get_etcd_client
from api.models.audit import AuditedModel


logger = logging.getLogger(__name__)


def validate_certificate(value):
    try:
        crypto.load_certificate(crypto.FILETYPE_PEM, value)
    except crypto.Error as e:
        raise ValidationError('Could not load certificate: {}'.format(e))


# define update/delete callbacks for synchronizing
# models with the configuration management backend

def _log_cert_added(**kwargs):
    if kwargs.get('created'):
        cert = kwargs['instance']
        logger.info("cert {} added".format(cert))


def _log_cert_removed(**kwargs):
    cert = kwargs['instance']
    logger.info("cert {} removed".format(cert))


def _etcd_publish_cert(**kwargs):
    cert = kwargs['instance']
    get_etcd_client().write('/deis/certs/{}/cert'.format(cert), cert.certificate)
    get_etcd_client().write('/deis/certs/{}/key'.format(cert), cert.key)


def _etcd_purge_cert(**kwargs):
    cert = kwargs['instance']
    try:
        get_etcd_client().delete('/deis/certs/{}'.format(cert),
                                 prevExist=True, dir=True, recursive=True)
    except KeyError:
        pass


@python_2_unicode_compatible
class Certificate(AuditedModel):
    """
    Public and private key pair used to secure application traffic at the router.
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    # there is no upper limit on the size of an x.509 certificate
    certificate = models.TextField(validators=[validate_certificate])
    key = models.TextField()
    # X.509 certificates allow any string of information as the common name.
    common_name = models.TextField(unique=True)
    expires = models.DateTimeField()

    class Meta:
        db_table = 'certificate'
        app_label = 'api'

    def __str__(self):
        return self.common_name

    def _get_certificate(self):
        try:
            return crypto.load_certificate(crypto.FILETYPE_PEM, self.certificate)
        except crypto.Error as e:
            raise SuspiciousOperation(e)

    def save(self, *args, **kwargs):
        certificate = self._get_certificate()
        if not self.common_name:
            self.common_name = certificate.get_subject().CN

        if not self.expires:
            # convert openssl's expiry date format to Django's DateTimeField format
            self.expires = datetime.strptime(certificate.get_notAfter(), '%Y%m%d%H%M%SZ')

        return super(Certificate, self).save(*args, **kwargs)

# Log significant app-related events and handle in etcd if needed
post_save.connect(_log_cert_added, sender=Certificate, dispatch_uid='api.models.log')
post_delete.connect(_log_cert_removed, sender=Certificate, dispatch_uid='api.models.log')
if get_etcd_client():
    post_save.connect(_etcd_publish_cert, sender=Certificate, dispatch_uid='api.models')
    post_delete.connect(_etcd_purge_cert, sender=Certificate, dispatch_uid='api.models')
