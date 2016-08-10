# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0007_auto_20160805_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proteinstructurefeature',
            name='chain',
            field=models.CharField(max_length=4),
        ),
        migrations.AlterUniqueTogether(
            name='entrystructurefeature',
            unique_together=set([('entry', 'structure', 'chain')]),
        ),
        migrations.AlterUniqueTogether(
            name='proteinentryfeature',
            unique_together=set([('protein', 'entry')]),
        ),
        migrations.AlterUniqueTogether(
            name='proteinstructurefeature',
            unique_together=set([('protein', 'structure', 'chain')]),
        ),
    ]
