"""
Classes to serialize the RESTful representation of Deis API models.
"""

import json
import re

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from api import models

PROCTYPE_MATCH = re.compile(r'^(?P<type>[a-z]+)')
MEMLIMIT_MATCH = re.compile(r'^(?P<mem>[0-9]+(MB|KB|GB|[BKMG]))$', re.IGNORECASE)
CPUSHARE_MATCH = re.compile(r'^(?P<cpu>[0-9]+)$')
TAGKEY_MATCH = re.compile(r'^[a-z]+$')
TAGVAL_MATCH = re.compile(r'^\w+$')
CONFIGKEY_MATCH = re.compile(r'^[a-z_]+[a-z0-9_]*$', re.IGNORECASE)


class JSONFieldSerializer(serializers.JSONField):
    def __init__(self, *args, **kwargs):
        self.type = kwargs.pop('type', 'string')
        super(JSONFieldSerializer, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        """Deserialize the field's JSON data, for write operations."""
        try:
            val = json.loads(data)
        except TypeError:
            val = data
        return val

    def to_representation(self, obj):
        """Serialize the field's JSON data, for read operations."""
        for k, v in obj.items():
            if v is None:  # NoneType is used to unset a value
                continue

            try:
                if self.type == 'int':
                    obj[k] = int(v)
                else:
                    obj[k] = str(v)
            except ValueError:
                obj[k] = v
                # Do nothing, the validator will catch this later

        return obj


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'is_superuser',
                  'is_staff', 'groups', 'user_permissions', 'last_login', 'date_joined',
                  'is_active']
        read_only_fields = ['is_superuser', 'is_staff', 'groups',
                            'user_permissions', 'last_login', 'date_joined', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        now = timezone.now()
        user = User(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            last_login=now,
            date_joined=now,
            is_active=True
        )

        if validated_data.get('first_name'):
            user.first_name = validated_data['first_name']

        if validated_data.get('last_name'):
            user.last_name = validated_data['last_name']

        user.set_password(validated_data['password'])
        # Make the first signup an admin / superuser
        if not User.objects.filter(is_superuser=True).exists():
            user.is_superuser = user.is_staff = True

        user.save()
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    """Serialize admin status for a User model."""

    class Meta:
        model = User
        fields = ['username', 'is_superuser']
        read_only_fields = ['username']


class AppSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.App` model."""

    owner = serializers.ReadOnlyField(source='owner.username')
    structure = serializers.JSONField(required=False)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a :class:`AppSerializer`."""
        model = models.App
        fields = ['uuid', 'id', 'owner', 'structure', 'created', 'updated']
        read_only_fields = ['uuid']


class BuildSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Build` model."""

    app = serializers.SlugRelatedField(slug_field='id', queryset=models.App.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    procfile = serializers.JSONField(required=False)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a :class:`BuildSerializer`."""
        model = models.Build
        fields = ['owner', 'app', 'image', 'sha', 'procfile', 'dockerfile', 'created',
                  'updated', 'uuid']
        read_only_fields = ['uuid']


class ConfigSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Config` model."""

    app = serializers.SlugRelatedField(slug_field='id', queryset=models.App.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    values = JSONFieldSerializer(required=False, binary=True)
    memory = JSONFieldSerializer(required=False, binary=True)
    cpu = JSONFieldSerializer(required=False, binary=True, type='int')
    tags = JSONFieldSerializer(required=False, binary=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a :class:`ConfigSerializer`."""
        model = models.Config

    def validate_values(self, data):
        for key, value in data.items():
            if not re.match(CONFIGKEY_MATCH, key):
                raise serializers.ValidationError(
                    "Config keys must start with a letter or underscore and "
                    "only contain [A-z0-9_]")

        return data

    def validate_memory(self, data):
        for key, value in data.items():
            if value is None:  # use NoneType to unset an item
                continue

            if not re.match(PROCTYPE_MATCH, key):
                raise serializers.ValidationError("Process types can only contain [a-z]")

            if not re.match(MEMLIMIT_MATCH, str(value)):
                raise serializers.ValidationError(
                    "Limit format: <number><unit>, where unit = B, K, M or G")

        return data

    def validate_cpu(self, data):
        for key, value in data.items():
            if value is None:  # use NoneType to unset an item
                continue

            if not re.match(PROCTYPE_MATCH, key):
                raise serializers.ValidationError("Process types can only contain [a-z]")

            shares = re.match(CPUSHARE_MATCH, str(value))
            if not shares:
                raise serializers.ValidationError("CPU shares must be an integer")

            for share in shares.groupdict().values():
                try:
                    i = int(share)
                except ValueError:
                    raise serializers.ValidationError("CPU shares must be an integer")

                if i > 1024 or i < 0:
                    raise serializers.ValidationError("CPU shares must be between 0 and 1024")

        return data

    def validate_tags(self, data):
        for key, value in data.items():
            if value is None:  # use NoneType to unset an item
                continue

            if not re.match(TAGKEY_MATCH, key):
                raise serializers.ValidationError("Tag keys can only contain [a-z]")

            if not re.match(TAGVAL_MATCH, str(value)):
                raise serializers.ValidationError("Invalid tag data")

        return data


class ReleaseSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Release` model."""

    app = serializers.SlugRelatedField(slug_field='id', queryset=models.App.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a :class:`ReleaseSerializer`."""
        model = models.Release


class ContainerSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Container` model."""

    app = serializers.SlugRelatedField(slug_field='id', queryset=models.App.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    release = serializers.SerializerMethodField()

    class Meta:
        """Metadata options for a :class:`ContainerSerializer`."""
        model = models.Container
        fields = ['owner', 'app', 'release', 'type', 'num', 'state', 'created', 'updated', 'uuid']

    def get_release(self, obj):
        return "v{}".format(obj.release.version)


class KeySerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Key` model."""

    owner = serializers.ReadOnlyField(source='owner.username')
    fingerprint = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a KeySerializer."""
        model = models.Key


class DomainSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Domain` model."""

    app = serializers.SlugRelatedField(slug_field='id', queryset=models.App.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a :class:`DomainSerializer`."""
        model = models.Domain
        fields = ['owner', 'created', 'updated', 'app', 'domain']

    def validate_domain(self, value):
        """
        Check that the hostname is valid
        """
        if len(value) > 255:
            raise serializers.ValidationError('Hostname must be 255 characters or less.')

        if value[-1:] == ".":
            value = value[:-1]  # strip exactly one dot from the right, if present

        labels = value.split('.')
        if 'xip.io' in value:
            return value

        if labels[0] == '*':
            raise serializers.ValidationError(
                'Adding a wildcard subdomain is currently not supported.')

        allowed = re.compile("^(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        for label in labels:
            match = allowed.match(label)
            if not match or '--' in label or label.isdigit() or \
               len(labels) == 1 and any(char.isdigit() for char in label):
                raise serializers.ValidationError('Hostname does not look valid.')

        if models.Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError(
                "The domain {} is already in use by another app".format(value))

        return value


class CertificateSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Cert` model."""

    owner = serializers.ReadOnlyField(source='owner.username')
    expires = serializers.DateTimeField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a DomainCertSerializer."""
        model = models.Certificate
        extra_kwargs = {'certificate': {'write_only': True},
                        'key': {'write_only': True},
                        'common_name': {'required': False}}
        read_only_fields = ['expires', 'created', 'updated']


class PushSerializer(serializers.ModelSerializer):
    """Serialize a :class:`~api.models.Push` model."""

    app = serializers.SlugRelatedField(slug_field='id', queryset=models.App.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        """Metadata options for a :class:`PushSerializer`."""
        model = models.Push
        fields = ['uuid', 'owner', 'app', 'sha', 'fingerprint', 'receive_user', 'receive_repo',
                  'ssh_connection', 'ssh_original_command', 'created', 'updated']
