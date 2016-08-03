# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0005_coordinates_as_json'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryStructureFeature',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('chain', models.CharField(max_length=1)),
                ('coordinates', jsonfield.fields.JSONField()),
                ('entry', models.ForeignKey(to='webfront.Entry')),
                ('structure', models.ForeignKey(to='webfront.Structure')),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='structures',
            field=models.ManyToManyField(to='webfront.Structure', through='webfront.EntryStructureFeature'),
        ),
        migrations.AddField(
            model_name='structure',
            name='entries',
            field=models.ManyToManyField(to='webfront.Entry', through='webfront.EntryStructureFeature'),
        ),
    ]
