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


class CabShadow(models.Model):
    ann_id = models.CharField(max_length=7)
    name = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(max_length=4000)
    comments = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cab_shadow"'


class CathDom(models.Model):
    entry = models.CharField(max_length=4)
    pdb_chain = models.CharField(max_length=1)
    cath_id = models.CharField(max_length=8)
    dbeg = models.CharField(max_length=10)
    dend = models.CharField(max_length=10)
    abeg = models.CharField(max_length=10)
    aend = models.CharField(max_length=10)
    rbeg = models.CharField(max_length=10)
    rend = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cath_dom"'


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


class Comments(models.Model):
    key = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    value = models.CharField(max_length=4000, blank=True, null=True)
    who = models.CharField(max_length=100)
    when = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."comments"'


class CommonAnnotation(models.Model):
    ann_id = models.CharField(primary_key=True, max_length=7)
    name = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(unique=True, max_length=4000)
    comments = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."common_annotation"'


class CommonAnnotationAudit(models.Model):
    ann_id = models.CharField(max_length=7, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    text = models.CharField(max_length=4000, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)
    comments = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."common_annotation_audit"'


class CreateJavaLobTable(models.Model):
    name = models.CharField(unique=True, max_length=700, blank=True, null=True)
    lob = models.BinaryField(blank=True, null=True)
    loadtime = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."create$java$lob$table"'


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


class CvIfc(models.Model):
    code = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_ifc"'


class CvRank(models.Model):
    rank = models.CharField(max_length=20, blank=True, null=True)
    seq = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_rank"'


class CvRelation(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    abbrev = models.CharField(unique=True, max_length=10)
    description = models.CharField(max_length=2000, blank=True, null=True)
    forward = models.CharField(max_length=30)
    reverse = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_relation"'


class CvStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=1)
    abbrev = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_status"'


class CvSynonym(models.Model):
    code = models.CharField(primary_key=True, max_length=4)
    description = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."cv_synonym"'


class DatabaseCount(models.Model):
    dbcode = models.CharField(max_length=1)
    what = models.CharField(max_length=40)
    total = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."database_count"'


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


class DbVersionAudit(models.Model):
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    version = models.CharField(max_length=20, blank=True, null=True)
    entry_count = models.IntegerField(blank=True, null=True)
    file_date = models.DateField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."db_version_audit"'


class Ding(models.Model):
    method_ac = models.CharField(max_length=25, blank=True, null=True)
    abstract = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."ding"'


class Domain2Family(models.Model):
    domain_ac = models.CharField(max_length=9)
    family_ac = models.CharField(max_length=9)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."domain2family"'
        unique_together = (('domain_ac', 'family_ac'),)


class Entry(models.Model):
    entry_ac = models.CharField(primary_key=True, max_length=9)
    entry_type = models.ForeignKey(CvEntryType, db_column='entry_type')
    name = models.CharField(unique=True, max_length=100, blank=True, null=True)
    checked = models.CharField(max_length=1)
    created = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    short_name = models.CharField(unique=True, max_length=30, blank=True, null=True)
    # commons = models.ManyToManyField(CommonAnnotation, through='Entry2Common')
    comps = models.ManyToManyField('Entry', through='Entry2Comp', related_name='EntryThroughComp')
    entries = models.ManyToManyField('Entry', through='Entry2Entry', related_name='EntryThroughEntry')
    ifcs = models.ManyToManyField('CvIfc', through='Entry2Ifc')

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


class Entry2CommonAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    ann_id = models.CharField(max_length=7, blank=True, null=True)
    order_in = models.IntegerField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2common_audit"'


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


class Entry2CompAudit(models.Model):
    entry1_ac = models.CharField(max_length=9, blank=True, null=True)
    entry2_ac = models.CharField(max_length=9, blank=True, null=True)
    relation = models.CharField(max_length=2, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2comp_audit"'


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


class Entry2EntryAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    parent_ac = models.CharField(max_length=9, blank=True, null=True)
    relation = models.CharField(max_length=2, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2entry_audit"'


class Entry2Ifc(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    code = models.ForeignKey(CvIfc, db_column='code')

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2ifc"'
        unique_together = (('entry_ac', 'code'),)


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


class Entry2MethodAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    method_ac = models.CharField(max_length=25, blank=True, null=True)
    evidence = models.CharField(max_length=3, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2method_audit"'


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
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    order_in = models.IntegerField()
    pub = models.ForeignKey(Citation)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2pub"'
        unique_together = (('entry_ac', 'pub'), ('entry_ac', 'order_in'))


class Entry2PubAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    order_in = models.IntegerField(blank=True, null=True)
    pub_id = models.CharField(max_length=11, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry2pub_audit"'


class EntryAccpair(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    secondary_ac = models.CharField(max_length=9)
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_accpair"'
        unique_together = (('entry_ac', 'secondary_ac'),)


class EntryAccpairAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    secondary_ac = models.CharField(max_length=9, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_accpair_audit"'


class EntryAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    entry_type = models.CharField(max_length=1, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)
    short_name = models.CharField(max_length=30, blank=True, null=True)
    checked = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_audit"'


class EntryColour(models.Model):
    entry_ac = models.CharField(max_length=9)
    colour_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_colour"'
        unique_together = (('entry_ac', 'colour_id'),)


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


class EntryXrefAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    ac = models.CharField(max_length=70, blank=True, null=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."entry_xref_audit"'


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


class Example(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')

    class Meta:
        managed = False
        db_table = '"INTERPRO"."example"'
        unique_together = (('entry_ac', 'protein_ac'),)


class ExampleArchive(models.Model):
    entry_ac = models.CharField(max_length=9)
    protein_ac = models.CharField(max_length=15)
    order_in = models.IntegerField()
    description = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."example_archive"'


class ExampleAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    order_in = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."example_audit"'


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


class IntactDataStg(models.Model):
    uniprot_id = models.CharField(max_length=30)
    protein_ac = models.CharField(max_length=30)
    undetermined = models.CharField(max_length=1, blank=True, null=True)
    intact_id = models.CharField(max_length=30)
    interacts_with = models.CharField(max_length=30)
    type = models.CharField(max_length=20, blank=True, null=True)
    entry_ac = models.CharField(max_length=30)
    pubmed_id = models.CharField(max_length=30, blank=True, null=True)
    interacts_with_id = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."intact_data_stg"'


class Interpro2Go(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    go_id = models.CharField(max_length=10)
    source = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."interpro2go"'
        unique_together = (('entry_ac', 'go_id', 'source'),)


class Interpro2GoAudit(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    go_id = models.CharField(max_length=10, blank=True, null=True)
    source = models.CharField(max_length=4, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."interpro2go_audit"'


class Iprscan2Dbcode(models.Model):
    iprscan_sig_lib_rel_id = models.IntegerField()
    dbcode = models.CharField(max_length=1)
    evidence = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."iprscan2dbcode"'


class JavaClassMd5Table(models.Model):
    name = models.CharField(unique=True, max_length=200, blank=True, null=True)
    md5 = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = '"INTERPRO"."java$class$md5$table"'


class JavaOptions(models.Model):
    what = models.CharField(max_length=128, blank=True, null=True)
    opt = models.CharField(max_length=20, blank=True, null=True)
    value = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."java$options"'


class LogDetail(models.Model):
    log = models.ForeignKey('LogExecution', blank=True, null=True)
    inserted = models.DateField(blank=True, null=True)
    loglevel = models.NullBooleanField()
    elapsed = models.FloatField(blank=True, null=True)
    cnt = models.FloatField(blank=True, null=True)
    val = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."log_detail"'


class LogError(models.Model):
    log = models.ForeignKey('LogExecution', blank=True, null=True)
    inserted = models.DateField(blank=True, null=True)
    ora_code = models.FloatField(blank=True, null=True)
    ora_msg = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."log_error"'


class LogExecution(models.Model):
    log_id = models.FloatField(primary_key=True)
    module = models.CharField(max_length=30, blank=True, null=True)
    proc = models.CharField(max_length=30, blank=True, null=True)
    start_time = models.DateField(blank=True, null=True)
    end_time = models.DateField(blank=True, null=True)
    elapsed = models.FloatField(blank=True, null=True)
    exec_status = models.CharField(max_length=1, blank=True, null=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    os_user = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."log_execution"'


class Match(models.Model):
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    method_ac = models.ForeignKey('Method', db_column='method_ac')
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    status = models.ForeignKey(CvStatus, db_column='status')
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


class MatchCountIndexes(models.Model):
    table_name = models.CharField(max_length=30, blank=True, null=True)
    index_name = models.CharField(max_length=30, blank=True, null=True)
    index_ddl = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match_count_indexes"'


class MatchLoadStatus(models.Model):
    dsname = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(max_length=512, blank=True, null=True)
    tstamp_mn_start = models.DateTimeField(blank=True, null=True)
    tstamp_mn_end = models.DateTimeField(blank=True, null=True)
    tstamp_m_end = models.DateTimeField(blank=True, null=True)
    tstamp_m_start = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match_load_status"'


class MatchNew(models.Model):
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    method_ac = models.ForeignKey('Method', db_column='method_ac')
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    status = models.ForeignKey(CvStatus, db_column='status')
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    evidence = models.ForeignKey(CvEvidence, db_column='evidence', blank=True, null=True)
    seq_date = models.DateField()
    match_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match_new"'
        unique_together = (('protein_ac', 'method_ac', 'pos_from', 'pos_to'),)


class MatchNewStg(models.Model):
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
        db_table = '"INTERPRO"."match_new_stg"'


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


class MatchPirsf(models.Model):
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
        db_table = '"INTERPRO"."match_pirsf"'


class MatchStats(models.Model):
    dbname = models.CharField(max_length=20)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')
    status = models.CharField(max_length=1)
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."match_stats"'


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


class Merops(models.Model):
    code = models.CharField(max_length=8)
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    name = models.CharField(max_length=120)
    method_ac = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."merops"'
        unique_together = (('code', 'protein_ac', 'pos_from', 'pos_to'),)


class MeropsNew(models.Model):
    code = models.CharField(max_length=8)
    protein_ac = models.CharField(max_length=15)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    name = models.CharField(max_length=120)
    method_ac = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."merops_new"'
        unique_together = (('code', 'protein_ac', 'pos_from', 'pos_to'),)


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


class Method2Abstract(models.Model):
    method_ac = models.CharField(max_length=25)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30)
    entry_type = models.CharField(max_length=1)
    abstract = models.CharField(max_length=4000)
    timestamp = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method2abstract"'


class Method2Pub(models.Model):
    pub = models.ForeignKey(Citation)
    method_ac = models.ForeignKey(Method, db_column='method_ac')

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method2pub"'
        unique_together = (('method_ac', 'pub'),)


class Method2SwissDe(models.Model):
    protein_ac = models.CharField(max_length=100)
    description = models.CharField(max_length=4000, blank=True, null=True)
    method_ac = models.CharField(max_length=100)
    status = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method2swiss_de"'


class MethodAudit(models.Model):
    method_ac = models.CharField(max_length=25, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    method_date = models.DateField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)
    skip_flag = models.CharField(max_length=1, blank=True, null=True)
    candidate = models.CharField(max_length=1, blank=True, null=True)
    description = models.CharField(max_length=220, blank=True, null=True)
    sig_type = models.CharField(max_length=1, blank=True, null=True)
    abstract = models.CharField(max_length=4000, blank=True, null=True)
    abstract_long = models.TextField(blank=True, null=True)
    deleted = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method_audit"'


class MethodStg(models.Model):
    method_ac = models.CharField(max_length=25, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=220, blank=True, null=True)
    sig_type = models.CharField(max_length=1, blank=True, null=True)
    abstract = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."method_stg"'
        unique_together = (('method_ac', 'name'),)


class MethodsToDeleteTempTable(models.Model):
    method_ac = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."methods_to_delete_temp_table"'


class Modbase(models.Model):
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    beg = models.IntegerField(blank=True, null=True)
    end = models.IntegerField(blank=True, null=True)
    crc = models.CharField(max_length=16, blank=True, null=True)
    percent_id = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    evalue = models.FloatField(blank=True, null=True)
    score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."modbase"'


class ModbaseTmp(models.Model):
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    beg = models.IntegerField(blank=True, null=True)
    end = models.IntegerField(blank=True, null=True)
    evalue = models.FloatField(blank=True, null=True)
    r = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."modbase_tmp"'


class MvEntry2Protein(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    match_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_entry2protein"'
        unique_together = (('entry_ac', 'protein_ac', 'entry_ac', 'protein_ac'),)


class MvEntry2ProteinTrue(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    protein_ac = models.ForeignKey('Protein', db_column='protein_ac')
    match_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_entry2protein_true"'
        unique_together = (('entry_ac', 'protein_ac', 'entry_ac', 'protein_ac'),)


class MvEntry2UniparcTrue(models.Model):
    entry_ac = models.CharField(max_length=9)
    uniparc_id = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_entry2uniparc_true"'


class MvEntryMatch(models.Model):
    # entry_ac = models.ForeignKey(Entry, db_column='entry_ac', primary_key=True)
    entry_ac = models.OneToOneField(Entry, db_column='entry_ac', primary_key=True)
    protein_count = models.IntegerField()
    match_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_entry_match"'


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


class MvPdb2Interpro2Go(models.Model):
    db_id = models.CharField(max_length=32)
    pdb_id = models.CharField(max_length=32)
    chain_id = models.CharField(max_length=32)
    entry_ac = models.CharField(max_length=9)
    method_ac = models.CharField(max_length=75)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    go_id = models.CharField(max_length=30)
    tax_id = models.BigIntegerField(blank=True, null=True)
    uniprot_ac = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_pdb2interpro2go"'


class MvPdb2Interpro2GoBak(models.Model):
    db_id = models.CharField(max_length=32)
    pdb_id = models.CharField(max_length=32)
    chain_id = models.CharField(max_length=32)
    entry_ac = models.CharField(max_length=9)
    method_ac = models.CharField(max_length=75)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    go_id = models.CharField(max_length=30)
    tax_id = models.BigIntegerField(blank=True, null=True)
    uniprot_ac = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_pdb2interpro2go_bak"'


class MvProteinMethodTax(models.Model):
    protein_ac = models.CharField(max_length=15)
    method_ac = models.CharField(max_length=25)
    tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_protein_method_tax"'


class MvProteomeCount(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    name = models.CharField(max_length=100)
    oscode = models.ForeignKey('Organism', db_column='oscode')
    protein_count = models.IntegerField()
    method_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_proteome_count"'
        unique_together = (('entry_ac', 'oscode'),)


class MvSecondary(models.Model):
    entry_ac = models.CharField(max_length=9)
    secondary_ac = models.CharField(max_length=9)
    method_ac = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_secondary"'


class MvTaxEntryCount(models.Model):
    entry_ac = models.CharField(max_length=9)
    tax_id = models.IntegerField()
    count = models.FloatField(blank=True, null=True)
    count_specified_tax_id = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_tax_entry_count"'
        unique_together = (('entry_ac', 'tax_id'),)


class MvUniprot2Interpro2Go(models.Model):
    protein_ac = models.CharField(max_length=15)
    entry_ac = models.CharField(max_length=9)
    go_id = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."mv_uniprot2interpro2go"'


class Onion2Dbcode(models.Model):
    onion_type = models.IntegerField()
    dbcode = models.CharField(max_length=1)
    evidence = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."onion2dbcode"'


class Organism(models.Model):
    oscode = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=100)
    italics_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    tax_code = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."organism"'


class Pathway2Ec(models.Model):
    pathway_id = models.CharField(max_length=25)
    ec = models.CharField(max_length=15)
    dbcode = models.ForeignKey(CvDatabase, db_column='dbcode')

    class Meta:
        managed = False
        db_table = '"INTERPRO"."pathway2ec"'


class Pdb2Pub(models.Model):
    pub = models.ForeignKey(Citation)
    domain_id = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."pdb2pub"'
        unique_together = (('domain_id', 'pub'),)


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


class PfamNested(models.Model):
    pfam1 = models.CharField(max_length=25)
    pfam2 = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."pfam_nested"'


class PrefileMatch(models.Model):
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
        db_table = '"INTERPRO"."prefile_match"'


class PrefileMethod(models.Model):
    method_ac = models.CharField(max_length=25)
    name = models.CharField(max_length=30)
    dbcode = models.CharField(max_length=1)
    method_date = models.DateField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    skip_flag = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."prefile_method"'


class ProfileArchive(models.Model):
    entry_ac = models.CharField(max_length=9)
    method_ac = models.CharField(max_length=25)
    name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=30, blank=True, null=True)
    abstract = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."profile_archive"'


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


class Protein2Genome(models.Model):
    protein_ac = models.CharField(max_length=15)
    oscode = models.CharField(max_length=5)
    has_string = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein2genome"'
        unique_together = (('oscode', 'protein_ac'),)


class ProteinTaxonomyHierarchyDm(models.Model):
    protein_ac = models.CharField(max_length=15)
    tree_tax_id = models.FloatField(blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=306, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein__taxonomy_hierarchy_dm"'


class ProteinAccpair(models.Model):
    protein_ac = models.ForeignKey(Protein, db_column='protein_ac')
    secondary_ac = models.CharField(max_length=15)
    userstamp = models.CharField(max_length=30)
    timestamp = models.DateField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_accpair"'
        unique_together = (('protein_ac', 'secondary_ac'),)


class ProteinAccpairAudit(models.Model):
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    secondary_ac = models.CharField(max_length=15, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_accpair_audit"'


class ProteinAccpairNew(models.Model):
    protein_ac = models.ForeignKey(Protein, db_column='protein_ac')
    secondary_ac = models.CharField(max_length=15)
    timestamp = models.DateField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_accpair_new"'
        unique_together = (('protein_ac', 'secondary_ac'),)


class ProteinAccpairNewTmp(models.Model):
    protein_ac = models.CharField(max_length=15)
    secondary_ac = models.CharField(max_length=15)
    timestamp = models.DateField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_accpair_new_tmp"'


class ProteinChanges(models.Model):
    flag = models.CharField(max_length=1, blank=True, null=True)
    old_rowid = models.TextField(unique=True, blank=True, null=True)  # This field type is a guess.
    new_rowid = models.TextField(unique=True, blank=True, null=True)  # This field type is a guess.
    old_protein_ac = models.CharField(unique=True, max_length=15, blank=True, null=True)
    new_protein_ac = models.CharField(unique=True, max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_changes"'


class ProteinChangesTmp(models.Model):
    flag = models.CharField(max_length=1, blank=True, null=True)
    old_rowid = models.TextField(blank=True, null=True)  # This field type is a guess.
    new_rowid = models.TextField(blank=True, null=True)  # This field type is a guess.
    old_protein_ac = models.CharField(max_length=6, blank=True, null=True)
    new_protein_ac = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_changes_tmp"'


class ProteinIda(models.Model):
    # protein_ac = models.ForeignKey(Protein, db_column='protein_ac', primary_key=True)
    protein_ac = models.OneToOneField(Protein, db_column='protein_ac', primary_key=True)
    ida = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_ida"'


class ProteinIdaOld(models.Model):
    protein_ac = models.CharField(max_length=15)
    ida = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_ida_old"'


class ProteinNew(models.Model):
    protein_ac = models.CharField(unique=True, max_length=15)
    name = models.CharField(max_length=16)
    dbcode = models.CharField(max_length=1)
    fragment = models.CharField(max_length=1)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    timestamp = models.DateField()
    tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_new"'


class ProteinNewTmp(models.Model):
    protein_ac = models.CharField(max_length=15)
    name = models.CharField(max_length=12)
    dbcode = models.CharField(max_length=1)
    fragment = models.CharField(max_length=1)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    timestamp = models.DateField()
    tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_new_tmp"'


class ProteinTmp(models.Model):
    protein_ac = models.CharField(max_length=15)
    name = models.CharField(max_length=12)
    dbcode = models.CharField(max_length=1)
    crc64 = models.CharField(max_length=16)
    len = models.IntegerField()
    timestamp = models.DateField()
    userstamp = models.CharField(max_length=30)
    fragment = models.CharField(max_length=1)
    struct_flag = models.CharField(max_length=1)
    tax_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_tmp"'


class ProteinToScan(models.Model):
    protein_ac = models.CharField(primary_key=True, max_length=15)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    upi = models.CharField(max_length=13, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_to_scan"'


class ProteinToScanTmp(models.Model):
    protein_ac = models.CharField(max_length=15)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    upi = models.CharField(max_length=13, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."protein_to_scan_tmp"'


class ProteomeRank(models.Model):
    entry_ac = models.ForeignKey(Entry, db_column='entry_ac')
    oscode = models.ForeignKey(Organism, db_column='oscode')
    rank = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."proteome_rank"'
        unique_together = (('entry_ac', 'oscode'),)


class SanityCheck(models.Model):
    name = models.CharField(primary_key=True, max_length=30)
    implementation = models.CharField(max_length=10)
    description = models.CharField(max_length=300)
    result = models.CharField(max_length=12, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."sanity_check"'


class SanityReport(models.Model):
    name = models.ForeignKey(SanityCheck, db_column='name')
    line_num = models.IntegerField()
    report = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."sanity_report"'
        unique_together = (('name', 'line_num'),)


class SchemaVersionLog(models.Model):
    release = models.CharField(primary_key=True, max_length=100)
    upgradetime = models.DateField()
    message = models.CharField(max_length=150)
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."schema_version_log"'


class ScopDom(models.Model):
    entry = models.CharField(max_length=4)
    pdb_chain = models.CharField(max_length=1)
    scop_id = models.CharField(max_length=8)
    dbeg = models.CharField(max_length=10)
    dend = models.CharField(max_length=10)
    abeg = models.CharField(max_length=10)
    aend = models.CharField(max_length=10)
    rbeg = models.CharField(max_length=10)
    rend = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."scop_dom"'


class ShortNameVocab(models.Model):
    entry_name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(unique=True, max_length=40, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."short_name_vocab"'


class ShortNameVocabAudit(models.Model):
    entry_name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=40, blank=True, null=True)
    dbuser = models.CharField(max_length=30, blank=True, null=True)
    osuser = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    action = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."short_name_vocab_audit"'


class SproExample(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    tax_name_concat = models.CharField(max_length=80, blank=True, null=True)
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    struct_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."spro_example"'


class SptrUnobs(models.Model):
    accession_code = models.CharField(max_length=4)
    pdb_chain = models.CharField(max_length=1)
    sptr_ac = models.CharField(max_length=6, blank=True, null=True)
    pdb_seq = models.IntegerField(blank=True, null=True)
    serial = models.IntegerField(blank=True, null=True)
    ins_code = models.CharField(max_length=1, blank=True, null=True)
    not_observed = models.CharField(max_length=1, blank=True, null=True)
    sunid = models.IntegerField(blank=True, null=True)
    cath_domain = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."sptr_unobs"'


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


class SupermatchNew(models.Model):
    protein_ac = models.CharField(max_length=15)
    entry_ac = models.CharField(max_length=9)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."supermatch_new"'


class Swissmodel(models.Model):
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    md5 = models.CharField(max_length=32, blank=True, null=True)
    beg = models.IntegerField(blank=True, null=True)
    end = models.IntegerField(blank=True, null=True)
    crc64 = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."swissmodel"'


class TaxExampleGroup(models.Model):
    tax_name = models.CharField(max_length=80, blank=True, null=True)
    example_group = models.FloatField(blank=True, null=True)
    order_in = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tax_example_group"'
        unique_together = (('tax_name', 'example_group'), ('example_group', 'order_in'),)


class TaxLineage(models.Model):
    ref_tax_id = models.BigIntegerField()
    parent_id = models.BigIntegerField()
    scientific_name = models.CharField(max_length=100)
    order_t = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tax_lineage"'
        unique_together = (('ref_tax_id', 'parent_id'),)


class TaxNameToId(models.Model):
    tax_name = models.CharField(max_length=30, blank=True, null=True)
    tax_id = models.BigIntegerField(blank=True, null=True)
    parent = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tax_name_to_id"'


class TaxonomyLoad(models.Model):
    tax_id = models.IntegerField()
    parent_id = models.IntegerField(blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    rank = models.CharField(max_length=50)
    common_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."taxonomy_load"'


class TempTaxHierarchy(models.Model):
    leaf_tax_id = models.FloatField(blank=True, null=True)
    tree_tax_id = models.FloatField(blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=306, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."temp_tax_hierarchy"'


class TextIndexEntry(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    field = models.CharField(max_length=20, blank=True, null=True)
    text = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."text_index_entry"'


class TmpDbinnsPhobius(models.Model):
    upi = models.CharField(max_length=1020)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tmp_dbinns_phobius"'


class TmpIda(models.Model):
    protein_ac = models.CharField(primary_key=True, max_length=15)
    ida = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tmp_ida"'


class TmpPfamaBlackBox(models.Model):
    upi = models.CharField(max_length=13)
    method_ac = models.CharField(max_length=25)
    seq_start = models.IntegerField()
    seq_end = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."tmp_pfama_black_box"'
        unique_together = (('upi', 'method_ac', 'seq_start', 'seq_end'),)


class TremblExample(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    tax_name_concat = models.CharField(max_length=80, blank=True, null=True)
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    struct_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."trembl_example"'


class UniparcProtein(models.Model):
    seq_short = models.CharField(max_length=4000, blank=True, null=True)
    seq_long = models.TextField(blank=True, null=True)
    upi = models.CharField(max_length=13)
    md5 = models.CharField(max_length=32)
    crc64 = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniparc_protein"'


class UniparcXref(models.Model):
    ac = models.CharField(max_length=42)
    dbid = models.IntegerField()
    upi = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniparc_xref"'


class UniprotClass(models.Model):
    domain_id = models.CharField(max_length=14)
    fam_id = models.CharField(max_length=20, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_class"'


class UniprotOvlap(models.Model):
    entry_ac = models.CharField(max_length=9)
    protein_ac = models.CharField(max_length=15)
    dbcode = models.CharField(max_length=1)
    ac = models.CharField(max_length=20)
    name = models.CharField(max_length=20, blank=True, null=True)
    overlap = models.IntegerField(blank=True, null=True)
    p_count = models.IntegerField(blank=True, null=True)
    d_count = models.IntegerField(blank=True, null=True)
    n_d = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_ovlap"'


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


class UniprotSblob(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    entry_type = models.CharField(max_length=1, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    ac = models.CharField(max_length=20, blank=True, null=True)
    overlap = models.IntegerField(blank=True, null=True)
    p_count = models.IntegerField(blank=True, null=True)
    d_count = models.IntegerField(blank=True, null=True)
    n_d = models.IntegerField(blank=True, null=True)
    len = models.IntegerField(blank=True, null=True)
    coverage = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    suplen = models.IntegerField(blank=True, null=True)
    n = models.IntegerField(blank=True, null=True)
    sblob = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    dom_id = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_sblob"'


class UniprotSdom(models.Model):
    entry_id = models.CharField(max_length=4)
    method = models.CharField(max_length=5, blank=True, null=True)
    resolution = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dom_id = models.CharField(max_length=7)
    fam_id = models.CharField(max_length=20, blank=True, null=True)
    dom_db = models.CharField(max_length=1)
    sptr_ac = models.CharField(max_length=15)
    sptr_id = models.CharField(max_length=16)
    beg_seq = models.IntegerField()
    end_seq = models.IntegerField(blank=True, null=True)
    crc64 = models.CharField(max_length=16)
    flag = models.CharField(max_length=1, blank=True, null=True)
    chain = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_sdom"'
        unique_together = (('sptr_ac', 'entry_id', 'dom_id', 'beg_seq'),)


class UniprotStruct(models.Model):
    protein_ac = models.CharField(max_length=15)
    domain_id = models.CharField(max_length=14)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_struct"'
        unique_together = (('protein_ac', 'domain_id', 'pos_from'),)


class UniprotSxref(models.Model):
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    ac = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_sxref"'


class UniprotTaxonomy(models.Model):
    protein_ac = models.CharField(max_length=15)
    tax_id = models.BigIntegerField(blank=True, null=True)
    left_number = models.FloatField(blank=True, null=True)
    right_number = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."uniprot_taxonomy"'


class UserAccountInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=30)
    email = models.CharField(max_length=100, blank=True, null=True)
    team = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."user_account_info"'


class UserSession(models.Model):
    session_id = models.IntegerField()
    user_id = models.IntegerField()
    server_key = models.CharField(max_length=16, blank=True, null=True)
    max_idle = models.IntegerField(blank=True, null=True)
    last_used = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."user_session"'


class UserSettings(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=4000, blank=True, null=True)
    encrypted = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."user_settings"'


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


class VarsplicNew(models.Model):
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    method_ac = models.CharField(max_length=25, blank=True, null=True)
    pos_from = models.FloatField(blank=True, null=True)
    pos_to = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=1, blank=True, null=True)
    dbcode = models.CharField(max_length=1, blank=True, null=True)
    evidence = models.CharField(max_length=3, blank=True, null=True)
    seq_date = models.DateField(blank=True, null=True)
    match_date = models.DateField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    userstamp = models.CharField(max_length=30, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."varsplic_new"'


class VarsplicSupermatch(models.Model):
    protein_ac = models.CharField(max_length=15)
    entry_ac = models.CharField(max_length=9)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."varsplic_supermatch"'
        unique_together = (('protein_ac', 'entry_ac', 'pos_from', 'pos_to'),)


class ViolatorsEntryXref(models.Model):
    entry_ac = models.CharField(max_length=9)
    dbcode = models.CharField(max_length=1)
    ac = models.CharField(max_length=30)
    name = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."violators_entry_xref"'


class Webstatus(models.Model):
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."webstatus"'


class XrefSummary(models.Model):
    dbcode = models.CharField(max_length=8, blank=True, null=True)
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    short_name = models.CharField(max_length=30, blank=True, null=True)
    method_ac = models.CharField(max_length=25, blank=True, null=True)
    method_name = models.CharField(max_length=30, blank=True, null=True)
    pos_from = models.IntegerField(blank=True, null=True)
    pos_to = models.IntegerField(blank=True, null=True)
    match_status = models.CharField(max_length=1, blank=True, null=True)
    match_status_final = models.CharField(max_length=15, blank=True, null=True)
    match_count = models.IntegerField(blank=True, null=True)
    match_date = models.DateField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."xref_summary"'


class ZeusJobsLogs(models.Model):
    collect_date = models.DateField()
    job = models.FloatField()
    log_user = models.CharField(max_length=30)
    priv_user = models.CharField(max_length=30)
    schema_user = models.CharField(max_length=30)
    last_date = models.DateField(blank=True, null=True)
    this_date = models.DateField(blank=True, null=True)
    next_date = models.DateField()
    total_time = models.FloatField(blank=True, null=True)
    broken = models.CharField(max_length=1, blank=True, null=True)
    interval = models.CharField(max_length=200)
    failures = models.FloatField(blank=True, null=True)
    what = models.CharField(max_length=4000, blank=True, null=True)
    nls_env = models.CharField(max_length=4000, blank=True, null=True)
    misc_env = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = '"INTERPRO"."zeus_jobs_logs"'
        unique_together = (('collect_date', 'job'),)


class ZeusSegmentArchived(models.Model):
    collect_date = models.DateField()
    obj_field = models.FloatField(db_column='obj#')  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    owner = models.CharField(max_length=30)
    object_type = models.CharField(max_length=18)
    object_name = models.CharField(max_length=30)
    statistic_field = models.FloatField(db_column='statistic#', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    statistic_name = models.CharField(max_length=64, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '"INTERPRO"."zeus_segment_archived"'


class ZeusSegmentLogs(models.Model):
    collect_date = models.DateField()
    obj_field = models.FloatField(db_column='obj#')  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    owner = models.CharField(max_length=30)
    object_type = models.CharField(max_length=18)
    object_name = models.CharField(max_length=30)
    statistic_field = models.FloatField(db_column='statistic#')  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    statistic_name = models.CharField(max_length=64)
    value = models.FloatField()

    class Meta:
        managed = False
        db_table = '"INTERPRO"."zeus_segment_logs"'
