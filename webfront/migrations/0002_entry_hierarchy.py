# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-03-28 10:05
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0001_basic_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='hierarchy',
            field=jsonfield.fields.JSONField(null=True),
        ),
    ]