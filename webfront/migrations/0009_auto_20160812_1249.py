# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0008_auto_20160810_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='source_database',
            field=models.CharField(max_length=20, db_index=True),
        ),
        migrations.AlterField(
            model_name='protein',
            name='source_database',
            field=models.CharField(default='uniprot', max_length=20, db_index=True),
        ),
        migrations.AlterField(
            model_name='structure',
            name='source_database',
            field=models.CharField(default='pdb', max_length=20, db_index=True),
        ),
    ]
