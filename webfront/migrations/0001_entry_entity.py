# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('entry_id', models.CharField(max_length=10)),
                ('accession', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=10)),
                ('name', models.TextField()),
                ('short_name', models.CharField(max_length=12)),
                ('other_names', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(max_length=20)),
                ('member_databases', jsonfield.fields.JSONField()),
                ('go_terms', jsonfield.fields.JSONField()),
                ('description', models.TextField()),
                ('wikipedia', models.TextField()),
                ('literature', jsonfield.fields.JSONField()),
                ('integrated', models.ForeignKey(to='webfront.Entry', null=True, blank=True)),
            ],
        ),
    ]
