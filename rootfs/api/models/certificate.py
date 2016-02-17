from OpenSSL import crypto
from pyasn1.codec.der import decoder as der_decoder
from pyasn1.type import univ, constraint
from ndg.httpsclient.ssl_peer_verification import SUBJ_ALT_NAME_SUPPORT
from ndg.httpsclient.subj_alt_name import SubjectAltName as BaseSubjectAltName
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.contrib.postgres.fields import ArrayField

from api.models import AuditedModel, validate_label, AlreadyExists
from api.models.domain import Domain


import logging
logger = logging.getLogger(__name__)


# Note: This is a slightly bug-fixed version of same from ndg-httpsclient.
class SubjectAltName(BaseSubjectAltName):
    '''ASN.1 implementation for subjectAltNames support'''

    # There is no limit to how many SAN certificates a certificate may have,
    #   however this needs to have some limit so we'll set an arbitrarily high
    #   limit.
    sizeSpec = univ.SequenceOf.sizeSpec + \
        constraint.ValueSizeConstraint(1, 1024)


# Note: This is a slightly bug-fixed version of same from ndg-httpsclient.
def get_subj_alt_name(peer_cert):
    # Search through extensions
    dns_name = []
    if not SUBJ_ALT_NAME_SUPPORT:
        return dns_name

    general_names = SubjectAltName()
    for i in range(peer_cert.get_extension_count()):
        ext = peer_cert.get_extension(i)
        ext_name = ext.get_short_name()
        if ext_name != b'subjectAltName':
            continue

        # PyOpenSSL returns extension data in ASN.1 encoded form
        ext_dat = ext.get_data()
        decoded_dat = der_decoder.decode(ext_dat,
                                         asn1Spec=general_names)

        for name in decoded_dat:
            if not isinstance(name, SubjectAltName):
                continue
            for entry in range(len(name)):
                component = name.getComponentByPosition(entry)
                if component.getName() != 'dNSName':
                    continue
                dns_name.append(str(component.getComponent()))

    return dns_name


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
    name = models.CharField(max_length=253, unique=True, validators=[validate_label])
    # there is no upper limit on the size of an x.509 certificate
    certificate = models.TextField(validators=[validate_certificate])
    key = models.TextField()
    # X.509 certificates allow any string of information as the common name.
    common_name = models.TextField(editable=False, unique=False)
    # A list of DNS records if certificate has SubjectAltName
    san = ArrayField(models.CharField(max_length=253), null=True)
    # SHA256 fingerprint
    fingerprint = models.CharField(max_length=96, editable=False)
    # Expires and Start time of cert
    expires = models.DateTimeField(editable=False)
    starts = models.DateTimeField(editable=False)
    issuer = models.TextField(editable=False)
    subject = models.TextField(editable=False)

    @property
    def domains(self):
        domains = []
        for data in Domain.objects.filter(certificate=self).distinct().order_by('domain'):
            domains.append(data.domain)

        return domains

    def __str__(self):
        return self.name

    def _get_certificate(self):
        try:
            return crypto.load_certificate(crypto.FILETYPE_PEM, self.certificate)
        except crypto.Error as e:
            raise SuspiciousOperation(e)

    def save(self, *args, **kwargs):
        certificate = self._get_certificate()
        if not self.common_name:
            self.common_name = certificate.get_subject().CN

        # Grab expire date of the certificate
        if not self.expires:
            # https://pyopenssl.readthedocs.org/en/latest/api/crypto.html#OpenSSL.crypto.X509.get_notAfter
            # Convert bytes to string
            timestamp = certificate.get_notAfter().decode(encoding='UTF-8')
            # convert openssl's expiry date format to Django's DateTimeField format
            self.expires = datetime.strptime(timestamp, '%Y%m%d%H%M%SZ')

        # Grab the start date of the certificate
        if not self.starts:
            # https://pyopenssl.readthedocs.org/en/latest/api/crypto.html#OpenSSL.crypto.X509.get_notBefore
            # Convert bytes to string
            timestamp = certificate.get_notBefore().decode(encoding='UTF-8')
            # convert openssl's starts date format to Django's DateTimeField format
            self.starts = datetime.strptime(timestamp, '%Y%m%d%H%M%SZ')

        # process issuers - separate each key/value with a slash
        issuer = certificate.get_issuer().get_components()
        self.issuer = '/' + '/'.join('%s=%s' % (key.decode(encoding='UTF-8'), value.decode(encoding='UTF-8')) for key, value in issuer)  # noqa

        # process subject - separate each key/value with a slash
        subject = certificate.get_subject().get_components()
        self.subject = '/' + '/'.join('%s=%s' % (key.decode(encoding='UTF-8'), value.decode(encoding='UTF-8')) for key, value in subject)  # noqa

        # public fingerprint of certificate
        self.fingerprint = certificate.digest('sha256')

        # SubjectAltName from the certificate - return a list
        self.san = get_subj_alt_name(certificate)

        return super(Certificate, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Remove from k8s and domain object if there are any
        if self.domains:
            for domain in self.domains:
                kwargs['domain'] = domain
                self.detach(*args, **kwargs)
                del kwargs['domain']

        # Delete from DB
        return super(Certificate, self).delete(*args, **kwargs)

    def attach(self, *args, **kwargs):
        data = {
            'cert': self.certificate,
            'key': self.key
        }

        # add the certificate to the domain
        domain = get_object_or_404(Domain, domain=kwargs['domain'])
        if domain.certificate is not None:
            raise AlreadyExists("Domain already has a certificate attached to it")

        domain.certificate = self
        domain.save()

        name = '%s-cert' % self.name
        app = domain.app
        # only create if it exists
        try:
            # We raise an exception when a secret doesn't exist
            self._scheduler._get_secret(app, name)
        except RuntimeError:
            self._scheduler._create_secret(app, name, data)

        # get config for the service
        config = self._load_service_config(app, 'router')

        # See if certificates are available
        if 'certificates' not in config:
            config['certificates'] = ''

        # convert from string to list to work with and filter out empty strings
        cert = '{}:{}'.format(domain.domain, self.name)
        certificates = [_f for _f in config['certificates'].split(',') if _f]
        if cert not in certificates:
            certificates.append(cert)
        config['certificates'] = ','.join(certificates)

        self._save_service_config(app, 'router', config)

    def detach(self, *args, **kwargs):
        # remove the certificate from the domain
        domain = get_object_or_404(Domain, domain=kwargs['domain'])
        domain.certificate = None
        domain.save()

        name = '%s-cert' % self.name
        app = domain.app
        # only delete if it exists
        try:
            # We raise an exception when a secret doesn't exist
            self._scheduler._get_secret(app, name)
            self._scheduler._delete_secret(app, name)
        except RuntimeError as e:
            logger.critical(e)

        # get config for the service
        config = self._load_service_config(app, 'router')

        # See if certificates are available
        if 'certificates' not in config:
            config['certificates'] = ''

        # convert from string to list to work with and filter out empty strings
        cert = '{}:{}'.format(domain.domain, self.name)
        certificates = [_f for _f in config['certificates'].split(',') if _f]
        if cert in certificates:
            certificates.remove(cert)
        config['certificates'] = ','.join(certificates)

        self._save_service_config(app, 'router', config)
