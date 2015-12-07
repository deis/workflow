from __future__ import unicode_literals
import logging

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings


# local models
from api.utils import dict_diff
from registry import publish_release
from api.models import log_event
from api.models.audit import UuidAuditedModel

logger = logging.getLogger(__name__)

# define update/delete callbacks for synchronizing
# models with the configuration management backend


def _log_release_created(**kwargs):
    if kwargs.get('created'):
        release = kwargs['instance']
        # log only to the controller; this event will be logged in the release summary
        logger.info("{}: release {} created".format(release.app, release))
        # append release lifecycle logs to the app
        release.app.log(release.summary)


@python_2_unicode_compatible
class Release(UuidAuditedModel):
    """
    Software release deployed by the application platform

    Releases contain a :class:`Build` and a :class:`Config`.
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    app = models.ForeignKey('App')
    version = models.PositiveIntegerField()
    summary = models.TextField(blank=True, null=True)

    config = models.ForeignKey('Config')
    build = models.ForeignKey('Build', null=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
        unique_together = (('app', 'version'),)
        db_table = 'release'
        app_label = 'api'

    def __str__(self):
        return "{0}-v{1}".format(self.app.id, self.version)

    @property
    def image(self):
        return '{}:v{}'.format(self.app.id, str(self.version))

    def new(self, user, config, build, summary=None, source_version='latest'):
        """
        Create a new application release using the provided Build and Config
        on behalf of a user.

        Releases start at v1 and auto-increment.
        """
        # construct fully-qualified target image
        new_version = self.version + 1
        # create new release and auto-increment version
        release = Release.objects.create(
            owner=user, app=self.app, config=config,
            build=build, version=new_version, summary=summary
        )

        try:
            release.publish()
        except EnvironmentError as e:
            # If we cannot publish this app, just log and carry on
            log_event(self.app, e)

        return release

    def publish(self, source_version='latest'):
        if self.build is None:
            raise EnvironmentError('No build associated with this release to publish')

        source_image = self.build.image
        if ':' not in source_image:
            source_tag = 'git-{}'.format(self.build.sha) if self.build.sha else source_version
            source_image = "{}:{}".format(source_image, source_tag)

        # If the build has a SHA, assume it's from deis-builder and in the deis-registry already
        deis_registry = bool(self.build.sha)
        publish_release(source_image, self.config.values, self.image, deis_registry)

    def previous(self):
        """
        Return the previous Release to this one.

        :return: the previous :class:`Release`, or None
        """
        releases = self.app.release_set
        if self.pk:
            releases = releases.exclude(pk=self.pk)

        try:
            # Get the Release previous to this one
            prev_release = releases.latest()
        except Release.DoesNotExist:
            prev_release = None

        return prev_release

    def rollback(self, user, version):
        if version < 1:
            raise EnvironmentError('version cannot be below 0')

        summary = "{} rolled back to v{}".format(user, version)
        prev = self.app.release_set.get(version=version)
        new_release = self.new(
            user,
            build=prev.build,
            config=prev.config,
            summary=summary,
            source_version='v{}'.format(version)
        )

        try:
            self.app.deploy(user, new_release)
            return new_release
        except RuntimeError:
            new_release.delete()
            raise

    def save(self, *args, **kwargs):  # noqa
        if not self.summary:
            self.summary = ''
            prev_release = self.previous()
            # compare this build to the previous build
            old_build = prev_release.build if prev_release else None
            old_config = prev_release.config if prev_release else None
            # if the build changed, log it and who pushed it
            if self.version == 1:
                self.summary += "{} created initial release".format(self.app.owner)
            elif self.build != old_build:
                if self.build.sha:
                    self.summary += "{} deployed {}".format(self.build.owner, self.build.sha[:7])
                else:
                    self.summary += "{} deployed {}".format(self.build.owner, self.build.image)

            # if the config data changed, log the dict diff
            if self.config != old_config:
                dict1 = self.config.values
                dict2 = old_config.values if old_config else {}
                diff = dict_diff(dict1, dict2)
                # try to be as succinct as possible
                added = ', '.join(k for k in diff.get('added', {}))
                added = 'added ' + added if added else ''
                changed = ', '.join(k for k in diff.get('changed', {}))
                changed = 'changed ' + changed if changed else ''
                deleted = ', '.join(k for k in diff.get('deleted', {}))
                deleted = 'deleted ' + deleted if deleted else ''
                changes = ', '.join(i for i in (added, changed, deleted) if i)
                if changes:
                    if self.summary:
                        self.summary += ' and '

                    self.summary += "{} {}".format(self.config.owner, changes)

                # if the limits changed (memory or cpu), log the dict diff
                changes = []
                old_mem = old_config.memory if old_config else {}
                diff = dict_diff(self.config.memory, old_mem)
                if diff.get('added') or diff.get('changed') or diff.get('deleted'):
                    changes.append('memory')

                old_cpu = old_config.cpu if old_config else {}
                diff = dict_diff(self.config.cpu, old_cpu)
                if diff.get('added') or diff.get('changed') or diff.get('deleted'):
                    changes.append('cpu')

                if changes:
                    changes = 'changed limits for '+', '.join(changes)
                    self.summary += "{} {}".format(self.config.owner, changes)

                # if the tags changed, log the dict diff
                changes = []
                old_tags = old_config.tags if old_config else {}
                diff = dict_diff(self.config.tags, old_tags)
                # try to be as succinct as possible
                added = ', '.join(k for k in diff.get('added', {}))
                added = 'added tag ' + added if added else ''
                changed = ', '.join(k for k in diff.get('changed', {}))
                changed = 'changed tag ' + changed if changed else ''
                deleted = ', '.join(k for k in diff.get('deleted', {}))
                deleted = 'deleted tag ' + deleted if deleted else ''
                changes = ', '.join(i for i in (added, changed, deleted) if i)
                if changes:
                    if self.summary:
                        self.summary += ' and '

                    self.summary += "{} {}".format(self.config.owner, changes)

            if not self.summary:
                if self.version == 1:
                    self.summary = "{} created the initial release".format(self.owner)
                else:
                    self.summary = "{} changed nothing".format(self.owner)

        super(Release, self).save(*args, **kwargs)


# Release
post_save.connect(_log_release_created, sender=Release, dispatch_uid='api.models.log')
