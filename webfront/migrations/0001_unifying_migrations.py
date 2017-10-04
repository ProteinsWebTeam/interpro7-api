# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-10-04 11:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('entry_id', models.CharField(max_length=10, null=True)),
                ('accession', models.CharField(max_length=19, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=14)),
                ('name', models.TextField()),
                ('short_name', models.CharField(max_length=30)),
                ('other_names', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(db_index=True, max_length=20)),
                ('member_databases', jsonfield.fields.JSONField()),
                ('go_terms', jsonfield.fields.JSONField()),
                ('description', jsonfield.fields.JSONField()),
                ('wikipedia', models.TextField(null=True)),
                ('literature', jsonfield.fields.JSONField()),
                ('hierarchy', jsonfield.fields.JSONField(null=True)),
                ('cross_references', jsonfield.fields.JSONField()),
                ('integrated', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webfront.Entry')),
            ],
        ),
        migrations.CreateModel(
            name='EntryAnnotation',
            fields=[
                ('annotation_id', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=20)),
                ('value', models.BinaryField()),
                ('mime_type', models.CharField(max_length=64)),
                ('accession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webfront.Entry')),
            ],
        ),
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
                ('proteomes', jsonfield.fields.JSONField()),
                ('gene', models.CharField(max_length=20)),
                ('go_terms', jsonfield.fields.JSONField()),
                ('evidence_code', models.IntegerField()),
                ('feature', jsonfield.fields.JSONField()),
                ('genomic_context', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(db_index=True, default='uniprot', max_length=20)),
                ('residues', jsonfield.fields.JSONField()),
                ('structure', jsonfield.fields.JSONField(default={})),
                ('fragment', models.CharField(max_length=1)),
                ('tax_id', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Proteome',
            fields=[
                ('accession', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('is_reference', models.BooleanField()),
                ('strain', models.CharField(max_length=512)),
                ('assembly', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('accession', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512)),
                ('short_name', models.CharField(max_length=20, null=True)),
                ('other_names', jsonfield.fields.JSONField()),
                ('experiment_type', models.CharField(max_length=30)),
                ('release_date', models.DateField()),
                ('authors', jsonfield.fields.JSONField()),
                ('chains', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(db_index=True, default='pdb', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('accession', models.IntegerField(primary_key=True, serialize=False)),
                ('scientific_name', models.CharField(max_length=255)),
                ('full_name', models.CharField(max_length=512)),
                ('lineage', models.CharField(max_length=512)),
                ('rank', models.CharField(max_length=20)),
                ('children', jsonfield.fields.JSONField()),
                ('left_number', models.IntegerField()),
                ('right_number', models.IntegerField()),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webfront.Taxonomy')),
            ],
        ),
        migrations.AddField(
            model_name='proteome',
            name='taxonomy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webfront.Taxonomy'),
        ),
    ]