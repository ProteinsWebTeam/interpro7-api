# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webfront', '0002_auto_20151001_1431'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabShadow',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ann_id', models.CharField(max_length=7)),
                ('name', models.CharField(max_length=50, blank=True, null=True)),
                ('text', models.CharField(max_length=4000)),
                ('comments', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cab_shadow',
            },
        ),
        migrations.CreateModel(
            name='CathDom',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry', models.CharField(max_length=4)),
                ('pdb_chain', models.CharField(max_length=1)),
                ('cath_id', models.CharField(max_length=8)),
                ('dbeg', models.CharField(max_length=10)),
                ('dend', models.CharField(max_length=10)),
                ('abeg', models.CharField(max_length=10)),
                ('aend', models.CharField(max_length=10)),
                ('rbeg', models.CharField(max_length=10)),
                ('rend', models.CharField(max_length=10)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cath_dom',
            },
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('pub_id', models.CharField(max_length=11, serialize=False, primary_key=True)),
                ('pub_type', models.CharField(max_length=1)),
                ('pubmed_id', models.IntegerField(unique=True, blank=True, null=True)),
                ('isbn', models.CharField(max_length=10, blank=True, null=True)),
                ('volume', models.CharField(max_length=55, blank=True, null=True)),
                ('issue', models.CharField(max_length=55, blank=True, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('title', models.CharField(max_length=740, blank=True, null=True)),
                ('url', models.CharField(max_length=740, blank=True, null=True)),
                ('rawpages', models.CharField(max_length=100, blank=True, null=True)),
                ('medline_journal', models.CharField(max_length=255, blank=True, null=True)),
                ('iso_journal', models.CharField(max_length=255, blank=True, null=True)),
                ('authors', models.CharField(max_length=4000, blank=True, null=True)),
                ('doi_url', models.CharField(max_length=1500, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_citation',
            },
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=4000, blank=True, null=True)),
                ('who', models.CharField(max_length=100)),
                ('when', models.DateField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_comments',
            },
        ),
        migrations.CreateModel(
            name='CommonAnnotation',
            fields=[
                ('ann_id', models.CharField(max_length=7, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50, blank=True, null=True)),
                ('text', models.CharField(max_length=4000, unique=True)),
                ('comments', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_common_annotation',
            },
        ),
        migrations.CreateModel(
            name='CommonAnnotationAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ann_id', models.CharField(max_length=7, blank=True, null=True)),
                ('name', models.CharField(max_length=50, blank=True, null=True)),
                ('text', models.CharField(max_length=4000, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
                ('comments', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_common_annotation_audit',
            },
        ),
        migrations.CreateModel(
            name='CreateJavaLobTable',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=700, unique=True, blank=True, null=True)),
                ('lob', models.BinaryField(blank=True, null=True)),
                ('loadtime', models.DateField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_create$java$lob$table',
            },
        ),
        migrations.CreateModel(
            name='CvDatabase',
            fields=[
                ('dbcode', models.CharField(max_length=1, serialize=False, primary_key=True)),
                ('dbname', models.CharField(max_length=20, unique=True)),
                ('dborder', models.IntegerField(unique=True)),
                ('dbshort', models.CharField(max_length=10, unique=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_database',
            },
        ),
        migrations.CreateModel(
            name='CvEntryType',
            fields=[
                ('code', models.CharField(max_length=1, serialize=False, primary_key=True)),
                ('abbrev', models.CharField(max_length=20, unique=True)),
                ('description', models.CharField(max_length=2000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_entry_type',
            },
        ),
        migrations.CreateModel(
            name='CvEvidence',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('abbrev', models.CharField(max_length=10, unique=True)),
                ('description', models.CharField(max_length=2000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_evidence',
            },
        ),
        migrations.CreateModel(
            name='CvIfc',
            fields=[
                ('code', models.CharField(max_length=4, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=60)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_ifc',
            },
        ),
        migrations.CreateModel(
            name='CvRank',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('rank', models.CharField(max_length=20, blank=True, null=True)),
                ('seq', models.BigIntegerField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_rank',
            },
        ),
        migrations.CreateModel(
            name='CvRelation',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('abbrev', models.CharField(max_length=10, unique=True)),
                ('description', models.CharField(max_length=2000, blank=True, null=True)),
                ('forward', models.CharField(max_length=30)),
                ('reverse', models.CharField(max_length=30)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_relation',
            },
        ),
        migrations.CreateModel(
            name='CvStatus',
            fields=[
                ('code', models.CharField(max_length=1, serialize=False, primary_key=True)),
                ('abbrev', models.CharField(max_length=20)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_status',
            },
        ),
        migrations.CreateModel(
            name='CvSynonym',
            fields=[
                ('code', models.CharField(max_length=4, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=80)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_cv_synonym',
            },
        ),
        migrations.CreateModel(
            name='DatabaseCount',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dbcode', models.CharField(max_length=1)),
                ('what', models.CharField(max_length=40)),
                ('total', models.BigIntegerField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_database_count',
            },
        ),
        migrations.CreateModel(
            name='DbVersionAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('version', models.CharField(max_length=20, blank=True, null=True)),
                ('entry_count', models.IntegerField(blank=True, null=True)),
                ('file_date', models.DateField(blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_db_version_audit',
            },
        ),
        migrations.CreateModel(
            name='Ding',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
                ('abstract', models.CharField(max_length=4000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_ding',
            },
        ),
        migrations.CreateModel(
            name='Domain2Family',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('domain_ac', models.CharField(max_length=9)),
                ('family_ac', models.CharField(max_length=9)),
            ],
            options={
                'db_table': 'INTERPRO_domain2family',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('entry_ac', models.CharField(max_length=9, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, unique=True, blank=True, null=True)),
                ('checked', models.CharField(max_length=1)),
                ('created', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('short_name', models.CharField(max_length=30, unique=True, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry',
            },
        ),
        migrations.CreateModel(
            name='Entry2CommonAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('ann_id', models.CharField(max_length=7, blank=True, null=True)),
                ('order_in', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry2common_audit',
            },
        ),
        migrations.CreateModel(
            name='Entry2CompAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry1_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('entry2_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('relation', models.CharField(max_length=2, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry2comp_audit',
            },
        ),
        migrations.CreateModel(
            name='Entry2EntryAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('parent_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('relation', models.CharField(max_length=2, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry2entry_audit',
            },
        ),
        migrations.CreateModel(
            name='Entry2MethodAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
                ('evidence', models.CharField(max_length=3, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry2method_audit',
            },
        ),
        migrations.CreateModel(
            name='Entry2Pathway',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('dbcode', models.CharField(max_length=1)),
                ('ac', models.CharField(max_length=70)),
                ('name', models.CharField(max_length=250, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry2pathway',
            },
        ),
        migrations.CreateModel(
            name='Entry2PubAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('order_in', models.IntegerField(blank=True, null=True)),
                ('pub_id', models.CharField(max_length=11, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry2pub_audit',
            },
        ),
        migrations.CreateModel(
            name='EntryAccpairAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('secondary_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry_accpair_audit',
            },
        ),
        migrations.CreateModel(
            name='EntryAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('entry_type', models.CharField(max_length=1, blank=True, null=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
                ('short_name', models.CharField(max_length=30, blank=True, null=True)),
                ('checked', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry_audit',
            },
        ),
        migrations.CreateModel(
            name='EntryColour',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('colour_id', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_entry_colour',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EntryDeleted',
            fields=[
                ('entry_ac', models.CharField(max_length=9, serialize=False, primary_key=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry_deleted',
            },
        ),
        migrations.CreateModel(
            name='EntryFriends',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry1_ac', models.CharField(max_length=9)),
                ('entry2_ac', models.CharField(max_length=9)),
                ('s', models.IntegerField()),
                ('p1', models.IntegerField()),
                ('p2', models.IntegerField()),
                ('pb', models.IntegerField()),
                ('a1', models.IntegerField()),
                ('a2', models.IntegerField()),
                ('ab', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_entry_friends',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EntryXrefAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('ac', models.CharField(max_length=70, blank=True, null=True)),
                ('name', models.CharField(max_length=250, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_entry_xref_audit',
            },
        ),
        migrations.CreateModel(
            name='Etaxi',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('tax_id', models.IntegerField()),
                ('parent_id', models.IntegerField(blank=True, null=True)),
                ('scientific_name', models.CharField(max_length=255, blank=True, null=True)),
                ('complete_genome_flag', models.CharField(max_length=1, blank=True, null=True)),
                ('rank', models.CharField(max_length=50)),
                ('hidden', models.FloatField(blank=True, null=True)),
                ('left_number', models.FloatField(blank=True, null=True)),
                ('right_number', models.FloatField(blank=True, null=True)),
                ('annotation_source', models.CharField(max_length=1, blank=True, null=True)),
                ('full_name', models.CharField(max_length=513, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_etaxi',
            },
        ),
        migrations.CreateModel(
            name='ExampleArchive',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('protein_ac', models.CharField(max_length=15)),
                ('order_in', models.IntegerField()),
                ('description', models.CharField(max_length=2000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_example_archive',
            },
        ),
        migrations.CreateModel(
            name='ExampleAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('order_in', models.IntegerField(blank=True, null=True)),
                ('description', models.CharField(max_length=2000, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_example_audit',
            },
        ),
        migrations.CreateModel(
            name='ExampleAuto',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('protein_ac', models.CharField(max_length=15)),
            ],
            options={
                'db_table': 'INTERPRO_example_auto',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='IntactData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('uniprot_id', models.CharField(max_length=30)),
                ('protein_ac', models.CharField(max_length=30)),
                ('undetermined', models.CharField(max_length=1, blank=True, null=True)),
                ('intact_id', models.CharField(max_length=30)),
                ('interacts_with', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=20, blank=True, null=True)),
                ('pubmed_id', models.CharField(max_length=30)),
                ('interacts_with_id', models.CharField(max_length=30, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_intact_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='IntactDataStg',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('uniprot_id', models.CharField(max_length=30)),
                ('protein_ac', models.CharField(max_length=30)),
                ('undetermined', models.CharField(max_length=1, blank=True, null=True)),
                ('intact_id', models.CharField(max_length=30)),
                ('interacts_with', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=20, blank=True, null=True)),
                ('entry_ac', models.CharField(max_length=30)),
                ('pubmed_id', models.CharField(max_length=30, blank=True, null=True)),
                ('interacts_with_id', models.CharField(max_length=30, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_intact_data_stg',
            },
        ),
        migrations.CreateModel(
            name='Interpro2Go',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('go_id', models.CharField(max_length=10)),
                ('source', models.CharField(max_length=4)),
            ],
            options={
                'db_table': 'INTERPRO_interpro2go',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Interpro2GoAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('go_id', models.CharField(max_length=10, blank=True, null=True)),
                ('source', models.CharField(max_length=4, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=3, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_interpro2go_audit',
            },
        ),
        migrations.CreateModel(
            name='Iprscan2Dbcode',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('iprscan_sig_lib_rel_id', models.IntegerField()),
                ('dbcode', models.CharField(max_length=1)),
                ('evidence', models.CharField(max_length=3)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_iprscan2dbcode',
            },
        ),
        migrations.CreateModel(
            name='JavaClassMd5Table',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, unique=True, blank=True, null=True)),
                ('md5', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_java$class$md5$table',
            },
        ),
        migrations.CreateModel(
            name='JavaOptions',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('what', models.CharField(max_length=128, blank=True, null=True)),
                ('opt', models.CharField(max_length=20, blank=True, null=True)),
                ('value', models.CharField(max_length=128, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_java$options',
            },
        ),
        migrations.CreateModel(
            name='LogDetail',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('inserted', models.DateField(blank=True, null=True)),
                ('loglevel', models.NullBooleanField()),
                ('elapsed', models.FloatField(blank=True, null=True)),
                ('cnt', models.FloatField(blank=True, null=True)),
                ('val', models.CharField(max_length=100, blank=True, null=True)),
                ('message', models.CharField(max_length=4000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_log_detail',
            },
        ),
        migrations.CreateModel(
            name='LogError',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('inserted', models.DateField(blank=True, null=True)),
                ('ora_code', models.FloatField(blank=True, null=True)),
                ('ora_msg', models.CharField(max_length=4000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_log_error',
            },
        ),
        migrations.CreateModel(
            name='LogExecution',
            fields=[
                ('log_id', models.FloatField(serialize=False, primary_key=True)),
                ('module', models.CharField(max_length=30, blank=True, null=True)),
                ('proc', models.CharField(max_length=30, blank=True, null=True)),
                ('start_time', models.DateField(blank=True, null=True)),
                ('end_time', models.DateField(blank=True, null=True)),
                ('elapsed', models.FloatField(blank=True, null=True)),
                ('exec_status', models.CharField(max_length=1, blank=True, null=True)),
                ('username', models.CharField(max_length=30, blank=True, null=True)),
                ('os_user', models.CharField(max_length=30, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_log_execution',
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_match',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MatchCountIndexes',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('table_name', models.CharField(max_length=30, blank=True, null=True)),
                ('index_name', models.CharField(max_length=30, blank=True, null=True)),
                ('index_ddl', models.CharField(max_length=4000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_match_count_indexes',
            },
        ),
        migrations.CreateModel(
            name='MatchLoadStatus',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dsname', models.CharField(max_length=30, blank=True, null=True)),
                ('status', models.CharField(max_length=30, blank=True, null=True)),
                ('username', models.CharField(max_length=512, blank=True, null=True)),
                ('tstamp_mn_start', models.DateTimeField(blank=True, null=True)),
                ('tstamp_mn_end', models.DateTimeField(blank=True, null=True)),
                ('tstamp_m_end', models.DateTimeField(blank=True, null=True)),
                ('tstamp_m_start', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_match_load_status',
            },
        ),
        migrations.CreateModel(
            name='MatchNew',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_match_new',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MatchNewStg',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('method_ac', models.CharField(max_length=25)),
                ('pos_from', models.IntegerField(blank=True, null=True)),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=1)),
                ('dbcode', models.CharField(max_length=1)),
                ('evidence', models.CharField(max_length=3, blank=True, null=True)),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_match_new_stg',
            },
        ),
        migrations.CreateModel(
            name='MatchPanther',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('method_ac', models.CharField(max_length=25)),
                ('pos_from', models.IntegerField(blank=True, null=True)),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=1)),
                ('dbcode', models.CharField(max_length=1)),
                ('evidence', models.CharField(max_length=3, blank=True, null=True)),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_match_panther',
            },
        ),
        migrations.CreateModel(
            name='MatchPirsf',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('method_ac', models.CharField(max_length=25)),
                ('pos_from', models.IntegerField(blank=True, null=True)),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=1)),
                ('dbcode', models.CharField(max_length=1)),
                ('evidence', models.CharField(max_length=3, blank=True, null=True)),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_match_pirsf',
            },
        ),
        migrations.CreateModel(
            name='MatchStats',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dbname', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=1)),
                ('count', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_match_stats',
            },
        ),
        migrations.CreateModel(
            name='MatchStruct',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_match_struct',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Merops',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=8)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
                ('name', models.CharField(max_length=120)),
                ('method_ac', models.CharField(max_length=10, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_merops',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MeropsNew',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=8)),
                ('protein_ac', models.CharField(max_length=15)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
                ('name', models.CharField(max_length=120)),
                ('method_ac', models.CharField(max_length=10, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_merops_new',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('method_ac', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('method_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('skip_flag', models.CharField(max_length=1)),
                ('candidate', models.CharField(max_length=1)),
                ('description', models.CharField(max_length=220, blank=True, null=True)),
                ('abstract', models.CharField(max_length=4000, blank=True, null=True)),
                ('abstract_long', models.TextField(blank=True, null=True)),
                ('deleted', models.CharField(max_length=1)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_method',
            },
        ),
        migrations.CreateModel(
            name='Method2Abstract',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('method_ac', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=30)),
                ('entry_type', models.CharField(max_length=1)),
                ('abstract', models.CharField(max_length=4000)),
                ('timestamp', models.DateField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_method2abstract',
            },
        ),
        migrations.CreateModel(
            name='Method2Pub',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'INTERPRO_method2pub',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Method2SwissDe',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=4000, blank=True, null=True)),
                ('method_ac', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=6, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_method2swiss_de',
            },
        ),
        migrations.CreateModel(
            name='MethodAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
                ('name', models.CharField(max_length=30, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('method_date', models.DateField(blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
                ('skip_flag', models.CharField(max_length=1, blank=True, null=True)),
                ('candidate', models.CharField(max_length=1, blank=True, null=True)),
                ('description', models.CharField(max_length=220, blank=True, null=True)),
                ('sig_type', models.CharField(max_length=1, blank=True, null=True)),
                ('abstract', models.CharField(max_length=4000, blank=True, null=True)),
                ('abstract_long', models.TextField(blank=True, null=True)),
                ('deleted', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_method_audit',
            },
        ),
        migrations.CreateModel(
            name='MethodStg',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('description', models.CharField(max_length=220, blank=True, null=True)),
                ('sig_type', models.CharField(max_length=1, blank=True, null=True)),
                ('abstract', models.CharField(max_length=4000, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_method_stg',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MethodsToDeleteTempTable',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_methods_to_delete_temp_table',
            },
        ),
        migrations.CreateModel(
            name='Modbase',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('beg', models.IntegerField(blank=True, null=True)),
                ('end', models.IntegerField(blank=True, null=True)),
                ('crc', models.CharField(max_length=16, blank=True, null=True)),
                ('percent_id', models.DecimalField(max_digits=6, blank=True, decimal_places=2, null=True)),
                ('evalue', models.FloatField(blank=True, null=True)),
                ('score', models.DecimalField(max_digits=4, blank=True, decimal_places=2, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_modbase',
            },
        ),
        migrations.CreateModel(
            name='ModbaseTmp',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('beg', models.IntegerField(blank=True, null=True)),
                ('end', models.IntegerField(blank=True, null=True)),
                ('evalue', models.FloatField(blank=True, null=True)),
                ('r', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_modbase_tmp',
            },
        ),
        migrations.CreateModel(
            name='MvEntry2Protein',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('match_count', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_mv_entry2protein',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MvEntry2ProteinTrue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('match_count', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_mv_entry2protein_true',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MvEntry2UniparcTrue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('uniparc_id', models.CharField(max_length=13)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_entry2uniparc_true',
            },
        ),
        migrations.CreateModel(
            name='MvMethod2Protein',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('match_count', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_mv_method2protein',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MvPdb2Interpro2Go',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('db_id', models.CharField(max_length=32)),
                ('pdb_id', models.CharField(max_length=32)),
                ('chain_id', models.CharField(max_length=32)),
                ('entry_ac', models.CharField(max_length=9)),
                ('method_ac', models.CharField(max_length=75)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
                ('go_id', models.CharField(max_length=30)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
                ('uniprot_ac', models.CharField(max_length=30, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_pdb2interpro2go',
            },
        ),
        migrations.CreateModel(
            name='MvPdb2Interpro2GoBak',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('db_id', models.CharField(max_length=32)),
                ('pdb_id', models.CharField(max_length=32)),
                ('chain_id', models.CharField(max_length=32)),
                ('entry_ac', models.CharField(max_length=9)),
                ('method_ac', models.CharField(max_length=75)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
                ('go_id', models.CharField(max_length=30)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
                ('uniprot_ac', models.CharField(max_length=30, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_pdb2interpro2go_bak',
            },
        ),
        migrations.CreateModel(
            name='MvProteinMethodTax',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('method_ac', models.CharField(max_length=25)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_protein_method_tax',
            },
        ),
        migrations.CreateModel(
            name='MvProteomeCount',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('protein_count', models.IntegerField()),
                ('method_count', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_mv_proteome_count',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MvSecondary',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('secondary_ac', models.CharField(max_length=9)),
                ('method_ac', models.CharField(max_length=25)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_secondary',
            },
        ),
        migrations.CreateModel(
            name='MvTaxEntryCount',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('tax_id', models.IntegerField()),
                ('count', models.FloatField(blank=True, null=True)),
                ('count_specified_tax_id', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_mv_tax_entry_count',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MvUniprot2Interpro2Go',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('entry_ac', models.CharField(max_length=9)),
                ('go_id', models.CharField(max_length=30)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_uniprot2interpro2go',
            },
        ),
        migrations.CreateModel(
            name='Onion2Dbcode',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('onion_type', models.IntegerField()),
                ('dbcode', models.CharField(max_length=1)),
                ('evidence', models.CharField(max_length=3)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_onion2dbcode',
            },
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('oscode', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('italics_name', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=100, blank=True, null=True)),
                ('tax_code', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_organism',
            },
        ),
        migrations.CreateModel(
            name='Pathway2Ec',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('pathway_id', models.CharField(max_length=25)),
                ('ec', models.CharField(max_length=15)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_pathway2ec',
            },
        ),
        migrations.CreateModel(
            name='Pdb2Pub',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('domain_id', models.CharField(max_length=25)),
                ('pub', models.ForeignKey(to='webfront.Citation')),
            ],
            options={
                'db_table': 'INTERPRO_pdb2pub',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PdbPubAdditional',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_pdb_pub_additional',
            },
        ),
        migrations.CreateModel(
            name='PfamClan',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('clan_id', models.CharField(max_length=15, blank=True, null=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_pfam_clan',
            },
        ),
        migrations.CreateModel(
            name='PfamClanData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('clan_id', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=75, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_pfam_clan_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PfamNested',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('pfam1', models.CharField(max_length=25)),
                ('pfam2', models.CharField(max_length=25)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_pfam_nested',
            },
        ),
        migrations.CreateModel(
            name='PrefileMatch',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('method_ac', models.CharField(max_length=25)),
                ('pos_from', models.IntegerField(blank=True, null=True)),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=1)),
                ('dbcode', models.CharField(max_length=1)),
                ('evidence', models.CharField(max_length=3, blank=True, null=True)),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_prefile_match',
            },
        ),
        migrations.CreateModel(
            name='PrefileMethod',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('method_ac', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=30)),
                ('dbcode', models.CharField(max_length=1)),
                ('method_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('skip_flag', models.CharField(max_length=1)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_prefile_method',
            },
        ),
        migrations.CreateModel(
            name='ProfileArchive',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('method_ac', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('short_name', models.CharField(max_length=30, blank=True, null=True)),
                ('abstract', models.CharField(max_length=4000)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_profile_archive',
            },
        ),
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('protein_ac', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=16)),
                ('crc64', models.CharField(max_length=16)),
                ('len', models.IntegerField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('fragment', models.CharField(max_length=1)),
                ('struct_flag', models.CharField(max_length=1)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein',
            },
        ),
        migrations.CreateModel(
            name='Protein2Genome',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('oscode', models.CharField(max_length=5)),
                ('has_string', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'INTERPRO_protein2genome',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ProteinAccpair',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('secondary_ac', models.CharField(max_length=15)),
                ('userstamp', models.CharField(max_length=30)),
                ('timestamp', models.DateField()),
            ],
            options={
                'db_table': 'INTERPRO_protein_accpair',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ProteinAccpairAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('secondary_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('remark', models.CharField(max_length=50, blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_accpair_audit',
            },
        ),
        migrations.CreateModel(
            name='ProteinAccpairNew',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('secondary_ac', models.CharField(max_length=15)),
                ('timestamp', models.DateField()),
            ],
            options={
                'db_table': 'INTERPRO_protein_accpair_new',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ProteinAccpairNewTmp',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('secondary_ac', models.CharField(max_length=15)),
                ('timestamp', models.DateField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_accpair_new_tmp',
            },
        ),
        migrations.CreateModel(
            name='ProteinChanges',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('flag', models.CharField(max_length=1, blank=True, null=True)),
                ('old_rowid', models.TextField(unique=True, blank=True, null=True)),
                ('new_rowid', models.TextField(unique=True, blank=True, null=True)),
                ('old_protein_ac', models.CharField(max_length=15, unique=True, blank=True, null=True)),
                ('new_protein_ac', models.CharField(max_length=15, unique=True, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_changes',
            },
        ),
        migrations.CreateModel(
            name='ProteinChangesTmp',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('flag', models.CharField(max_length=1, blank=True, null=True)),
                ('old_rowid', models.TextField(blank=True, null=True)),
                ('new_rowid', models.TextField(blank=True, null=True)),
                ('old_protein_ac', models.CharField(max_length=6, blank=True, null=True)),
                ('new_protein_ac', models.CharField(max_length=6, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_changes_tmp',
            },
        ),
        migrations.CreateModel(
            name='ProteinIdaOld',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('ida', models.CharField(max_length=1000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_ida_old',
            },
        ),
        migrations.CreateModel(
            name='ProteinNew',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, unique=True)),
                ('name', models.CharField(max_length=16)),
                ('dbcode', models.CharField(max_length=1)),
                ('fragment', models.CharField(max_length=1)),
                ('crc64', models.CharField(max_length=16)),
                ('len', models.IntegerField()),
                ('timestamp', models.DateField()),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_new',
            },
        ),
        migrations.CreateModel(
            name='ProteinNewTmp',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=12)),
                ('dbcode', models.CharField(max_length=1)),
                ('fragment', models.CharField(max_length=1)),
                ('crc64', models.CharField(max_length=16)),
                ('len', models.IntegerField()),
                ('timestamp', models.DateField()),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_new_tmp',
            },
        ),
        migrations.CreateModel(
            name='ProteinTaxonomyHierarchyDm',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('tree_tax_id', models.FloatField(blank=True, null=True)),
                ('rank', models.CharField(max_length=50, blank=True, null=True)),
                ('scientific_name', models.CharField(max_length=255, blank=True, null=True)),
                ('full_name', models.CharField(max_length=306, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein__taxonomy_hierarchy_dm',
            },
        ),
        migrations.CreateModel(
            name='ProteinTmp',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=12)),
                ('dbcode', models.CharField(max_length=1)),
                ('crc64', models.CharField(max_length=16)),
                ('len', models.IntegerField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('fragment', models.CharField(max_length=1)),
                ('struct_flag', models.CharField(max_length=1)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_tmp',
            },
        ),
        migrations.CreateModel(
            name='ProteinToScan',
            fields=[
                ('protein_ac', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('upi', models.CharField(max_length=13, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_to_scan',
            },
        ),
        migrations.CreateModel(
            name='ProteinToScanTmp',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('upi', models.CharField(max_length=13, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_to_scan_tmp',
            },
        ),
        migrations.CreateModel(
            name='ProteomeRank',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('rank', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_proteome_rank',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SanityCheck',
            fields=[
                ('name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('implementation', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=300)),
                ('result', models.CharField(max_length=12, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_sanity_check',
            },
        ),
        migrations.CreateModel(
            name='SanityReport',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('line_num', models.IntegerField()),
                ('report', models.CharField(max_length=120)),
                ('name', models.ForeignKey(to='webfront.SanityCheck', db_column='name')),
            ],
            options={
                'db_table': 'INTERPRO_sanity_report',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SchemaVersionLog',
            fields=[
                ('release', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('upgradetime', models.DateField()),
                ('message', models.CharField(max_length=150)),
                ('status', models.CharField(max_length=10)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_schema_version_log',
            },
        ),
        migrations.CreateModel(
            name='ScopDom',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry', models.CharField(max_length=4)),
                ('pdb_chain', models.CharField(max_length=1)),
                ('scop_id', models.CharField(max_length=8)),
                ('dbeg', models.CharField(max_length=10)),
                ('dend', models.CharField(max_length=10)),
                ('abeg', models.CharField(max_length=10)),
                ('aend', models.CharField(max_length=10)),
                ('rbeg', models.CharField(max_length=10)),
                ('rend', models.CharField(max_length=10)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_scop_dom',
            },
        ),
        migrations.CreateModel(
            name='ShortNameVocab',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_name', models.CharField(max_length=100, blank=True, null=True)),
                ('short_name', models.CharField(max_length=40, unique=True, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_short_name_vocab',
            },
        ),
        migrations.CreateModel(
            name='ShortNameVocabAudit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_name', models.CharField(max_length=100, blank=True, null=True)),
                ('short_name', models.CharField(max_length=40, blank=True, null=True)),
                ('dbuser', models.CharField(max_length=30, blank=True, null=True)),
                ('osuser', models.CharField(max_length=30, blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('action', models.CharField(max_length=12, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_short_name_vocab_audit',
            },
        ),
        migrations.CreateModel(
            name='SproExample',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('tax_name_concat', models.CharField(max_length=80, blank=True, null=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('struct_flag', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_spro_example',
            },
        ),
        migrations.CreateModel(
            name='SptrUnobs',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('accession_code', models.CharField(max_length=4)),
                ('pdb_chain', models.CharField(max_length=1)),
                ('sptr_ac', models.CharField(max_length=6, blank=True, null=True)),
                ('pdb_seq', models.IntegerField(blank=True, null=True)),
                ('serial', models.IntegerField(blank=True, null=True)),
                ('ins_code', models.CharField(max_length=1, blank=True, null=True)),
                ('not_observed', models.CharField(max_length=1, blank=True, null=True)),
                ('sunid', models.IntegerField(blank=True, null=True)),
                ('cath_domain', models.CharField(max_length=8, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_sptr_unobs',
            },
        ),
        migrations.CreateModel(
            name='StructClass',
            fields=[
                ('domain_id', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('fam_id', models.CharField(max_length=20, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_struct_class',
            },
        ),
        migrations.CreateModel(
            name='Supermatch',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_supermatch',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SupermatchNew',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('entry_ac', models.CharField(max_length=9)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_supermatch_new',
            },
        ),
        migrations.CreateModel(
            name='Swissmodel',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('md5', models.CharField(max_length=32, blank=True, null=True)),
                ('beg', models.IntegerField(blank=True, null=True)),
                ('end', models.IntegerField(blank=True, null=True)),
                ('crc64', models.CharField(max_length=16, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_swissmodel',
            },
        ),
        migrations.CreateModel(
            name='TaxExampleGroup',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('tax_name', models.CharField(max_length=80, blank=True, null=True)),
                ('example_group', models.FloatField(blank=True, null=True)),
                ('order_in', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_tax_example_group',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TaxLineage',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ref_tax_id', models.BigIntegerField()),
                ('parent_id', models.BigIntegerField()),
                ('scientific_name', models.CharField(max_length=100)),
                ('order_t', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_tax_lineage',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TaxNameToId',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('tax_name', models.CharField(max_length=30, blank=True, null=True)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
                ('parent', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_tax_name_to_id',
            },
        ),
        migrations.CreateModel(
            name='TaxonomyLoad',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('tax_id', models.IntegerField()),
                ('parent_id', models.IntegerField(blank=True, null=True)),
                ('scientific_name', models.CharField(max_length=255, blank=True, null=True)),
                ('rank', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_taxonomy_load',
            },
        ),
        migrations.CreateModel(
            name='TempTaxHierarchy',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('leaf_tax_id', models.FloatField(blank=True, null=True)),
                ('tree_tax_id', models.FloatField(blank=True, null=True)),
                ('rank', models.CharField(max_length=50, blank=True, null=True)),
                ('scientific_name', models.CharField(max_length=255, blank=True, null=True)),
                ('full_name', models.CharField(max_length=306, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_temp_tax_hierarchy',
            },
        ),
        migrations.CreateModel(
            name='TextIndexEntry',
            fields=[
                ('id', models.CharField(max_length=9, serialize=False, primary_key=True)),
                ('field', models.CharField(max_length=20, blank=True, null=True)),
                ('text', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_text_index_entry',
            },
        ),
        migrations.CreateModel(
            name='TmpDbinnsPhobius',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('upi', models.CharField(max_length=1020)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_tmp_dbinns_phobius',
            },
        ),
        migrations.CreateModel(
            name='TmpIda',
            fields=[
                ('protein_ac', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('ida', models.CharField(max_length=1000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_tmp_ida',
            },
        ),
        migrations.CreateModel(
            name='TmpPfamaBlackBox',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('upi', models.CharField(max_length=13)),
                ('method_ac', models.CharField(max_length=25)),
                ('seq_start', models.IntegerField()),
                ('seq_end', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_tmp_pfama_black_box',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TremblExample',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('tax_name_concat', models.CharField(max_length=80, blank=True, null=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('struct_flag', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_trembl_example',
            },
        ),
        migrations.CreateModel(
            name='UniparcProtein',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('seq_short', models.CharField(max_length=4000, blank=True, null=True)),
                ('seq_long', models.TextField(blank=True, null=True)),
                ('upi', models.CharField(max_length=13)),
                ('md5', models.CharField(max_length=32)),
                ('crc64', models.CharField(max_length=16)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniparc_protein',
            },
        ),
        migrations.CreateModel(
            name='UniparcXref',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ac', models.CharField(max_length=42)),
                ('dbid', models.IntegerField()),
                ('upi', models.CharField(max_length=13)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniparc_xref',
            },
        ),
        migrations.CreateModel(
            name='UniprotClass',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('domain_id', models.CharField(max_length=14)),
                ('fam_id', models.CharField(max_length=20, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniprot_class',
            },
        ),
        migrations.CreateModel(
            name='UniprotOvlap',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('protein_ac', models.CharField(max_length=15)),
                ('dbcode', models.CharField(max_length=1)),
                ('ac', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=20, blank=True, null=True)),
                ('overlap', models.IntegerField(blank=True, null=True)),
                ('p_count', models.IntegerField(blank=True, null=True)),
                ('d_count', models.IntegerField(blank=True, null=True)),
                ('n_d', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniprot_ovlap',
            },
        ),
        migrations.CreateModel(
            name='UniprotPdbe',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_id', models.CharField(max_length=4)),
                ('chain', models.CharField(max_length=4)),
                ('sptr_ac', models.CharField(max_length=15)),
                ('sptr_id', models.CharField(max_length=16)),
                ('beg_seq', models.BigIntegerField(blank=True, null=True)),
                ('end_seq', models.BigIntegerField(blank=True, null=True)),
                ('method', models.CharField(max_length=6, blank=True, null=True)),
                ('resolution', models.DecimalField(max_digits=10, blank=True, decimal_places=2, null=True)),
                ('pubmed_list', models.CharField(max_length=4000, blank=True, null=True)),
                ('crc64', models.CharField(max_length=16)),
                ('flag', models.CharField(max_length=1)),
                ('title', models.CharField(max_length=1024, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniprot_pdbe',
            },
        ),
        migrations.CreateModel(
            name='UniprotSblob',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('entry_type', models.CharField(max_length=1, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('ac', models.CharField(max_length=20, blank=True, null=True)),
                ('overlap', models.IntegerField(blank=True, null=True)),
                ('p_count', models.IntegerField(blank=True, null=True)),
                ('d_count', models.IntegerField(blank=True, null=True)),
                ('n_d', models.IntegerField(blank=True, null=True)),
                ('len', models.IntegerField(blank=True, null=True)),
                ('coverage', models.DecimalField(max_digits=10, blank=True, decimal_places=3, null=True)),
                ('suplen', models.IntegerField(blank=True, null=True)),
                ('n', models.IntegerField(blank=True, null=True)),
                ('sblob', models.DecimalField(max_digits=10, blank=True, decimal_places=3, null=True)),
                ('dom_id', models.CharField(max_length=8, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniprot_sblob',
            },
        ),
        migrations.CreateModel(
            name='UniprotSdom',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_id', models.CharField(max_length=4)),
                ('method', models.CharField(max_length=5, blank=True, null=True)),
                ('resolution', models.DecimalField(max_digits=10, blank=True, decimal_places=2, null=True)),
                ('dom_id', models.CharField(max_length=7)),
                ('fam_id', models.CharField(max_length=20, blank=True, null=True)),
                ('dom_db', models.CharField(max_length=1)),
                ('sptr_ac', models.CharField(max_length=15)),
                ('sptr_id', models.CharField(max_length=16)),
                ('beg_seq', models.IntegerField()),
                ('end_seq', models.IntegerField(blank=True, null=True)),
                ('crc64', models.CharField(max_length=16)),
                ('flag', models.CharField(max_length=1, blank=True, null=True)),
                ('chain', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_uniprot_sdom',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UniprotStruct',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('domain_id', models.CharField(max_length=14)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_uniprot_struct',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UniprotSxref',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('ac', models.CharField(max_length=30, blank=True, null=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniprot_sxref',
            },
        ),
        migrations.CreateModel(
            name='UniprotTaxonomy',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('tax_id', models.BigIntegerField(blank=True, null=True)),
                ('left_number', models.FloatField(blank=True, null=True)),
                ('right_number', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_uniprot_taxonomy',
            },
        ),
        migrations.CreateModel(
            name='UserAccountInfo',
            fields=[
                ('username', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('email', models.CharField(max_length=100, blank=True, null=True)),
                ('team', models.CharField(max_length=100, blank=True, null=True)),
                ('purpose', models.CharField(max_length=4000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_user_account_info',
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('session_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('server_key', models.CharField(max_length=16, blank=True, null=True)),
                ('max_idle', models.IntegerField(blank=True, null=True)),
                ('last_used', models.DateField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_user_session',
            },
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('value', models.CharField(max_length=4000, blank=True, null=True)),
                ('encrypted', models.CharField(max_length=1)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_user_settings',
            },
        ),
        migrations.CreateModel(
            name='VarsplicMaster',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('variant', models.IntegerField(blank=True, null=True)),
                ('crc64', models.CharField(max_length=16, blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_varsplic_master',
            },
        ),
        migrations.CreateModel(
            name='VarsplicMatch',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('pos_from', models.IntegerField(blank=True, null=True)),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=1)),
                ('seq_date', models.DateField()),
                ('match_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_varsplic_match',
            },
        ),
        migrations.CreateModel(
            name='VarsplicNew',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
                ('pos_from', models.FloatField(blank=True, null=True)),
                ('pos_to', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(max_length=1, blank=True, null=True)),
                ('dbcode', models.CharField(max_length=1, blank=True, null=True)),
                ('evidence', models.CharField(max_length=3, blank=True, null=True)),
                ('seq_date', models.DateField(blank=True, null=True)),
                ('match_date', models.DateField(blank=True, null=True)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('userstamp', models.CharField(max_length=30, blank=True, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_varsplic_new',
            },
        ),
        migrations.CreateModel(
            name='VarsplicSupermatch',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('protein_ac', models.CharField(max_length=15)),
                ('entry_ac', models.CharField(max_length=9)),
                ('pos_from', models.IntegerField()),
                ('pos_to', models.IntegerField()),
            ],
            options={
                'db_table': 'INTERPRO_varsplic_supermatch',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ViolatorsEntryXref',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('entry_ac', models.CharField(max_length=9)),
                ('dbcode', models.CharField(max_length=1)),
                ('ac', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=70, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_violators_entry_xref',
            },
        ),
        migrations.CreateModel(
            name='Webstatus',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_webstatus',
            },
        ),
        migrations.CreateModel(
            name='XrefSummary',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dbcode', models.CharField(max_length=8, blank=True, null=True)),
                ('protein_ac', models.CharField(max_length=15, blank=True, null=True)),
                ('entry_ac', models.CharField(max_length=9, blank=True, null=True)),
                ('short_name', models.CharField(max_length=30, blank=True, null=True)),
                ('method_ac', models.CharField(max_length=25, blank=True, null=True)),
                ('method_name', models.CharField(max_length=30, blank=True, null=True)),
                ('pos_from', models.IntegerField(blank=True, null=True)),
                ('pos_to', models.IntegerField(blank=True, null=True)),
                ('match_status', models.CharField(max_length=1, blank=True, null=True)),
                ('match_status_final', models.CharField(max_length=15, blank=True, null=True)),
                ('match_count', models.IntegerField(blank=True, null=True)),
                ('match_date', models.DateField(blank=True, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_xref_summary',
            },
        ),
        migrations.CreateModel(
            name='ZeusJobsLogs',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('collect_date', models.DateField()),
                ('job', models.FloatField()),
                ('log_user', models.CharField(max_length=30)),
                ('priv_user', models.CharField(max_length=30)),
                ('schema_user', models.CharField(max_length=30)),
                ('last_date', models.DateField(blank=True, null=True)),
                ('this_date', models.DateField(blank=True, null=True)),
                ('next_date', models.DateField()),
                ('total_time', models.FloatField(blank=True, null=True)),
                ('broken', models.CharField(max_length=1, blank=True, null=True)),
                ('interval', models.CharField(max_length=200)),
                ('failures', models.FloatField(blank=True, null=True)),
                ('what', models.CharField(max_length=4000, blank=True, null=True)),
                ('nls_env', models.CharField(max_length=4000, blank=True, null=True)),
                ('misc_env', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'INTERPRO_zeus_jobs_logs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ZeusSegmentArchived',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('collect_date', models.DateField()),
                ('obj_field', models.FloatField(db_column='obj#')),
                ('owner', models.CharField(max_length=30)),
                ('object_type', models.CharField(max_length=18)),
                ('object_name', models.CharField(max_length=30)),
                ('statistic_field', models.FloatField(db_column='statistic#', blank=True, null=True)),
                ('statistic_name', models.CharField(max_length=64, blank=True, null=True)),
                ('value', models.FloatField(blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_zeus_segment_archived',
            },
        ),
        migrations.CreateModel(
            name='ZeusSegmentLogs',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('collect_date', models.DateField()),
                ('obj_field', models.FloatField(db_column='obj#')),
                ('owner', models.CharField(max_length=30)),
                ('object_type', models.CharField(max_length=18)),
                ('object_name', models.CharField(max_length=30)),
                ('statistic_field', models.FloatField(db_column='statistic#')),
                ('statistic_name', models.CharField(max_length=64)),
                ('value', models.FloatField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_zeus_segment_logs',
            },
        ),
        migrations.CreateModel(
            name='DbVersion',
            fields=[
                ('dbcode', models.OneToOneField(db_column='dbcode', serialize=False, to='webfront.CvDatabase', primary_key=True)),
                ('version', models.CharField(max_length=20)),
                ('entry_count', models.IntegerField()),
                ('file_date', models.DateField()),
                ('load_date', models.DateField()),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_db_version',
            },
        ),
        migrations.CreateModel(
            name='Entry2Common',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('order_in', models.IntegerField()),
                ('ann', models.ForeignKey(to='webfront.CommonAnnotation')),
            ],
            options={
                'db_table': 'INTERPRO_entry2common',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Entry2Comp',
            fields=[
                ('entry1_ac', models.OneToOneField(db_column='entry1_ac', related_name='Entry1', serialize=False, to='webfront.Entry', primary_key=True)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'INTERPRO_entry2comp',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Entry2Entry',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'INTERPRO_entry2entry',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Entry2Ifc',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('code', models.ForeignKey(to='webfront.CvIfc', db_column='code')),
            ],
            options={
                'db_table': 'INTERPRO_entry2ifc',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Entry2Method',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
                ('ida', models.CharField(max_length=1, blank=True, null=True)),
                ('evidence', models.ForeignKey(to='webfront.CvEvidence', db_column='evidence')),
            ],
            options={
                'db_table': 'INTERPRO_entry2method',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Entry2Pub',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('order_in', models.IntegerField()),
                ('pub', models.ForeignKey(to='webfront.Citation')),
            ],
            options={
                'db_table': 'INTERPRO_entry2pub',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EntryAccpair',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('secondary_ac', models.CharField(max_length=9)),
                ('timestamp', models.DateField()),
                ('userstamp', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'INTERPRO_entry_accpair',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EntryXref',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('ac', models.CharField(max_length=70)),
                ('name', models.CharField(max_length=300, blank=True, null=True)),
                ('dbcode', models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode')),
            ],
            options={
                'db_table': 'INTERPRO_entry_xref',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
            ],
            options={
                'db_table': 'INTERPRO_example',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MvEntryMatch',
            fields=[
                ('entry_ac', models.OneToOneField(db_column='entry_ac', serialize=False, to='webfront.Entry', primary_key=True)),
                ('protein_count', models.IntegerField()),
                ('match_count', models.IntegerField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_entry_match',
            },
        ),
        migrations.CreateModel(
            name='MvMethodMatch',
            fields=[
                ('method_ac', models.OneToOneField(db_column='method_ac', serialize=False, to='webfront.Method', primary_key=True)),
                ('protein_count', models.IntegerField()),
                ('match_count', models.IntegerField()),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_mv_method_match',
            },
        ),
        migrations.CreateModel(
            name='ProteinIda',
            fields=[
                ('protein_ac', models.OneToOneField(db_column='protein_ac', serialize=False, to='webfront.Protein', primary_key=True)),
                ('ida', models.CharField(max_length=2000, blank=True, null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'INTERPRO_protein_ida',
            },
        ),
        migrations.AlterUniqueTogether(
            name='zeusjobslogs',
            unique_together=set([('collect_date', 'job')]),
        ),
        migrations.AlterUniqueTogether(
            name='varsplicsupermatch',
            unique_together=set([('protein_ac', 'entry_ac', 'pos_from', 'pos_to')]),
        ),
        migrations.AddField(
            model_name='varsplicmatch',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AddField(
            model_name='varsplicmatch',
            name='evidence',
            field=models.ForeignKey(db_column='evidence', to='webfront.CvEvidence', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='varsplicmatch',
            name='method_ac',
            field=models.ForeignKey(to='webfront.Method', db_column='method_ac'),
        ),
        migrations.AlterUniqueTogether(
            name='uniprotstruct',
            unique_together=set([('protein_ac', 'domain_id', 'pos_from')]),
        ),
        migrations.AlterUniqueTogether(
            name='uniprotsdom',
            unique_together=set([('sptr_ac', 'entry_id', 'dom_id', 'beg_seq')]),
        ),
        migrations.AlterUniqueTogether(
            name='tmppfamablackbox',
            unique_together=set([('upi', 'method_ac', 'seq_start', 'seq_end')]),
        ),
        migrations.AlterUniqueTogether(
            name='taxlineage',
            unique_together=set([('ref_tax_id', 'parent_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='taxexamplegroup',
            unique_together=set([('example_group', 'order_in'), ('tax_name', 'example_group')]),
        ),
        migrations.AddField(
            model_name='supermatch',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='supermatch',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='proteomerank',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='proteomerank',
            name='oscode',
            field=models.ForeignKey(to='webfront.Organism', db_column='oscode'),
        ),
        migrations.AddField(
            model_name='proteinaccpairnew',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='proteinaccpair',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AlterUniqueTogether(
            name='protein2genome',
            unique_together=set([('oscode', 'protein_ac')]),
        ),
        migrations.AddField(
            model_name='protein',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AlterUniqueTogether(
            name='pfamclandata',
            unique_together=set([('clan_id', 'name')]),
        ),
        migrations.AddField(
            model_name='pdbpubadditional',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='pdbpubadditional',
            name='pub',
            field=models.ForeignKey(to='webfront.Citation'),
        ),
        migrations.AddField(
            model_name='pathway2ec',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AlterUniqueTogether(
            name='mvtaxentrycount',
            unique_together=set([('entry_ac', 'tax_id')]),
        ),
        migrations.AddField(
            model_name='mvproteomecount',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='mvproteomecount',
            name='oscode',
            field=models.ForeignKey(to='webfront.Organism', db_column='oscode'),
        ),
        migrations.AddField(
            model_name='mvmethod2protein',
            name='method_ac',
            field=models.ForeignKey(to='webfront.Method', db_column='method_ac'),
        ),
        migrations.AddField(
            model_name='mvmethod2protein',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='mventry2proteintrue',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='mventry2proteintrue',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='mventry2protein',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='mventry2protein',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AlterUniqueTogether(
            name='methodstg',
            unique_together=set([('method_ac', 'name')]),
        ),
        migrations.AddField(
            model_name='method2pub',
            name='method_ac',
            field=models.ForeignKey(to='webfront.Method', db_column='method_ac'),
        ),
        migrations.AddField(
            model_name='method2pub',
            name='pub',
            field=models.ForeignKey(to='webfront.Citation'),
        ),
        migrations.AddField(
            model_name='method',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AddField(
            model_name='method',
            name='sig_type',
            field=models.ForeignKey(db_column='sig_type', to='webfront.CvEntryType', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='meropsnew',
            unique_together=set([('code', 'protein_ac', 'pos_from', 'pos_to')]),
        ),
        migrations.AddField(
            model_name='merops',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='matchstruct',
            name='domain',
            field=models.ForeignKey(to='webfront.StructClass'),
        ),
        migrations.AddField(
            model_name='matchstats',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AddField(
            model_name='matchnew',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AddField(
            model_name='matchnew',
            name='evidence',
            field=models.ForeignKey(db_column='evidence', to='webfront.CvEvidence', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='matchnew',
            name='method_ac',
            field=models.ForeignKey(to='webfront.Method', db_column='method_ac'),
        ),
        migrations.AddField(
            model_name='matchnew',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='matchnew',
            name='status',
            field=models.ForeignKey(to='webfront.CvStatus', db_column='status'),
        ),
        migrations.AddField(
            model_name='match',
            name='dbcode',
            field=models.ForeignKey(to='webfront.CvDatabase', db_column='dbcode'),
        ),
        migrations.AddField(
            model_name='match',
            name='evidence',
            field=models.ForeignKey(db_column='evidence', to='webfront.CvEvidence', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='match',
            name='method_ac',
            field=models.ForeignKey(to='webfront.Method', db_column='method_ac'),
        ),
        migrations.AddField(
            model_name='match',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AddField(
            model_name='match',
            name='status',
            field=models.ForeignKey(to='webfront.CvStatus', db_column='status'),
        ),
        migrations.AddField(
            model_name='logerror',
            name='log',
            field=models.ForeignKey(to='webfront.LogExecution', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='logdetail',
            name='log',
            field=models.ForeignKey(to='webfront.LogExecution', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='interpro2go',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AddField(
            model_name='intactdata',
            name='entry_ac',
            field=models.ForeignKey(to='webfront.Entry', db_column='entry_ac'),
        ),
        migrations.AlterUniqueTogether(
            name='exampleauto',
            unique_together=set([('entry_ac', 'protein_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entryfriends',
            unique_together=set([('entry1_ac', 'entry2_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entrycolour',
            unique_together=set([('entry_ac', 'colour_id')]),
        ),
        migrations.AddField(
            model_name='entry',
            name='entry_type',
            field=models.ForeignKey(to='webfront.CvEntryType', db_column='entry_type'),
        ),
        migrations.AlterUniqueTogether(
            name='domain2family',
            unique_together=set([('domain_ac', 'family_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='supermatch',
            unique_together=set([('protein_ac', 'entry_ac', 'pos_from', 'pos_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='sanityreport',
            unique_together=set([('name', 'line_num')]),
        ),
        migrations.AlterUniqueTogether(
            name='proteomerank',
            unique_together=set([('entry_ac', 'oscode')]),
        ),
        migrations.AlterUniqueTogether(
            name='proteinaccpairnew',
            unique_together=set([('protein_ac', 'secondary_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='proteinaccpair',
            unique_together=set([('protein_ac', 'secondary_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='pdb2pub',
            unique_together=set([('domain_id', 'pub')]),
        ),
        migrations.AlterUniqueTogether(
            name='mvproteomecount',
            unique_together=set([('entry_ac', 'oscode')]),
        ),
        migrations.AlterUniqueTogether(
            name='mvmethod2protein',
            unique_together=set([('method_ac', 'protein_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='mventry2proteintrue',
            unique_together=set([('entry_ac', 'protein_ac', 'entry_ac', 'protein_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='mventry2protein',
            unique_together=set([('entry_ac', 'protein_ac', 'entry_ac', 'protein_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='method2pub',
            unique_together=set([('method_ac', 'pub')]),
        ),
        migrations.AlterUniqueTogether(
            name='merops',
            unique_together=set([('code', 'protein_ac', 'pos_from', 'pos_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='matchstruct',
            unique_together=set([('protein_ac', 'domain', 'pos_from')]),
        ),
        migrations.AlterUniqueTogether(
            name='matchnew',
            unique_together=set([('protein_ac', 'method_ac', 'pos_from', 'pos_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='match',
            unique_together=set([('protein_ac', 'method_ac', 'pos_from', 'pos_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='interpro2go',
            unique_together=set([('entry_ac', 'go_id', 'source')]),
        ),
        migrations.AlterUniqueTogether(
            name='intactdata',
            unique_together=set([('entry_ac', 'intact_id', 'interacts_with', 'protein_ac', 'pubmed_id')]),
        ),
        migrations.AddField(
            model_name='example',
            name='protein_ac',
            field=models.ForeignKey(to='webfront.Protein', db_column='protein_ac'),
        ),
        migrations.AlterUniqueTogether(
            name='entryaccpair',
            unique_together=set([('entry_ac', 'secondary_ac')]),
        ),
        migrations.AddField(
            model_name='entry2method',
            name='method_ac',
            field=models.OneToOneField(db_column='method_ac', to='webfront.Method'),
        ),
        migrations.AddField(
            model_name='entry2entry',
            name='parent_ac',
            field=models.ForeignKey(db_column='parent_ac', related_name='ParentEntry', to='webfront.Entry'),
        ),
        migrations.AddField(
            model_name='entry2entry',
            name='relation',
            field=models.ForeignKey(to='webfront.CvRelation', db_column='relation'),
        ),
        migrations.AddField(
            model_name='entry2comp',
            name='entry2_ac',
            field=models.ForeignKey(db_column='entry2_ac', related_name='Entry2', to='webfront.Entry'),
        ),
        migrations.AddField(
            model_name='entry2comp',
            name='relation',
            field=models.ForeignKey(to='webfront.CvRelation', db_column='relation'),
        ),
        migrations.AddField(
            model_name='entry',
            name='comps',
            field=models.ManyToManyField(through='webfront.Entry2Comp', to='webfront.Entry', related_name='EntryThroughComp'),
        ),
        migrations.AddField(
            model_name='entry',
            name='entries',
            field=models.ManyToManyField(through='webfront.Entry2Entry', to='webfront.Entry', related_name='EntryThroughEntry'),
        ),
        migrations.AddField(
            model_name='entry',
            name='ifcs',
            field=models.ManyToManyField(through='webfront.Entry2Ifc', to='webfront.CvIfc'),
        ),
        migrations.AlterUniqueTogether(
            name='example',
            unique_together=set([('entry_ac', 'protein_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entryxref',
            unique_together=set([('entry_ac', 'dbcode', 'ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry2pub',
            unique_together=set([('entry_ac', 'pub'), ('entry_ac', 'order_in')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry2method',
            unique_together=set([('entry_ac', 'method_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry2ifc',
            unique_together=set([('entry_ac', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry2entry',
            unique_together=set([('entry_ac', 'parent_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry2comp',
            unique_together=set([('entry1_ac', 'entry2_ac')]),
        ),
        migrations.AlterUniqueTogether(
            name='entry2common',
            unique_together=set([('entry_ac', 'order_in'), ('entry_ac', 'ann', 'order_in'), ('entry_ac', 'ann')]),
        ),
    ]
