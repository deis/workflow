# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import api.models
import api.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('id', models.SlugField(max_length=24, unique=True, null=True, validators=[api.models.validate_id_is_docker_compatible, api.models.validate_reserved_names])),
                ('structure', jsonfield.fields.JSONField(default={}, blank=True, validators=[api.models.validate_app_structure])),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('use_app', 'Can use app'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('image', models.CharField(max_length=256)),
                ('sha', models.CharField(max_length=40, blank=True)),
                ('procfile', jsonfield.fields.JSONField(default={}, blank=True)),
                ('dockerfile', models.TextField(blank=True)),
                ('app', models.ForeignKey(to='api.App')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('certificate', models.TextField(validators=[api.models.validate_certificate])),
                ('key', models.TextField()),
                ('common_name', models.TextField(unique=True)),
                ('expires', models.DateTimeField()),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('values', jsonfield.fields.JSONField(default={}, blank=True)),
                ('memory', jsonfield.fields.JSONField(default={}, blank=True)),
                ('cpu', jsonfield.fields.JSONField(default={}, blank=True)),
                ('tags', jsonfield.fields.JSONField(default={}, blank=True)),
                ('app', models.ForeignKey(to='api.App')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=128)),
                ('num', models.PositiveIntegerField()),
                ('app', models.ForeignKey(to='api.App')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
                'get_latest_by': '-created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('domain', models.TextField(unique=True)),
                ('app', models.ForeignKey(to='api.App')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=128)),
                ('public', models.TextField(unique=True, validators=[api.models.validate_base64])),
                ('fingerprint', models.CharField(max_length=128)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SSH Key',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Push',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('sha', models.CharField(max_length=40)),
                ('fingerprint', models.CharField(max_length=255)),
                ('receive_user', models.CharField(max_length=255)),
                ('receive_repo', models.CharField(max_length=255)),
                ('ssh_connection', models.CharField(max_length=255)),
                ('ssh_original_command', models.CharField(max_length=255)),
                ('app', models.ForeignKey(to='api.App')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('uuid', api.fields.UuidField(auto_created=True, primary_key=True, serialize=False, editable=False, max_length=32, unique=True, verbose_name='UUID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('version', models.PositiveIntegerField()),
                ('summary', models.TextField(null=True, blank=True)),
                ('app', models.ForeignKey(to='api.App')),
                ('build', models.ForeignKey(to='api.Build', null=True)),
                ('config', models.ForeignKey(to='api.Config')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('app', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='push',
            unique_together=set([('app', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='key',
            unique_together=set([('owner', 'fingerprint')]),
        ),
        migrations.AddField(
            model_name='container',
            name='release',
            field=models.ForeignKey(to='api.Release'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='config',
            unique_together=set([('app', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='build',
            unique_together=set([('app', 'uuid')]),
        ),
    ]
