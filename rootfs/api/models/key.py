import base64

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from api.models import UuidAuditedModel
from api.utils import fingerprint


def validate_base64(value):
    """Check that value contains only valid base64 characters."""
    try:
        base64.b64decode(value.split()[1])
    except Exception as e:
        raise ValidationError(e)


class Key(UuidAuditedModel):
    """An SSH public key."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    id = models.CharField(max_length=128)
    public = models.TextField(unique=True, validators=[validate_base64])
    fingerprint = models.CharField(max_length=128, editable=False)

    class Meta:
        verbose_name = 'SSH Key'
        unique_together = (('owner', 'fingerprint'))

    def __str__(self):
        return "{}...{}".format(self.public[:18], self.public[-31:])

    def save(self, *args, **kwargs):
        self.fingerprint = fingerprint(self.public)
        return super(Key, self).save(*args, **kwargs)
