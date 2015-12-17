"""
Deis API custom fields for representing data in Django forms.
"""

from django.db import models


class UuidField(models.UUIDField):
    pass
