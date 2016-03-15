# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0002_protein_entity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='description',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AlterField(
            model_name='entry',
            name='integrated',
            field=models.ForeignKey(null=True, to='webfront.Entry'),
        ),
    ]
