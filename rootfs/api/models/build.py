from django.conf import settings
from django.db import models
from jsonfield import JSONField

from api.models import UuidAuditedModel


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
            if 'new_release' in locals():
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
        return "{0}-{1}".format(self.app.id, str(self.uuid)[:7])
