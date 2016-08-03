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
                ('accession', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=20, unique=True)),
                ('organism', jsonfield.fields.JSONField()),
                ('name', models.CharField(max_length=20)),
                ('short_name', models.CharField(max_length=20, null=True)),
                ('other_names', jsonfield.fields.JSONField()),
                ('description', jsonfield.fields.JSONField()),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('match_start', models.IntegerField()),
                ('match_end', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='entry',
            name='description',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AddField(
            model_name='proteinentryfeature',
            name='entry',
            field=models.ForeignKey(to='webfront.Entry'),
        ),
        migrations.AddField(
            model_name='proteinentryfeature',
            name='protein',
            field=models.ForeignKey(to='webfront.Protein'),
        ),
    ]
