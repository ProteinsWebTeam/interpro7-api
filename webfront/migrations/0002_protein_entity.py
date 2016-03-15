# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0001_entry_entity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('identifier', models.CharField(primary_key=True, max_length=20, serialize=False, unique=True)),
                ('accession', models.CharField(max_length=20)),
                ('organism', jsonfield.fields.JSONField()),
                ('name', models.CharField(max_length=20)),
                ('short_name', models.CharField(max_length=20, null=True)),
                ('other_names', jsonfield.fields.JSONField()),
                ('description', models.TextField(null=True)),
                ('sequence', models.TextField()),
                ('length', models.IntegerField()),
                ('proteome', models.CharField(max_length=20)),
                ('gene', models.CharField(max_length=20)),
                ('go_terms', jsonfield.fields.JSONField()),
                ('evidence_code', models.IntegerField()),
                ('feature', jsonfield.fields.JSONField()),
                ('structure', jsonfield.fields.JSONField()),
                ('genomic_context', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(max_length=20, default='uniprot')),
            ],
        ),
        migrations.CreateModel(
            name='ProteinEntryFeature',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('match_start', models.IntegerField()),
                ('match_end', models.IntegerField()),
                ('entry', models.ForeignKey(to='webfront.Entry')),
                ('protein', models.ForeignKey(to='webfront.Protein')),
            ],
        ),
    ]
