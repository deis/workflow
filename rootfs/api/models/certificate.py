from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError, SuspiciousOperation

from OpenSSL import crypto
from api.models import AuditedModel


def validate_certificate(value):
    try:
        crypto.load_certificate(crypto.FILETYPE_PEM, value)
    except crypto.Error as e:
        raise ValidationError('Could not load certificate: {}'.format(e))


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
    expires = models.DateTimeField(editable=False)

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
            # https://pyopenssl.readthedocs.org/en/latest/api/crypto.html#OpenSSL.crypto.X509.get_notAfter
            # Convert bytes to string
            timestamp = certificate.get_notAfter().decode(encoding='UTF-8')
            # convert openssl's expiry date format to Django's DateTimeField format
            self.expires = datetime.strptime(timestamp, '%Y%m%d%H%M%SZ')

        return super(Certificate, self).save(*args, **kwargs)
