# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-10-04 13:25
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0001_unifying_migrations'),
    ]

    operations = [
        migrations.CreateModel(
            name='Set',
            fields=[
                ('accession', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('description', models.TextField()),
                ('source_database', models.CharField(db_index=True, max_length=20)),
                ('integrated', jsonfield.fields.JSONField()),
                ('relationships', jsonfield.fields.JSONField()),
            ],
        ),
    ]