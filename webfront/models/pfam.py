# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Pfama(models.Model):
    pfama_acc = models.CharField(db_column='pfamA_acc', primary_key=True, max_length=7)  # Field name made lowercase.
    pfama_id = models.CharField(db_column='pfamA_id', unique=True, max_length=16)  # Field name made lowercase.
    previous_id = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=100)
    author = models.TextField(blank=True, null=True)
    deposited_by = models.CharField(max_length=100)
    seed_source = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=11)
    comment = models.TextField(blank=True, null=True)
    sequence_ga = models.FloatField(db_column='sequence_GA', null=True)  # Field name made lowercase.
    domain_ga = models.FloatField(db_column='domain_GA', null=True)  # Field name made lowercase.
    sequence_tc = models.FloatField(db_column='sequence_TC', null=True)  # Field name made lowercase.
    domain_tc = models.FloatField(db_column='domain_TC', null=True)  # Field name made lowercase.
    sequence_nc = models.FloatField(db_column='sequence_NC', null=True)  # Field name made lowercase.
    domain_nc = models.FloatField(db_column='domain_NC', null=True)  # Field name made lowercase.
    buildmethod = models.TextField(db_column='buildMethod', null=True)  # Field name made lowercase.
    model_length = models.IntegerField(null=True)
    searchmethod = models.TextField(db_column='searchMethod', null=True)  # Field name made lowercase.
    msv_lambda = models.FloatField(null=True)
    msv_mu = models.FloatField(null=True)
    viterbi_lambda = models.FloatField(null=True)
    viterbi_mu = models.FloatField(null=True)
    forward_lambda = models.FloatField(null=True)
    forward_tau = models.FloatField(null=True)
    num_seed = models.IntegerField(blank=True, null=True)
    num_full = models.IntegerField(blank=True, null=True)
    updated = models.DateTimeField(null=True)
    created = models.DateTimeField(blank=True, null=True)
    version = models.SmallIntegerField(blank=True, null=True)
    number_archs = models.IntegerField(blank=True, null=True)
    number_species = models.IntegerField(blank=True, null=True)
    number_structures = models.IntegerField(blank=True, null=True)
    number_ncbi = models.IntegerField(blank=True, null=True)
    number_meta = models.IntegerField(blank=True, null=True)
    average_length = models.FloatField(blank=True, null=True)
    percentage_id = models.IntegerField(blank=True, null=True)
    average_coverage = models.FloatField(blank=True, null=True)
    change_status = models.TextField(blank=True, null=True)
    seed_consensus = models.TextField(blank=True, null=True)
    full_consensus = models.TextField(blank=True, null=True)
    number_shuffled_hits = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA'



class ActiveSiteAlignments(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    alignment = models.TextField(blank=True, null=True)
    as_residues = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '_active_site_alignments'


class Lock(models.Model):
    locked = models.IntegerField()
    locker = models.CharField(max_length=10)
    allowcommits = models.IntegerField(db_column='allowCommits')  # Field name made lowercase.
    alsoallow = models.TextField(db_column='alsoAllow')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = '_lock'


class PfamaInternal(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    created_by = models.TextField(blank=True, null=True)
    iterated = models.IntegerField()
    iteration_gain = models.IntegerField(blank=True, null=True)
    iterated_by = models.TextField(blank=True, null=True)
    iteration_date = models.DateTimeField(blank=True, null=True)
    seed = models.TextField(blank=True, null=True)
    full = models.TextField(blank=True, null=True)
    seed_is_ref_proteome = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '_pfamA_internal'


class AlignmentAndTree(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    alignment = models.TextField(blank=True, null=True)
    tree = models.TextField(blank=True, null=True)
    jtml = models.TextField(blank=True, null=True)
    post = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'alignment_and_tree'


class Architecture(models.Model):
    auto_architecture = models.BigIntegerField(primary_key=True)
    architecture = models.TextField(blank=True, null=True)
    type_example = models.CharField(max_length=10)
    no_seqs = models.IntegerField()
    architecture_acc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'architecture'


class Clan(models.Model):
    clan_acc = models.CharField(primary_key=True, max_length=6)
    clan_id = models.CharField(unique=True, max_length=40)
    previous_id = models.CharField(max_length=75, blank=True, null=True)
    clan_description = models.CharField(max_length=100, blank=True, null=True)
    clan_author = models.TextField(blank=True, null=True)
    deposited_by = models.CharField(max_length=100)
    clan_comment = models.TextField(blank=True, null=True)
    updated = models.DateTimeField()
    created = models.DateTimeField(blank=True, null=True)
    version = models.SmallIntegerField(blank=True, null=True)
    number_structures = models.IntegerField(blank=True, null=True)
    number_archs = models.IntegerField(blank=True, null=True)
    number_species = models.IntegerField(blank=True, null=True)
    number_sequences = models.IntegerField(blank=True, null=True)
    competed = models.IntegerField(blank=True, null=True)
    members = models.ManyToManyField(Pfama, through="ClanMembership",related_name="clan")

    class Meta:
        managed = False
        db_table = 'clan'


class ClanAlignmentAndRelationship(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    alignment = models.TextField(blank=True, null=True)
    relationship = models.TextField(blank=True, null=True)
    image_map = models.TextField(blank=True, null=True)
    stockholm = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clan_alignment_and_relationship'


class ClanArchitecture(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    auto_architecture = models.ForeignKey(Architecture, db_column='auto_architecture')

    class Meta:
        managed = False
        db_table = 'clan_architecture'


class ClanDatabaseLinks(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    db_id = models.TextField()
    comment = models.TextField(blank=True, null=True)
    db_link = models.TextField()
    other_params = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clan_database_links'


class ClanLitRef(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    auto_lit = models.ForeignKey('LiteratureReference', db_column='auto_lit')
    order_added = models.IntegerField()
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clan_lit_ref'


class ClanMembership(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'clan_membership'
        unique_together = ('clan_acc','pfama_acc')


class ClanWiki(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    auto_wiki = models.ForeignKey('Wikipedia', db_column='auto_wiki')

    class Meta:
        managed = False
        db_table = 'clan_wiki'


class CompleteProteomes(models.Model):
    auto_proteome = models.AutoField(primary_key=True)
    ncbi_taxid = models.IntegerField(unique=True)
    species = models.CharField(max_length=256, blank=True, null=True)
    grouping = models.CharField(max_length=20, blank=True, null=True)
    num_distinct_regions = models.IntegerField()
    num_total_regions = models.IntegerField()
    num_proteins = models.IntegerField()
    sequence_coverage = models.IntegerField()
    residue_coverage = models.IntegerField()
    total_genome_proteins = models.IntegerField()
    total_aa_length = models.BigIntegerField()
    total_aa_covered = models.IntegerField(blank=True, null=True)
    total_seqs_covered = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'complete_proteomes'


class CurrentPfamVersion(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    seed = models.CharField(max_length=32)
    align = models.CharField(max_length=32)
    desc_file = models.CharField(max_length=32)
    hmm = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'current_pfam_version'


class DeadClan(models.Model):
    clan_acc = models.CharField(unique=True, max_length=7)
    clan_id = models.CharField(max_length=40)
    clan_description = models.CharField(max_length=100, blank=True, null=True)
    clan_membership = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    forward_to = models.CharField(max_length=6, blank=True, null=True)
    user = models.TextField(blank=True, null=True)
    killed = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dead_clan'


class DeadFamily(models.Model):
    pfama_acc = models.CharField(db_column='pfamA_acc', unique=True, max_length=7)  # Field name made lowercase.
    pfama_id = models.CharField(db_column='pfamA_id', max_length=40)  # Field name made lowercase.
    comment = models.TextField(blank=True, null=True)
    forward_to = models.CharField(max_length=7, blank=True, null=True)
    user = models.CharField(max_length=10)
    killed = models.DateTimeField()
    title = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dead_family'


class Edits(models.Model):
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    seq_version = models.IntegerField(blank=True, null=True)
    original_start = models.IntegerField()
    original_end = models.IntegerField()
    new_start = models.IntegerField(blank=True, null=True)
    new_end = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edits'


class Evidence(models.Model):
    evidence = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'evidence'


class GeneOntology(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    go_id = models.TextField()
    term = models.TextField()
    category = models.TextField()

    class Meta:
        managed = False
        db_table = 'gene_ontology'


class Interpro(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    interpro_id = models.TextField()
    abstract = models.TextField()

    class Meta:
        managed = False
        db_table = 'interpro'


class Ligand(models.Model):
    ligand_id = models.CharField(primary_key=True, max_length=3)
    name = models.TextField()
    formula = models.TextField()
    molecular_weight = models.FloatField()
    smiles = models.TextField()
    inchi = models.TextField()

    class Meta:
        managed = False
        db_table = 'ligand'


class LiteratureReference(models.Model):
    auto_lit = models.AutoField(primary_key=True)
    pmid = models.IntegerField(unique=True, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    journal = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'literature_reference'


class MarkupKey(models.Model):
    auto_markup = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'markup_key'


class NcbiTaxonomy(models.Model):
    ncbi_taxid = models.IntegerField(primary_key=True)
    species = models.CharField(max_length=100)
    taxonomy = models.TextField()

    class Meta:
        managed = False
        db_table = 'ncbi_taxonomy'


class NestedDomains(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    nests_pfama_acc = models.ForeignKey('Pfama', db_column='nests_pfamA_acc', related_name='nested_domain')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'nested_domains'


class NestedLocations(models.Model):
    pfama_acc = models.ForeignKey('Pfama', db_column='pfamA_acc')  # Field name made lowercase.
    nested_pfama_acc = models.ForeignKey('Pfama', db_column='nested_pfamA_acc', related_name='nested_location')  # Field name made lowercase.
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    seq_version = models.IntegerField(blank=True, null=True)
    seq_start = models.IntegerField(blank=True, null=True)
    seq_end = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nested_locations'


class OtherReg(models.Model):
    region_id = models.AutoField(primary_key=True)
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    seq_start = models.IntegerField()
    seq_end = models.IntegerField()
    type_id = models.CharField(max_length=20)
    source_id = models.CharField(max_length=20)
    score = models.FloatField(blank=True, null=True)
    orientation = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_reg'


class Pdb(models.Model):
    pdb_id = models.CharField(primary_key=True, max_length=5)
    keywords = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    resolution = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    method = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pdb'


class PdbImage(models.Model):
    pdb = models.ForeignKey(Pdb)
    pdb_image = models.TextField(blank=True, null=True)
    pdb_image_sml = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pdb_image'


class PdbPfamaReg(models.Model):
    auto_pdb_reg = models.AutoField(primary_key=True)
    auto_pfama_reg_full = models.ForeignKey('PfamaRegFullSignificant', db_column='auto_pfamA_reg_full')  # Field name made lowercase.
    pdb = models.ForeignKey(Pdb)
    pfama_acc = models.CharField(db_column='pfamA_acc', max_length=7)  # Field name made lowercase.
    pfamseq_acc = models.CharField(max_length=10)
    chain = models.CharField(max_length=4, blank=True, null=True)
    pdb_res_start = models.IntegerField(blank=True, null=True)
    pdb_start_icode = models.CharField(max_length=1, blank=True, null=True)
    pdb_res_end = models.IntegerField(blank=True, null=True)
    pdb_end_icode = models.CharField(max_length=1, blank=True, null=True)
    seq_start = models.IntegerField()
    seq_end = models.IntegerField()
    hex_colour = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pdb_pfamA_reg'


class PdbResidueData(models.Model):
    pdb = models.ForeignKey(Pdb)
    chain = models.CharField(max_length=4, blank=True, null=True)
    serial = models.IntegerField(blank=True, null=True)
    pdb_res = models.CharField(max_length=3, blank=True, null=True)
    pdb_seq_number = models.IntegerField(blank=True, null=True)
    pdb_insert_code = models.CharField(max_length=1, blank=True, null=True)
    observed = models.IntegerField(blank=True, null=True)
    dssp_code = models.CharField(max_length=4, blank=True, null=True)
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    pfamseq_res = models.CharField(max_length=3, blank=True, null=True)
    pfamseq_seq_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pdb_residue_data'



class Pfama2PfamaHhsearch(models.Model):
    pfama_acc_1 = models.ForeignKey(Pfama, db_column='pfamA_acc_1', related_name='relationship_source', primary_key=True)  # Field name made lowercase.
    pfama_acc_2 = models.ForeignKey(Pfama, db_column='pfamA_acc_2', related_name='relationship_target')  # Field name made lowercase.
    evalue = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'pfamA2pfamA_hhsearch'
        unique_together = ('pfama_acc_1','pfama_acc_2')


class Pfama2PfamaScoop(models.Model):
    pfama_acc_1 = models.ForeignKey(Pfama, db_column='pfamA_acc_1', related_name='scoop_source')  # Field name made lowercase.
    pfama_acc_2 = models.ForeignKey(Pfama, db_column='pfamA_acc_2', related_name='scoop_target')  # Field name made lowercase.
    score = models.FloatField()

    class Meta:
        managed = False
        db_table = 'pfamA2pfamA_scoop'


class PfamaHmm(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc',primary_key=True)  # Field name made lowercase.
    hmm = models.TextField(blank=True, null=True)
    #logo = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA_HMM'


class PfamaArchitecture(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    auto_architecture = models.ForeignKey(Architecture, db_column='auto_architecture')

    class Meta:
        managed = False
        db_table = 'pfamA_architecture'


class PfamaDatabaseLinks(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    db_id = models.TextField()
    comment = models.TextField(blank=True, null=True)
    db_link = models.TextField()
    other_params = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA_database_links'


class PfamaFasta(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    fasta = models.TextField(blank=True, null=True)
    nr_threshold = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA_fasta'


class PfamaInteractions(models.Model):
    pfama_acc_a = models.ForeignKey(Pfama, db_column='pfamA_acc_A', related_name='interactor_source')  # Field name made lowercase.
    pfama_acc_b = models.ForeignKey(Pfama, db_column='pfamA_acc_B', related_name='interactor_target')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pfamA_interactions'


class PfamaLigand(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    ligand = models.ForeignKey(Ligand)

    class Meta:
        managed = False
        db_table = 'pfamA_ligand'


class PfamaLiteratureReference(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    auto_lit = models.ForeignKey(LiteratureReference, db_column='auto_lit')
    comment = models.TextField(blank=True, null=True)
    order_added = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA_literature_reference'


class PfamaNcbi(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    pfama_id = models.CharField(db_column='pfamA_id', max_length=40)  # Field name made lowercase.
    ncbi_taxid = models.ForeignKey(NcbiTaxonomy, db_column='ncbi_taxid')

    class Meta:
        managed = False
        db_table = 'pfamA_ncbi'


class PfamaRegFullInsignificant(models.Model):
    auto_pfama_reg_full = models.AutoField(db_column='auto_pfamA_reg_full', primary_key=True)  # Field name made lowercase.
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    auto_pfamseq = models.IntegerField()
    seq_start = models.IntegerField()
    seq_end = models.IntegerField()
    model_start = models.IntegerField()
    model_end = models.IntegerField()
    domain_bits_score = models.FloatField()
    domain_evalue_score = models.CharField(max_length=15)
    sequence_bits_score = models.FloatField()
    sequence_evalue_score = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'pfamA_reg_full_insignificant'


class PfamaRegFullSignificant(models.Model):
    auto_pfama_reg_full = models.AutoField(db_column='auto_pfamA_reg_full', primary_key=True)  # Field name made lowercase.
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    seq_start = models.IntegerField()
    seq_end = models.IntegerField()
    ali_start = models.IntegerField()
    ali_end = models.IntegerField()
    model_start = models.IntegerField()
    model_end = models.IntegerField()
    domain_bits_score = models.FloatField(null=True)
    domain_evalue_score = models.CharField(max_length=15)
    sequence_bits_score = models.FloatField(null=True)
    sequence_evalue_score = models.CharField(max_length=15)
    cigar = models.TextField(blank=True, null=True)
    in_full = models.IntegerField()
    tree_order = models.IntegerField(blank=True, null=True)
    # domain_order = models.IntegerField(blank=True, null=True)
    # domain_oder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA_reg_full_significant'


class PfamaRegSeed(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    seq_start = models.IntegerField()
    seq_end = models.IntegerField()
    cigar = models.TextField(blank=True, null=True)
    tree_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamA_reg_seed'


class PfamaSpeciesTree(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    json_string = models.TextField()

    class Meta:
        managed = False
        db_table = 'pfamA_species_tree'


class PfamaTaxDepth(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    root = models.CharField(max_length=24)
    count = models.IntegerField()
    common = models.TextField()
    ncbi_taxid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pfamA_tax_depth'


class PfamaWiki(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    auto_wiki = models.ForeignKey('Wikipedia', db_column='auto_wiki')

    class Meta:
        managed = False
        db_table = 'pfamA_wiki'


class PfamAnnseq(models.Model):
    pfamseq_acc = models.ForeignKey('Pfamseq', db_column='pfamseq_acc')
    annseq_storable = models.TextField()

    class Meta:
        managed = False
        db_table = 'pfam_annseq'


class Pfamseq(models.Model):
    pfamseq_acc = models.CharField(primary_key=True, max_length=10)
    pfamseq_id = models.CharField(max_length=16)
    seq_version = models.IntegerField(blank=True, null=True)
    crc64 = models.CharField(max_length=16)
    md5 = models.CharField(max_length=32)
    description = models.TextField(blank=True, null=True)
    evidence = models.ForeignKey(Evidence, db_column='evidence')
    length = models.IntegerField(null=True)
    species = models.TextField(blank=True, null=True)
    taxonomy = models.TextField(blank=True, null=True)
    is_fragment = models.IntegerField(blank=True, null=True)
    sequence = models.TextField(null=True)
    updated = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    ncbi_taxid = models.IntegerField(null=True)
    genome_seq = models.IntegerField(blank=True, null=True)
    auto_architecture = models.BigIntegerField(blank=True, null=True)
    treefam_acc = models.CharField(max_length=8, blank=True, null=True)
    # rp15 = models.IntegerField(blank=True, null=True)
    # rp35 = models.IntegerField(blank=True, null=True)
    # rp55 = models.IntegerField(blank=True, null=True)
    # rp75 = models.IntegerField(blank=True, null=True)
    # ref_proteome = models.IntegerField(blank=True, null=True)
    # complete_proteome = models.IntegerField(blank=True, null=True)
    # field_live_ref_proteome = models.IntegerField(db_column='_live_ref_proteome', blank=True, null=True)  # Field renamed because it started with '_'.

    class Meta:
        managed = False
        db_table = 'pfamseq'


class PfamseqAntifam(models.Model):
    pfamseq_acc = models.CharField(primary_key=True, max_length=10)
    pfamseq_id = models.CharField(max_length=16)
    seq_version = models.IntegerField()
    crc64 = models.CharField(max_length=16)
    md5 = models.CharField(max_length=32)
    description = models.TextField()
    evidence = models.IntegerField()
    length = models.IntegerField()
    species = models.TextField()
    taxonomy = models.TextField(blank=True, null=True)
    is_fragment = models.IntegerField(blank=True, null=True)
    sequence = models.TextField()
    ncbi_taxid = models.ForeignKey(NcbiTaxonomy, db_column='ncbi_taxid')
    antifam_acc = models.CharField(max_length=8)
    antifam_id = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'pfamseq_antifam'


class PfamseqDisulphide(models.Model):
    pfamseq_acc = models.ForeignKey(Pfamseq, db_column='pfamseq_acc')
    bond_start = models.IntegerField()
    bond_end = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamseq_disulphide'


class PfamseqMarkup(models.Model):
    pfamseq_acc = models.ForeignKey(Pfamseq, db_column='pfamseq_acc',primary_key=True)
    auto_markup = models.ForeignKey(MarkupKey, db_column='auto_markup',primary_key=True)
    residue = models.IntegerField(primary_key=True)
    annotation = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfamseq_markup'
        unique_together = (('pfamseq_acc', 'auto_markup', 'residue'),)


class PfamseqNcbi(models.Model):
    pfamseq_acc = models.ForeignKey(Pfamseq, db_column='pfamseq_acc')
    ncbi_taxid = models.ForeignKey(NcbiTaxonomy, db_column='ncbi_taxid')

    class Meta:
        managed = False
        db_table = 'pfamseq_ncbi'


class ProteomeArchitecture(models.Model):
    auto_proteome = models.ForeignKey(CompleteProteomes, db_column='auto_proteome')
    auto_architecture = models.ForeignKey(Architecture, db_column='auto_architecture')
    type_example = models.CharField(max_length=10)
    no_seqs = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'proteome_architecture'


class ProteomePfamseq(models.Model):
    pfamseq_acc = models.ForeignKey(Pfamseq, db_column='pfamseq_acc')
    auto_proteome = models.ForeignKey(CompleteProteomes, db_column='auto_proteome')

    class Meta:
        managed = False
        db_table = 'proteome_pfamseq'


class ProteomeRegions(models.Model):
    auto_proteome = models.ForeignKey(CompleteProteomes, db_column='auto_proteome')
    pfamseq_acc = models.ForeignKey(Pfamseq, db_column='pfamseq_acc')
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'proteome_regions'


class ReleasedClanVersion(models.Model):
    clan_acc = models.ForeignKey(Clan, db_column='clan_acc')
    desc_file = models.CharField(max_length=32)
    version = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'released_clan_version'


class ReleasedPfamVersion(models.Model):
    pfama_acc = models.ForeignKey(Pfama, db_column='pfamA_acc')  # Field name made lowercase.
    seed = models.CharField(max_length=32)
    align = models.CharField(max_length=32)
    desc_file = models.CharField(max_length=32)
    hmm = models.CharField(max_length=32)
    version = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'released_pfam_version'


class SecondaryPfamseqAcc(models.Model):
    pfamseq_acc = models.ForeignKey(Pfamseq, db_column='pfamseq_acc')
    secondary_acc = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'secondary_pfamseq_acc'


class SeqInfo(models.Model):
    pfama_acc = models.CharField(db_column='pfamA_acc', max_length=7)  # Field name made lowercase.
    pfama_id = models.CharField(db_column='pfamA_id', max_length=16)  # Field name made lowercase.
    description = models.CharField(max_length=100)
    pfamseq_id = models.CharField(max_length=12)
    pfamseq_acc = models.CharField(max_length=16)
    seq_description = models.TextField()
    species = models.TextField()

    class Meta:
        managed = False
        db_table = 'seq_info'


class Taxonomy(models.Model):
    ncbi_taxid = models.IntegerField(blank=True, null=True)
    species = models.CharField(max_length=100, blank=True, null=True)
    taxonomy = models.TextField(blank=True, null=True)
    lft = models.IntegerField(blank=True, null=True)
    rgt = models.IntegerField(blank=True, null=True)
    parent = models.IntegerField(blank=True, null=True)
    level = models.CharField(max_length=200, blank=True, null=True)
    minimal = models.IntegerField()
    rank = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'taxonomy'


class Version(models.Model):
    pfam_release = models.TextField(blank=True, null=True)
    pfam_release_date = models.DateField(blank=True, null=True)
    swiss_prot_version = models.TextField(blank=True, null=True)
    trembl_version = models.TextField(blank=True, null=True)
    hmmer_version = models.TextField(blank=True, null=True)
    pfama_coverage = models.FloatField(db_column='pfamA_coverage', blank=True, null=True)  # Field name made lowercase.
    pfama_residue_coverage = models.FloatField(db_column='pfamA_residue_coverage', blank=True, null=True)  # Field name made lowercase.
    number_families = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'version'


class Wikipedia(models.Model):
    auto_wiki = models.AutoField(primary_key=True)
    title = models.TextField()
    wikitext = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wikipedia'
