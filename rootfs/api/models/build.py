from __future__ import unicode_literals
import logging

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from json_field.fields import JSONField

from api.models.audit import UuidAuditedModel

logger = logging.getLogger(__name__)


# define update/delete callbacks for synchronizing
# models with the configuration management backend


def _log_build_created(**kwargs):
    if kwargs.get('created'):
        build = kwargs['instance']
        # log only to the controller; this event will be logged in the release summary
        logger.info("{}: build {} created".format(build.app, build))


@python_2_unicode_compatible
class Build(UuidAuditedModel):
    """
    Instance of a software build used by runtime nodes
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    image = models.CharField(max_length=256)

    # optional fields populated by builder
    sha = models.CharField(max_length=40, blank=True)
    procfile = JSONField(default={}, blank=True)
    dockerfile = models.TextField(blank=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
        unique_together = (('app', 'uuid'),)
        db_table = 'build'
        app_label = 'api'

    def create(self, user, *args, **kwargs):
        latest_release = self.app.release_set.latest()
        source_version = 'latest'
        if self.sha:
            source_version = 'git-{}'.format(self.sha)

        new_release = latest_release.new(user,
                                         build=self,
                                         config=latest_release.config,
                                         source_version=source_version)
        try:
            self.app.deploy(user, new_release)
            return new_release
        except RuntimeError:
            new_release.delete()
            raise

    def save(self, **kwargs):
        try:
            previous_build = self.app.build_set.latest()
            to_destroy = []
            for proctype in previous_build.procfile:
                if proctype not in self.procfile:
                    for c in self.app.container_set.filter(type=proctype):
                        to_destroy.append(c)

            self.app._destroy_containers(to_destroy)
        except Build.DoesNotExist:
            pass

        return super(Build, self).save(**kwargs)

    def __str__(self):
        return "{0}-{1}".format(self.app.id, self.uuid[:7])

# Log significant app-related events
post_save.connect(_log_build_created, sender=Build, dispatch_uid='api.models.log')
