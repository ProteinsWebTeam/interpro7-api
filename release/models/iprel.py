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


class Citation(models.Model):
    pub_id = models.CharField(primary_key=True, max_length=11)
    pub_type = models.CharField(max_length=1)
    pubmed_id = models.IntegerField(unique=True, blank=True, null=True)
    isbn = models.CharField(max_length=10, blank=True, null=True)
    volume = models.CharField(max_length=55, blank=True, null=True)
    issue = models.CharField(max_length=55, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=740, blank=True, null=True)
    url = models.CharField(max_length=740, blank=True, null=True)
    rawpages = models.CharField(max_length=100, blank=True, null=True)
    medline_journal = models.CharField(max_length=255, blank=True, null=True)
    iso_journal = models.CharField(max_length=255, blank=True, null=True)
    authors = models.CharField(max_length=4000, blank=True, null=True)
    doi_url = models.CharField(max_length=1500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."citation"'


class CommonAnnotation(models.Model):
    ann_id = models.CharField(primary_key=True, max_length=7)
    name = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(unique=True, max_length=4000)
    comments = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."common_annotation"'


class CvDatabase(models.Model):
    dbcode = models.CharField(primary_key=True, max_length=1)
    dbname = models.CharField(unique=True, max_length=20)
    dborder = models.IntegerField(unique=True)
    dbshort = models.CharField(unique=True, max_length=10)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_database"'


class CvEntryType(models.Model):
    code = models.CharField(primary_key=True, max_length=1)
    abbrev = models.CharField(unique=True, max_length=20)
    description = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_entry_type"'


class CvEvidence(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    abbrev = models.CharField(unique=True, max_length=10)
    description = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_evidence"'


class CvRelation(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    abbrev = models.CharField(unique=True, max_length=10)
    description = models.CharField(max_length=2000, blank=True, null=True)
    forward = models.CharField(max_length=30)
    reverse = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_relation"'


class DbVersion(models.Model):
    # dbcode = models.ForeignKey(CvDatabase, db_column='dbcode', primary_key=True)
    dbcode = models.OneToOneField(CvDatabase, db_column='dbcode', primary_key=True)
    version = models.CharField(max_length=20)
    entry_count = models.IntegerField()
    file_date = models.DateField()
    load_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."db_version"'


class Entry(models.Model):
    entry_ac = models.CharField(primary_key=True, max_length=9)
    entry_type = models.ForeignKey(CvEntryType, db_column='entry_type')
    name = models.CharField(unique=True, max_length=100, blank=True, null=True)
    checked = models.CharField(max_length=1)
    created = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    short_name = models.CharField(unique=True, max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry"'


class Entry2Common(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    ann = models.ForeignKey(CommonAnnotation)
    order_in = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2common"'
        unique_together = (('entry_ac', 'ann'), ('entry_ac', 'ann', 'order_in'), ('entry_ac', 'order_in'))


class Entry2Comp(models.Model):
    # entry1_ac = models.ForeignKey(Entry, db_column='entry1_ac', primary_key=True)
    entry1_ac = models.OneToOneField(Entry, db_column='entry1_ac', primary_key=True, related_name='Entry1')
    entry2_ac = models.ForeignKey(Entry, db_column='entry2_ac', related_name='Entry2')
    relation = models.ForeignKey(CvRelation, db_column='relation')
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2comp"'
        unique_together = (('entry1_ac', 'entry2_ac'), )


class Entry2Entry(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', unique=True, primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', unique=True, primary_key=True)
    parent_ac = models.ForeignKey(Entry, db_column='parent_ac', related_name='ParentEntry')
    relation = models.ForeignKey(CvRelation, db_column='relation')
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2entry"'
        unique_together = (('entry_ac', 'parent_ac'),)


class Entry2Method(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    # method_ac = models.ForeignKey('Method', db_column='method_ac', unique=True)
    method_ac = models.OneToOneField('Method', db_column='method_ac', unique=True)
    evidence = models.ForeignKey(CvEvidence, db_column='evidence')
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    ida = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2method"'
        unique_together = (('entry_ac', 'method_ac'),)


class Entry2Pathway(models.Model):
    entry_ac = models.CharField(max_length=9)
    dbcode = models.CharField(max_length=1)
    ac = models.CharField(max_length=70)
    name = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2pathway"'


class Entry2Pub(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    order_in = models.IntegerField()
    pub = models.ForeignKey(Citation)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2pub"'
        unique_together = (('entry_ac', 'pub'), ('entry_ac', 'order_in'))


class EntryDeleted(models.Model):
    entry_ac = models.CharField(primary_key=True, max_length=9)
    remark = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_deleted"'


class EntryFriends(models.Model):
    entry1_ac = models.CharField(max_length=9)
    entry2_ac = models.CharField(max_length=9)
    s = models.IntegerField()
    p1 = models.IntegerField()
    p2 = models.IntegerField()
    pb = models.IntegerField()
    a1 = models.IntegerField()
    a2 = models.IntegerField()
    ab = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_friends"'
        unique_together = (('entry1_ac', 'entry2_ac'),)


class EntryXref(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    ac = models.CharField(max_length=70)
    name = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_xref"'
        unique_together = (('entry_ac', 'dbcode', 'ac'), )


class Etaxi(models.Model):
    tax_id = models.IntegerField()
    parent_id = models.IntegerField(blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    complete_genome_flag = models.CharField(max_length=1, blank=True, null=True)
    rank = models.CharField(max_length=50)
    hidden = models.FloatField(blank=True, null=True)
    left_number = models.FloatField(blank=True, null=True)
    right_number = models.FloatField(blank=True, null=True)
    annotation_source = models.CharField(max_length=1, blank=True, null=True)
    full_name = models.CharField(max_length=513, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."etaxi"'


class ExampleAuto(models.Model):
    entry_ac = models.CharField(max_length=9)
    protein_ac = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."example_auto"'
        unique_together = (('entry_ac', 'protein_ac'),)


class IntactData(models.Model):
    uniprot_id = models.CharField(max_length=30)
    protein_ac = models.CharField(max_length=30)
    undetermined = models.CharField(max_length=1, blank=True, null=True)
    intact_id = models.CharField(max_length=30)
    interacts_with = models.CharField(max_length=30)
    type = models.CharField(max_length=20, blank=True, null=True)
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    pubmed_id = models.CharField(max_length=30)
    interacts_with_id = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."intact_data"'
        unique_together = (('entry_ac', 'intact_id', 'interacts_with', 'protein_ac', 'pubmed_id'),)


class Interpro2Go(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    go_id = models.CharField(max_length=10)
    source = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."interpro2go"'
        unique_together = (('entry_ac', 'go_id', 'source'),)


class Iprscan2Dbcode(models.Model):
    iprscan_sig_lib_rel_id = models.IntegerField()
    dbcode = models.CharField(max_length=1)
    evidence = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."iprscan2dbcode"'


class Match(models.Model):
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    method_ac = models.ForeignKey('Method', db_column='method_ac')
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    status = models.CharField(max_length=1)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    evidence = models.ForeignKey(CvEvidence, db_column='evidence', blank=True, null=True)
    seq_date = models.DateField()
    match_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match"'
        unique_together = (('protein_ac', 'method_ac', 'pos_from', 'pos_to'),)


class MatchPanther(models.Model):
    protein_ac = models.CharField(max_length=15)
    method_ac = models.CharField(max_length=25)
    pos_from = models.IntegerField(blank=True, null=True)
    pos_to = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=1)
    dbcode = models.CharField(max_length=1)
    evidence = models.CharField(max_length=3, blank=True, null=True)
    seq_date = models.DateField()
    match_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match_panther"'


class MatchStruct(models.Model):
    protein_ac = models.CharField(max_length=15)
    domain = models.ForeignKey('StructClass')
    pos_from = models.IntegerField()
    pos_to = models.IntegerField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match_struct"'
        unique_together = (('protein_ac', 'domain', 'pos_from'),)


class Method(models.Model):
    method_ac = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=100, blank=True, null=True)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    method_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    skip_flag = models.CharField(max_length=1)
    candidate = models.CharField(max_length=1)
    description = models.CharField(max_length=220, blank=True, null=True)
    sig_type = models.ForeignKey(CvEntryType, db_column='sig_type', blank=True, null=True)
    abstract = models.CharField(max_length=4000, blank=True, null=True)
    abstract_long = models.TextField(blank=True, null=True)
    deleted = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method"'


class Method2Pub(models.Model):
    pub = models.ForeignKey(Citation)
    method_ac = models.ForeignKey(Method, db_column='method_ac')

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method2pub"'
        unique_together = (('method_ac', 'pub'),)


class MvEntry2ProteinTrue(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    match_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_entry2protein_true"'
        unique_together = (('entry_ac', 'protein_ac', 'entry_ac', 'protein_ac'),)


class MvMethod2Protein(models.Model):
    method_ac = models.ForeignKey(Method, db_column='method_ac')
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    match_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_method2protein"'
        unique_together = (('method_ac', 'protein_ac'),)


class MvMethodMatch(models.Model):
    # method_ac = models.ForeignKey(Method, db_column='method_ac', primary_key=True)
    method_ac = models.OneToOneField(Method, db_column='method_ac', primary_key=True)
    protein_count = models.IntegerField()
    match_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_method_match"'


class MvTaxEntryCount(models.Model):
    entry_ac = models.CharField(max_length=9)
    tax_id = models.IntegerField()
    count = models.FloatField(blank=True, null=True)
    count_specified_tax_id = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_tax_entry_count"'
        unique_together = (('entry_ac', 'tax_id'),)


class PdbPubAdditional(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    pub = models.ForeignKey(Citation)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."pdb_pub_additional"'


class PfamClan(models.Model):
    clan_id = models.CharField(max_length=15, blank=True, null=True)
    method_ac = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."pfam_clan"'


class PfamClanData(models.Model):
    clan_id = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=75, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."pfam_clan_data"'
        unique_together = (('clan_id', 'name'),)


class Protein(models.Model):
    protein_ac = models.CharField(primary_key=True, max_length=15)
    name = models.CharField(max_length=16)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    fragment = models.CharField(max_length=1)
    struct_flag = models.CharField(max_length=1)
    tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein"'


class StructClass(models.Model):
    domain_id = models.CharField(primary_key=True, max_length=14)
    fam_id = models.CharField(max_length=20, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."struct_class"'


class Supermatch(models.Model):
    protein_ac = models.ForeignKey(Protein, db_column='protein_ac')
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."supermatch"'
        unique_together = (('protein_ac', 'entry_ac', 'pos_from', 'pos_to'),)


class TaxNameToId(models.Model):
    tax_name = models.CharField(max_length=30, blank=True, null=True)
    tax_id = models.BigIntegerField(blank=True, null=True)
    parent = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tax_name_to_id"'


class UniprotPdbe(models.Model):
    entry_id = models.CharField(max_length=4)
    chain = models.CharField(max_length=4)
    sptr_ac = models.CharField(max_length=15)
    sptr_id = models.CharField(max_length=16)
    beg_seq = models.BigIntegerField(blank=True, null=True)
    end_seq = models.BigIntegerField(blank=True, null=True)
    method = models.CharField(max_length=6, blank=True, null=True)
    resolution = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pubmed_list = models.CharField(max_length=4000, blank=True, null=True)
    crc64 = models.CharField(max_length=16)
    flag = models.CharField(max_length=1)
    title = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_pdbe"'


class UniprotTaxonomy(models.Model):
    protein_ac = models.CharField(max_length=15)
    tax_id = models.BigIntegerField(blank=True, null=True)
    left_number = models.FloatField(blank=True, null=True)
    right_number = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_taxonomy"'


class VarsplicMaster(models.Model):
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    variant = models.IntegerField(blank=True, null=True)
    crc64 = models.CharField(max_length=16, blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."varsplic_master"'


class VarsplicMatch(models.Model):
    protein_ac = models.CharField(max_length=15)
    method_ac = models.ForeignKey(Method, db_column='method_ac')
    pos_from = models.IntegerField(blank=True, null=True)
    pos_to = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=1)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    evidence = models.ForeignKey(CvEvidence, db_column='evidence', blank=True, null=True)
    seq_date = models.DateField()
    match_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."varsplic_match"'


class Webstatus(models.Model):
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."webstatus"'
