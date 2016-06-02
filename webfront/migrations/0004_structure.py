# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0003_adding_many_to_many'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProteinStructureFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('chain', models.CharField(max_length=1)),
                ('length', models.IntegerField(null=True)),
                ('organism', jsonfield.fields.JSONField()),
                ('start_residue', models.IntegerField(null=True)),
                ('stop_residue', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('accession', models.CharField(primary_key=True, serialize=False, max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('experiment_type', models.CharField(max_length=30)),
                ('release_date', models.DateField()),
                ('authors', jsonfield.fields.JSONField()),
                ('chains', jsonfield.fields.JSONField()),
                ('source_database', models.CharField(default='pdb', max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='protein',
            name='structure',
        ),
        migrations.AlterField(
            model_name='proteinentryfeature',
            name='match_end',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='proteinentryfeature',
            name='match_start',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='structure',
            name='proteins',
            field=models.ManyToManyField(to='webfront.Protein', through='webfront.ProteinStructureFeature'),
        ),
        migrations.AddField(
            model_name='proteinstructurefeature',
            name='protein',
            field=models.ForeignKey(to='webfront.Protein'),
        ),
        migrations.AddField(
            model_name='proteinstructurefeature',
            name='structure',
            field=models.ForeignKey(to='webfront.Structure'),
        ),
        migrations.AddField(
            model_name='protein',
            name='structures',
            field=models.ManyToManyField(to='webfront.Structure', through='webfront.ProteinStructureFeature'),
        ),
    ]
