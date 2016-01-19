import morph

from django.db import models
from django.conf import settings

from api.models import AuditedModel
from api.utils import dict_merge


class Domain(AuditedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    domain = models.TextField(blank=False, null=False, unique=True)

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

    def save(self, *args, **kwargs):
        app = str(self.app)
        domain = str(self.domain)

        # get annotations for the service
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

        # get annotations for the service
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

        # Delete from DB
        return super(Domain, self).delete(*args, **kwargs)

    def __str__(self):
        return self.domain
