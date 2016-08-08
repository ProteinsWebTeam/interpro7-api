# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0006_entry_structure_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='accession',
            field=models.CharField(max_length=19, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='short_name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='entry',
            name='type',
            field=models.CharField(max_length=14),
        ),
        migrations.AlterField(
            model_name='structure',
            name='name',
            field=models.CharField(max_length=512),
        ),
    ]
