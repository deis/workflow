"""
Deis API custom fields for representing data in Django forms.
"""

from __future__ import unicode_literals
from django.db import models


class UuidField(models.UUIDField):
    pass
