# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0003_adding_many_to_many'),
    ]

    operations = [
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('accession', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('experiment_type', models.CharField(max_length=30)),
                ('release_date', models.DateField()),
                ('authors', jsonfield.fields.JSONField()),
                ('chains', jsonfield.fields.JSONField()),
                ('organism', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(default='pdb', max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='proteinentryfeature',
            name='match_end',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='proteinentryfeature',
            name='match_start',
            field=models.IntegerField(null=True),
        ),
    ]
