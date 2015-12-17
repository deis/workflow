# -*- coding: utf-8 -*-

from django.db import migrations, models
import api.models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='id',
            field=models.SlugField(max_length=24, unique=True, null=True, validators=[api.models.validate_id_is_docker_compatible, api.models.validate_reserved_names]),
        ),
        migrations.AlterField(
            model_name='app',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='build',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='container',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='key',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='push',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='uuid',
            field=models.UUIDField(serialize=False, verbose_name='UUID', primary_key=True),
        ),
    ]
