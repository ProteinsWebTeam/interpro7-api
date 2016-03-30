# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0002_protein_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='proteins',
            field=models.ManyToManyField(through='webfront.ProteinEntryFeature', to='webfront.Protein'),
        ),
    ]
