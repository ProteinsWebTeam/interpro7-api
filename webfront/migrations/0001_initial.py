# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveSiteAlignments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('alignment', models.TextField(null=True, blank=True)),
                ('as_residues', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': '_active_site_alignments',
            },
        ),
        migrations.CreateModel(
            name='AlignmentAndTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('alignment', models.TextField(null=True, blank=True)),
                ('tree', models.TextField(null=True, blank=True)),
                ('jtml', models.TextField(null=True, blank=True)),
                ('post', models.TextField(null=True, blank=True)),
                ('type', models.CharField(max_length=12)),
            ],
            options={
                'managed': True,
                'db_table': 'alignment_and_tree',
            },
        ),
        migrations.CreateModel(
            name='Architecture',
            fields=[
                ('auto_architecture', models.BigIntegerField(serialize=False, primary_key=True)),
                ('architecture', models.TextField(null=True, blank=True)),
                ('type_example', models.CharField(max_length=10)),
                ('no_seqs', models.IntegerField()),
                ('architecture_acc', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'architecture',
            },
        ),
        migrations.CreateModel(
            name='Clan',
            fields=[
                ('clan_acc', models.CharField(max_length=6, serialize=False, primary_key=True)),
                ('clan_id', models.CharField(max_length=40, unique=True)),
                ('previous_id', models.CharField(null=True, max_length=75, blank=True)),
                ('clan_description', models.CharField(null=True, max_length=100, blank=True)),
                ('clan_author', models.TextField(null=True, blank=True)),
                ('deposited_by', models.CharField(max_length=100)),
                ('clan_comment', models.TextField(null=True, blank=True)),
                ('updated', models.DateTimeField()),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('version', models.SmallIntegerField(null=True, blank=True)),
                ('number_structures', models.IntegerField(null=True, blank=True)),
                ('number_archs', models.IntegerField(null=True, blank=True)),
                ('number_species', models.IntegerField(null=True, blank=True)),
                ('number_sequences', models.IntegerField(null=True, blank=True)),
                ('competed', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'clan',
            },
        ),
        migrations.CreateModel(
            name='ClanAlignmentAndRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('alignment', models.TextField(null=True, blank=True)),
                ('relationship', models.TextField(null=True, blank=True)),
                ('image_map', models.TextField(null=True, blank=True)),
                ('stockholm', models.TextField(null=True, blank=True)),
                ('clan_acc', models.ForeignKey(to='webfront.Clan', db_column='clan_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'clan_alignment_and_relationship',
            },
        ),
        migrations.CreateModel(
            name='ClanArchitecture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('auto_architecture', models.ForeignKey(to='webfront.Architecture', db_column='auto_architecture')),
                ('clan_acc', models.ForeignKey(to='webfront.Clan', db_column='clan_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'clan_architecture',
            },
        ),
        migrations.CreateModel(
            name='ClanDatabaseLinks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('db_id', models.TextField()),
                ('comment', models.TextField(null=True, blank=True)),
                ('db_link', models.TextField()),
                ('other_params', models.TextField(null=True, blank=True)),
                ('clan_acc', models.ForeignKey(to='webfront.Clan', db_column='clan_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'clan_database_links',
            },
        ),
        migrations.CreateModel(
            name='ClanLitRef',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('order_added', models.IntegerField()),
                ('comment', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'clan_lit_ref',
            },
        ),
        migrations.CreateModel(
            name='ClanMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('clan_acc', models.ForeignKey(to='webfront.Clan', db_column='clan_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'clan_membership',
            },
        ),
        migrations.CreateModel(
            name='ClanWiki',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
                'managed': True,
                'db_table': 'clan_wiki',
            },
        ),
        migrations.CreateModel(
            name='CompleteProteomes',
            fields=[
                ('auto_proteome', models.AutoField(serialize=False, primary_key=True)),
                ('ncbi_taxid', models.IntegerField(unique=True)),
                ('species', models.CharField(null=True, max_length=256, blank=True)),
                ('grouping', models.CharField(null=True, max_length=20, blank=True)),
                ('num_distinct_regions', models.IntegerField()),
                ('num_total_regions', models.IntegerField()),
                ('num_proteins', models.IntegerField()),
                ('sequence_coverage', models.IntegerField()),
                ('residue_coverage', models.IntegerField()),
                ('total_genome_proteins', models.IntegerField()),
                ('total_aa_length', models.BigIntegerField()),
                ('total_aa_covered', models.IntegerField(null=True, blank=True)),
                ('total_seqs_covered', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'complete_proteomes',
            },
        ),
        migrations.CreateModel(
            name='CurrentPfamVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('seed', models.CharField(max_length=32)),
                ('align', models.CharField(max_length=32)),
                ('desc_file', models.CharField(max_length=32)),
                ('hmm', models.CharField(max_length=32)),
            ],
            options={
                'managed': True,
                'db_table': 'current_pfam_version',
            },
        ),
        migrations.CreateModel(
            name='DeadClan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('clan_acc', models.CharField(max_length=7, unique=True)),
                ('clan_id', models.CharField(max_length=40)),
                ('clan_description', models.CharField(null=True, max_length=100, blank=True)),
                ('clan_membership', models.TextField(null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('forward_to', models.CharField(null=True, max_length=6, blank=True)),
                ('user', models.TextField(null=True, blank=True)),
                ('killed', models.DateTimeField()),
            ],
            options={
                'managed': True,
                'db_table': 'dead_clan',
            },
        ),
        migrations.CreateModel(
            name='DeadFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('pfama_acc', models.CharField(max_length=7, db_column='pfamA_acc', unique=True)),
                ('pfama_id', models.CharField(max_length=40, db_column='pfamA_id')),
                ('comment', models.TextField(null=True, blank=True)),
                ('forward_to', models.CharField(null=True, max_length=7, blank=True)),
                ('user', models.CharField(max_length=10)),
                ('killed', models.DateTimeField()),
                ('title', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'dead_family',
            },
        ),
        migrations.CreateModel(
            name='Edits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('seq_version', models.IntegerField(null=True, blank=True)),
                ('original_start', models.IntegerField()),
                ('original_end', models.IntegerField()),
                ('new_start', models.IntegerField(null=True, blank=True)),
                ('new_end', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'edits',
            },
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('evidence', models.IntegerField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'managed': True,
                'db_table': 'evidence',
            },
        ),
        migrations.CreateModel(
            name='GeneOntology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('go_id', models.TextField()),
                ('term', models.TextField()),
                ('category', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'gene_ontology',
            },
        ),
        migrations.CreateModel(
            name='Interpro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('interpro_id', models.TextField()),
                ('abstract', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'interpro',
            },
        ),
        migrations.CreateModel(
            name='Ligand',
            fields=[
                ('ligand_id', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('formula', models.TextField()),
                ('molecular_weight', models.FloatField()),
                ('smiles', models.TextField()),
                ('inchi', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'ligand',
            },
        ),
        migrations.CreateModel(
            name='LiteratureReference',
            fields=[
                ('auto_lit', models.AutoField(serialize=False, primary_key=True)),
                ('pmid', models.IntegerField(null=True, blank=True, unique=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('author', models.TextField(null=True, blank=True)),
                ('journal', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'literature_reference',
            },
        ),
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('locked', models.IntegerField()),
                ('locker', models.CharField(max_length=10)),
                ('allowcommits', models.IntegerField(db_column='allowCommits')),
                ('alsoallow', models.TextField(db_column='alsoAllow')),
            ],
            options={
                'managed': True,
                'db_table': '_lock',
            },
        ),
        migrations.CreateModel(
            name='MarkupKey',
            fields=[
                ('auto_markup', models.IntegerField(serialize=False, primary_key=True)),
                ('label', models.CharField(null=True, max_length=50, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'markup_key',
            },
        ),
        migrations.CreateModel(
            name='NcbiTaxonomy',
            fields=[
                ('ncbi_taxid', models.IntegerField(serialize=False, primary_key=True)),
                ('species', models.CharField(max_length=100)),
                ('taxonomy', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'ncbi_taxonomy',
            },
        ),
        migrations.CreateModel(
            name='NestedDomains',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
                'managed': True,
                'db_table': 'nested_domains',
            },
        ),
        migrations.CreateModel(
            name='NestedLocations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('seq_version', models.IntegerField(null=True, blank=True)),
                ('seq_start', models.IntegerField(null=True, blank=True)),
                ('seq_end', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'nested_locations',
            },
        ),
        migrations.CreateModel(
            name='OtherReg',
            fields=[
                ('region_id', models.AutoField(serialize=False, primary_key=True)),
                ('seq_start', models.IntegerField()),
                ('seq_end', models.IntegerField()),
                ('type_id', models.CharField(max_length=20)),
                ('source_id', models.CharField(max_length=20)),
                ('score', models.FloatField(null=True, blank=True)),
                ('orientation', models.CharField(null=True, max_length=4, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'other_reg',
            },
        ),
        migrations.CreateModel(
            name='Pdb',
            fields=[
                ('pdb_id', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('keywords', models.TextField(null=True, blank=True)),
                ('title', models.TextField(null=True, blank=True)),
                ('date', models.TextField(null=True, blank=True)),
                ('resolution', models.DecimalField(null=True, max_digits=5, blank=True, decimal_places=2)),
                ('method', models.TextField(null=True, blank=True)),
                ('author', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'pdb',
            },
        ),
        migrations.CreateModel(
            name='PdbImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('pdb_image', models.TextField(null=True, blank=True)),
                ('pdb_image_sml', models.TextField(null=True, blank=True)),
                ('pdb', models.ForeignKey(to='webfront.Pdb')),
            ],
            options={
                'managed': True,
                'db_table': 'pdb_image',
            },
        ),
        migrations.CreateModel(
            name='PdbPfamaReg',
            fields=[
                ('auto_pdb_reg', models.AutoField(serialize=False, primary_key=True)),
                ('pfama_acc', models.CharField(max_length=7, db_column='pfamA_acc')),
                ('pfamseq_acc', models.CharField(max_length=10)),
                ('chain', models.CharField(null=True, max_length=4, blank=True)),
                ('pdb_res_start', models.IntegerField(null=True, blank=True)),
                ('pdb_start_icode', models.CharField(null=True, max_length=1, blank=True)),
                ('pdb_res_end', models.IntegerField(null=True, blank=True)),
                ('pdb_end_icode', models.CharField(null=True, max_length=1, blank=True)),
                ('seq_start', models.IntegerField()),
                ('seq_end', models.IntegerField()),
                ('hex_colour', models.CharField(null=True, max_length=6, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'pdb_pfamA_reg',
            },
        ),
        migrations.CreateModel(
            name='PdbResidueData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('chain', models.CharField(null=True, max_length=4, blank=True)),
                ('serial', models.IntegerField(null=True, blank=True)),
                ('pdb_res', models.CharField(null=True, max_length=3, blank=True)),
                ('pdb_seq_number', models.IntegerField(null=True, blank=True)),
                ('pdb_insert_code', models.CharField(null=True, max_length=1, blank=True)),
                ('observed', models.IntegerField(null=True, blank=True)),
                ('dssp_code', models.CharField(null=True, max_length=4, blank=True)),
                ('pfamseq_res', models.CharField(null=True, max_length=3, blank=True)),
                ('pfamseq_seq_number', models.IntegerField(null=True, blank=True)),
                ('pdb', models.ForeignKey(to='webfront.Pdb')),
            ],
            options={
                'managed': True,
                'db_table': 'pdb_residue_data',
            },
        ),
        migrations.CreateModel(
            name='Pfama',
            fields=[
                ('pfama_acc', models.CharField(max_length=7, db_column='pfamA_acc', serialize=False, primary_key=True)),
                ('pfama_id', models.CharField(max_length=16, db_column='pfamA_id', unique=True)),
                ('previous_id', models.TextField(null=True, blank=True)),
                ('description', models.CharField(max_length=100)),
                ('author', models.TextField(null=True, blank=True)),
                ('deposited_by', models.CharField(max_length=100)),
                ('seed_source', models.TextField(null=True, blank=True)),
                ('type', models.CharField(max_length=11)),
                ('comment', models.TextField(null=True, blank=True)),
                ('sequence_ga', models.FloatField(db_column='sequence_GA', null=True, blank=True)),
                ('domain_ga', models.FloatField(db_column='domain_GA', null=True, blank=True)),
                ('sequence_tc', models.FloatField(db_column='sequence_TC', null=True, blank=True)),
                ('domain_tc', models.FloatField(db_column='domain_TC', null=True, blank=True)),
                ('sequence_nc', models.FloatField(db_column='sequence_NC', null=True, blank=True)),
                ('domain_nc', models.FloatField(db_column='domain_NC', null=True, blank=True)),
                ('buildmethod', models.TextField(db_column='buildMethod', null=True, blank=True)),
                ('model_length', models.IntegerField(null=True, blank=True)),
                ('searchmethod', models.TextField(db_column='searchMethod', null=True, blank=True)),
                ('msv_lambda', models.FloatField(null=True, blank=True)),
                ('msv_mu', models.FloatField(null=True, blank=True)),
                ('viterbi_lambda', models.FloatField(null=True, blank=True)),
                ('viterbi_mu', models.FloatField(null=True, blank=True)),
                ('forward_lambda', models.FloatField(null=True, blank=True)),
                ('forward_tau', models.FloatField(null=True, blank=True)),
                ('num_seed', models.IntegerField(null=True, blank=True)),
                ('num_full', models.IntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('version', models.SmallIntegerField(null=True, blank=True)),
                ('number_archs', models.IntegerField(null=True, blank=True)),
                ('number_species', models.IntegerField(null=True, blank=True)),
                ('number_structures', models.IntegerField(null=True, blank=True)),
                ('number_ncbi', models.IntegerField(null=True, blank=True)),
                ('number_meta', models.IntegerField(null=True, blank=True)),
                ('average_length', models.FloatField(null=True, blank=True)),
                ('percentage_id', models.IntegerField(null=True, blank=True)),
                ('average_coverage', models.FloatField(null=True, blank=True)),
                ('change_status', models.TextField(null=True, blank=True)),
                ('seed_consensus', models.TextField(null=True, blank=True)),
                ('full_consensus', models.TextField(null=True, blank=True)),
                ('number_shuffled_hits', models.IntegerField(null=True, blank=True)),
                ('number_rp15', models.IntegerField(null=True, blank=True)),
                ('number_rp35', models.IntegerField(null=True, blank=True)),
                ('number_rp55', models.IntegerField(null=True, blank=True)),
                ('number_rp75', models.IntegerField(null=True, blank=True)),
                ('number_ref_proteome', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA',
            },
        ),
        migrations.CreateModel(
            name='Pfama2PfamaHhsearch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('evalue', models.CharField(max_length=25)),
                ('pfama_acc_1', models.ForeignKey(related_name='relationship_source', to='webfront.Pfama', db_column='pfamA_acc_1')),
                ('pfama_acc_2', models.ForeignKey(related_name='relationship_target', to='webfront.Pfama', db_column='pfamA_acc_2')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA2pfamA_hhsearch',
            },
        ),
        migrations.CreateModel(
            name='Pfama2PfamaScoop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('score', models.FloatField()),
                ('pfama_acc_1', models.ForeignKey(related_name='scoop_source', to='webfront.Pfama', db_column='pfamA_acc_1')),
                ('pfama_acc_2', models.ForeignKey(related_name='scoop_target', to='webfront.Pfama', db_column='pfamA_acc_2')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA2pfamA_scoop',
            },
        ),
        migrations.CreateModel(
            name='PfamaArchitecture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('auto_architecture', models.ForeignKey(to='webfront.Architecture', db_column='auto_architecture')),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_architecture',
            },
        ),
        migrations.CreateModel(
            name='PfamaDatabaseLinks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('db_id', models.TextField()),
                ('comment', models.TextField(null=True, blank=True)),
                ('db_link', models.TextField()),
                ('other_params', models.TextField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_database_links',
            },
        ),
        migrations.CreateModel(
            name='PfamaFasta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('fasta', models.TextField(null=True, blank=True)),
                ('nr_threshold', models.IntegerField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_fasta',
            },
        ),
        migrations.CreateModel(
            name='PfamaHmm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('hmm', models.TextField(null=True, blank=True)),
                ('logo', models.TextField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_HMM',
            },
        ),
        migrations.CreateModel(
            name='PfamaInteractions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('pfama_acc_a', models.ForeignKey(related_name='interactor_source', to='webfront.Pfama', db_column='pfamA_acc_A')),
                ('pfama_acc_b', models.ForeignKey(related_name='interactor_target', to='webfront.Pfama', db_column='pfamA_acc_B')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_interactions',
            },
        ),
        migrations.CreateModel(
            name='PfamaInternal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_by', models.TextField(null=True, blank=True)),
                ('iterated', models.IntegerField()),
                ('iteration_gain', models.IntegerField(null=True, blank=True)),
                ('iterated_by', models.TextField(null=True, blank=True)),
                ('iteration_date', models.DateTimeField(null=True, blank=True)),
                ('seed', models.TextField(null=True, blank=True)),
                ('full', models.TextField(null=True, blank=True)),
                ('seed_is_ref_proteome', models.IntegerField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': '_pfamA_internal',
            },
        ),
        migrations.CreateModel(
            name='PfamaLigand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ligand', models.ForeignKey(to='webfront.Ligand')),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_ligand',
            },
        ),
        migrations.CreateModel(
            name='PfamaLiteratureReference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('order_added', models.IntegerField(null=True, blank=True)),
                ('auto_lit', models.ForeignKey(to='webfront.LiteratureReference', db_column='auto_lit')),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_literature_reference',
            },
        ),
        migrations.CreateModel(
            name='PfamaNcbi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('pfama_id', models.CharField(max_length=40, db_column='pfamA_id')),
                ('ncbi_taxid', models.ForeignKey(to='webfront.NcbiTaxonomy', db_column='ncbi_taxid')),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_ncbi',
            },
        ),
        migrations.CreateModel(
            name='PfamAnnseq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('annseq_storable', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'pfam_annseq',
            },
        ),
        migrations.CreateModel(
            name='PfamaRegFullInsignificant',
            fields=[
                ('auto_pfama_reg_full', models.AutoField(db_column='auto_pfamA_reg_full', serialize=False, primary_key=True)),
                ('auto_pfamseq', models.IntegerField()),
                ('seq_start', models.IntegerField()),
                ('seq_end', models.IntegerField()),
                ('model_start', models.IntegerField()),
                ('model_end', models.IntegerField()),
                ('domain_bits_score', models.FloatField()),
                ('domain_evalue_score', models.CharField(max_length=15)),
                ('sequence_bits_score', models.FloatField()),
                ('sequence_evalue_score', models.CharField(max_length=15)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_reg_full_insignificant',
            },
        ),
        migrations.CreateModel(
            name='PfamaRegFullSignificant',
            fields=[
                ('auto_pfama_reg_full', models.AutoField(db_column='auto_pfamA_reg_full', serialize=False, primary_key=True)),
                ('seq_start', models.IntegerField()),
                ('seq_end', models.IntegerField()),
                ('ali_start', models.IntegerField()),
                ('ali_end', models.IntegerField()),
                ('model_start', models.IntegerField()),
                ('model_end', models.IntegerField()),
                ('domain_bits_score', models.FloatField()),
                ('domain_evalue_score', models.CharField(max_length=15)),
                ('sequence_bits_score', models.FloatField()),
                ('sequence_evalue_score', models.CharField(max_length=15)),
                ('cigar', models.TextField(null=True, blank=True)),
                ('in_full', models.IntegerField()),
                ('tree_order', models.IntegerField(null=True, blank=True)),
                ('domain_order', models.IntegerField(null=True, blank=True)),
                ('domain_oder', models.IntegerField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_reg_full_significant',
            },
        ),
        migrations.CreateModel(
            name='PfamaRegSeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('seq_start', models.IntegerField()),
                ('seq_end', models.IntegerField()),
                ('cigar', models.TextField(null=True, blank=True)),
                ('tree_order', models.IntegerField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_reg_seed',
            },
        ),
        migrations.CreateModel(
            name='PfamaSpeciesTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('json_string', models.TextField()),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_species_tree',
            },
        ),
        migrations.CreateModel(
            name='PfamaTaxDepth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('root', models.CharField(max_length=24)),
                ('count', models.IntegerField()),
                ('common', models.TextField()),
                ('ncbi_taxid', models.IntegerField()),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_tax_depth',
            },
        ),
        migrations.CreateModel(
            name='PfamaWiki',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
                'managed': True,
                'db_table': 'pfamA_wiki',
            },
        ),
        migrations.CreateModel(
            name='Pfamseq',
            fields=[
                ('pfamseq_acc', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('pfamseq_id', models.CharField(max_length=16)),
                ('seq_version', models.IntegerField()),
                ('crc64', models.CharField(max_length=16)),
                ('md5', models.CharField(max_length=32)),
                ('description', models.TextField()),
                ('length', models.IntegerField()),
                ('species', models.TextField()),
                ('taxonomy', models.TextField(null=True, blank=True)),
                ('is_fragment', models.IntegerField(null=True, blank=True)),
                ('sequence', models.TextField()),
                ('updated', models.DateTimeField()),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('ncbi_taxid', models.IntegerField()),
                ('genome_seq', models.IntegerField(null=True, blank=True)),
                ('auto_architecture', models.BigIntegerField(null=True, blank=True)),
                ('treefam_acc', models.CharField(null=True, max_length=8, blank=True)),
                ('rp15', models.IntegerField(null=True, blank=True)),
                ('rp35', models.IntegerField(null=True, blank=True)),
                ('rp55', models.IntegerField(null=True, blank=True)),
                ('rp75', models.IntegerField(null=True, blank=True)),
                ('ref_proteome', models.IntegerField(null=True, blank=True)),
                ('complete_proteome', models.IntegerField(null=True, blank=True)),
                ('field_live_ref_proteome', models.IntegerField(null=True, blank=True, db_column='_live_ref_proteome')),
                ('evidence', models.ForeignKey(to='webfront.Evidence', db_column='evidence')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamseq',
            },
        ),
        migrations.CreateModel(
            name='PfamseqAntifam',
            fields=[
                ('pfamseq_acc', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('pfamseq_id', models.CharField(max_length=16)),
                ('seq_version', models.IntegerField()),
                ('crc64', models.CharField(max_length=16)),
                ('md5', models.CharField(max_length=32)),
                ('description', models.TextField()),
                ('evidence', models.IntegerField()),
                ('length', models.IntegerField()),
                ('species', models.TextField()),
                ('taxonomy', models.TextField(null=True, blank=True)),
                ('is_fragment', models.IntegerField(null=True, blank=True)),
                ('sequence', models.TextField()),
                ('antifam_acc', models.CharField(max_length=8)),
                ('antifam_id', models.CharField(max_length=16)),
                ('ncbi_taxid', models.ForeignKey(to='webfront.NcbiTaxonomy', db_column='ncbi_taxid')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamseq_antifam',
            },
        ),
        migrations.CreateModel(
            name='PfamseqDisulphide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('bond_start', models.IntegerField()),
                ('bond_end', models.IntegerField(null=True, blank=True)),
                ('pfamseq_acc', models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamseq_disulphide',
            },
        ),
        migrations.CreateModel(
            name='PfamseqMarkup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('residue', models.IntegerField()),
                ('annotation', models.TextField(null=True, blank=True)),
                ('auto_markup', models.ForeignKey(to='webfront.MarkupKey', db_column='auto_markup')),
                ('pfamseq_acc', models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamseq_markup',
            },
        ),
        migrations.CreateModel(
            name='PfamseqNcbi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ncbi_taxid', models.ForeignKey(to='webfront.NcbiTaxonomy', db_column='ncbi_taxid')),
                ('pfamseq_acc', models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'pfamseq_ncbi',
            },
        ),
        migrations.CreateModel(
            name='ProteomeArchitecture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('type_example', models.CharField(max_length=10)),
                ('no_seqs', models.IntegerField()),
                ('auto_architecture', models.ForeignKey(to='webfront.Architecture', db_column='auto_architecture')),
                ('auto_proteome', models.ForeignKey(to='webfront.CompleteProteomes', db_column='auto_proteome')),
            ],
            options={
                'managed': True,
                'db_table': 'proteome_architecture',
            },
        ),
        migrations.CreateModel(
            name='ProteomePfamseq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('auto_proteome', models.ForeignKey(to='webfront.CompleteProteomes', db_column='auto_proteome')),
                ('pfamseq_acc', models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'proteome_pfamseq',
            },
        ),
        migrations.CreateModel(
            name='ProteomeRegions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('count', models.IntegerField()),
                ('auto_proteome', models.ForeignKey(to='webfront.CompleteProteomes', db_column='auto_proteome')),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
                ('pfamseq_acc', models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'proteome_regions',
            },
        ),
        migrations.CreateModel(
            name='ReleasedClanVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('desc_file', models.CharField(max_length=32)),
                ('version', models.SmallIntegerField(null=True, blank=True)),
                ('clan_acc', models.ForeignKey(to='webfront.Clan', db_column='clan_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'released_clan_version',
            },
        ),
        migrations.CreateModel(
            name='ReleasedPfamVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('seed', models.CharField(max_length=32)),
                ('align', models.CharField(max_length=32)),
                ('desc_file', models.CharField(max_length=32)),
                ('hmm', models.CharField(max_length=32)),
                ('version', models.SmallIntegerField(null=True, blank=True)),
                ('pfama_acc', models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'released_pfam_version',
            },
        ),
        migrations.CreateModel(
            name='SecondaryPfamseqAcc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('secondary_acc', models.CharField(max_length=10)),
                ('pfamseq_acc', models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc')),
            ],
            options={
                'managed': True,
                'db_table': 'secondary_pfamseq_acc',
            },
        ),
        migrations.CreateModel(
            name='SeqInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('pfama_acc', models.CharField(max_length=7, db_column='pfamA_acc')),
                ('pfama_id', models.CharField(max_length=16, db_column='pfamA_id')),
                ('description', models.CharField(max_length=100)),
                ('pfamseq_id', models.CharField(max_length=12)),
                ('pfamseq_acc', models.CharField(max_length=16)),
                ('seq_description', models.TextField()),
                ('species', models.TextField()),
            ],
            options={
                'managed': True,
                'db_table': 'seq_info',
            },
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ncbi_taxid', models.IntegerField(null=True, blank=True)),
                ('species', models.CharField(null=True, max_length=100, blank=True)),
                ('taxonomy', models.TextField(null=True, blank=True)),
                ('lft', models.IntegerField(null=True, blank=True)),
                ('rgt', models.IntegerField(null=True, blank=True)),
                ('parent', models.IntegerField(null=True, blank=True)),
                ('level', models.CharField(null=True, max_length=200, blank=True)),
                ('minimal', models.IntegerField()),
                ('rank', models.CharField(null=True, max_length=100, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'taxonomy',
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('pfam_release', models.TextField(null=True, blank=True)),
                ('pfam_release_date', models.DateField(null=True, blank=True)),
                ('swiss_prot_version', models.TextField(null=True, blank=True)),
                ('trembl_version', models.TextField(null=True, blank=True)),
                ('hmmer_version', models.TextField(null=True, blank=True)),
                ('pfama_coverage', models.FloatField(null=True, blank=True, db_column='pfamA_coverage')),
                ('pfama_residue_coverage', models.FloatField(null=True, blank=True, db_column='pfamA_residue_coverage')),
                ('number_families', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'version',
            },
        ),
        migrations.CreateModel(
            name='Wikipedia',
            fields=[
                ('auto_wiki', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.TextField()),
                ('wikitext', models.TextField(null=True, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'wikipedia',
            },
        ),
        migrations.AddField(
            model_name='pfamawiki',
            name='auto_wiki',
            field=models.ForeignKey(to='webfront.Wikipedia', db_column='auto_wiki'),
        ),
        migrations.AddField(
            model_name='pfamawiki',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='pfamaregseed',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='pfamaregfullsignificant',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='pfamaregfullinsignificant',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='pfamannseq',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='pdbresiduedata',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='pdbpfamareg',
            name='auto_pfama_reg_full',
            field=models.ForeignKey(to='webfront.PfamaRegFullSignificant', db_column='auto_pfamA_reg_full'),
        ),
        migrations.AddField(
            model_name='pdbpfamareg',
            name='pdb',
            field=models.ForeignKey(to='webfront.Pdb'),
        ),
        migrations.AddField(
            model_name='otherreg',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='nestedlocations',
            name='nested_pfama_acc',
            field=models.ForeignKey(related_name='nested_location', to='webfront.Pfama', db_column='nested_pfamA_acc'),
        ),
        migrations.AddField(
            model_name='nestedlocations',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='nestedlocations',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='nesteddomains',
            name='nests_pfama_acc',
            field=models.ForeignKey(related_name='nested_domain', to='webfront.Pfama', db_column='nests_pfamA_acc'),
        ),
        migrations.AddField(
            model_name='nesteddomains',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='interpro',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='geneontology',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='edits',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='edits',
            name='pfamseq_acc',
            field=models.ForeignKey(to='webfront.Pfamseq', db_column='pfamseq_acc'),
        ),
        migrations.AddField(
            model_name='currentpfamversion',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='clanwiki',
            name='auto_wiki',
            field=models.ForeignKey(to='webfront.Wikipedia', db_column='auto_wiki'),
        ),
        migrations.AddField(
            model_name='clanwiki',
            name='clan_acc',
            field=models.ForeignKey(to='webfront.Clan', db_column='clan_acc'),
        ),
        migrations.AddField(
            model_name='clanmembership',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='clanlitref',
            name='auto_lit',
            field=models.ForeignKey(to='webfront.LiteratureReference', db_column='auto_lit'),
        ),
        migrations.AddField(
            model_name='clanlitref',
            name='clan_acc',
            field=models.ForeignKey(to='webfront.Clan', db_column='clan_acc'),
        ),
        migrations.AddField(
            model_name='alignmentandtree',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
        migrations.AddField(
            model_name='activesitealignments',
            name='pfama_acc',
            field=models.ForeignKey(to='webfront.Pfama', db_column='pfamA_acc'),
        ),
    ]
