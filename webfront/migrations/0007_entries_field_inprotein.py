# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0006_entry_structure_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='protein',
            name='entries',
            field=models.ManyToManyField(through='webfront.ProteinEntryFeature', to='webfront.Entry'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='accession',
            field=models.CharField(primary_key=True, max_length=19, serialize=False),
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
