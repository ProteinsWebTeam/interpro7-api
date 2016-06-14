# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0004_structure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proteinentryfeature',
            name='match_end',
        ),
        migrations.RemoveField(
            model_name='proteinentryfeature',
            name='match_start',
        ),
        migrations.RemoveField(
            model_name='proteinstructurefeature',
            name='start_residue',
        ),
        migrations.RemoveField(
            model_name='proteinstructurefeature',
            name='stop_residue',
        ),
        migrations.AddField(
            model_name='proteinentryfeature',
            name='coordinates',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AddField(
            model_name='proteinstructurefeature',
            name='coordinates',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AddField(
            model_name='structure',
            name='other_names',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AddField(
            model_name='structure',
            name='short_name',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='structure',
            name='name',
            field=models.CharField(max_length=20),
        ),
    ]
