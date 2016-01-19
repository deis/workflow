from django.conf import settings
from django.db import models
from jsonfield import JSONField

from api.models import UuidAuditedModel


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

    def __str__(self):
        return "{}-{}".format(self.app.id, str(self.uuid)[:7])

    def healthcheck(self):
        # Update healthcheck - Scheduler determines the app type
        path = self.values.get('HEALTHCHECK_URL', '/')
        timeout = int(self.values.get('HEALTHCHECK_TIMEOUT', 1))
        delay = int(self.values.get('HEALTHCHECK_INITIAL_DELAY', 10))
        port = int(self.values.get('HEALTHCHECK_PORT', 8080))

        return {'path': path, 'timeout': timeout, 'delay': delay, 'port': port}

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
                [data.pop(k) for k, v in new_data.items() if v is None]
                setattr(self, attr, data)
        except Config.DoesNotExist:
            pass

        # verify the tags exist on any nodes as labels
        if self.tags:
            # Get all nodes with label selectors
            nodes = self._scheduler._get_nodes(labels=self.tags).json()
            if not nodes['items']:
                labels = ['{}={}'.format(key, value) for key, value in self.tags.items()]
                raise EnvironmentError(
                    'These tags do not match labels on kubernetes nodes: {}'.format(
                        ', '.join(labels)
                    )
                )

        return super(Config, self).save(**kwargs)
