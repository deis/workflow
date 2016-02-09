from django.db import models
from django.conf import settings

from api.models import AuditedModel


class Domain(AuditedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    domain = models.TextField(blank=False, null=False, unique=True)
    certificate = models.ForeignKey(
        'Certificate',
        models.SET_NULL,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        app = str(self.app)
        domain = str(self.domain)

        # get config for the service
        config = self._load_service_config(app, 'router')

        # See if domains are available
        if 'domains' not in config:
            config['domains'] = ''

        # convert from string to list to work with and filter out empty strings
        domains = [_f for _f in config['domains'].split(',') if _f]
        if domain not in domains:
            domains.append(domain)
        config['domains'] = ','.join(domains)

        self._save_service_config(app, 'router', config)

        # Save to DB
        return super(Domain, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        app = str(self.app)
        domain = str(self.domain)

        # get config for the service
        config = self._load_service_config(app, 'router')

        # See if domains are available
        if 'domains' not in config:
            config['domains'] = ''

        # convert from string to list to work with and filter out empty strings
        domains = [_f for _f in config['domains'].split(',') if _f]
        if domain in domains:
            domains.remove(domain)
        config['domains'] = ','.join(domains)

        self._save_service_config(app, 'router', config)

        # Deatch cert, updates k8s
        if self.certificate:
            self.certificate.deatch(domain=str(self.domain))

        # Delete from DB
        return super(Domain, self).delete(*args, **kwargs)

    def __str__(self):
        return self.domain
