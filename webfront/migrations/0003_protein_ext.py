# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0002_protein_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='protein',
            name='source_database',
            field=models.CharField(max_length=20, default='uniprot'),
        ),
    ]
