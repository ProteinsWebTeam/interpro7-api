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


class DwEntry(models.Model):
    entry_pk = models.FloatField(primary_key=True)
    entry_ac = models.CharField(unique=True, max_length=9)
    entry_type = models.CharField(max_length=1)
    checked = models.CharField(max_length=1)
    name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=30, blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    pathways_and_interactions = models.FloatField(blank=True, null=True)
    proteins_matched = models.FloatField(blank=True, null=True)
    domain_organisations = models.FloatField(blank=True, null=True)
    structures = models.FloatField(blank=True, null=True)
    related_resources = models.FloatField(blank=True, null=True)
    citations = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry'


class DwEntryCitation(models.Model):
    entry_citation_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    id = models.CharField(primary_key=True, max_length=11)
    title = models.CharField(max_length=740, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    volume = models.CharField(max_length=55, blank=True, null=True)
    rawpages = models.CharField(max_length=100, blank=True, null=True)
    doi_url = models.CharField(max_length=1500, blank=True, null=True)
    pubmed_id = models.IntegerField(blank=True, null=True)
    iso_journal = models.CharField(max_length=255, blank=True, null=True)
    authors = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_citation'


class DwEntryDomainOrg(models.Model):
    entry_do_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    ida_fk = models.FloatField(blank=True, null=True)
    ida = models.TextField(blank=True, null=True)
    count_ida = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_domain_org'


class DwEntryGo(models.Model):
    entry_go_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    entry_ac = models.CharField(max_length=9)
    go_id = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'dw_entry_go'


class DwEntryHierarchy(models.Model):
    hierarchy_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    flag = models.CharField(max_length=1, blank=True, null=True)
    rel_entry_ac = models.CharField(max_length=9, blank=True, null=True)
    rel_entry_name = models.CharField(max_length=100, blank=True, null=True)
    rel_parent_entry_ac = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_hierarchy'


class DwEntryInteraction(models.Model):
    entry_interaction_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    protein_id = models.CharField(max_length=30, blank=True, null=True)
    protein_ac = models.CharField(max_length=30)
    interactor_protein_name = models.CharField(max_length=30, blank=True, null=True)
    interactor_protein_ac = models.CharField(max_length=30)
    intact_id = models.CharField(max_length=30)
    pubmed_id = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_interaction'


class DwEntryMethod(models.Model):
    entry_method_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    dbcode = models.CharField(max_length=1)
    method_ac = models.CharField(max_length=25)
    method_name = models.CharField(max_length=100, blank=True, null=True)
    clan_id = models.CharField(max_length=15, blank=True, null=True)
    clan_name = models.CharField(max_length=50)
    clan_description = models.CharField(max_length=75, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_method'


class DwEntryPathway(models.Model):
    entry_pathway_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    dbcode = models.CharField(max_length=1)
    pathway_ac = models.CharField(max_length=70)
    pathway_name = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_pathway'


class DwEntryProteinsMatched(models.Model):
    pm_pk = models.FloatField(blank=True, primary_key=True)
    entry_fk = models.FloatField()
    dbid = models.IntegerField()
    xref_fk = models.FloatField(blank=True, null=True)
    protein_ac = models.CharField(max_length=60)
    description = models.CharField(max_length=4000, blank=True, null=True)
    tax_id = models.IntegerField(blank=True, null=True)
    taxonomy_full_name = models.CharField(max_length=513, blank=True, null=True)
    len = models.IntegerField()
    struct_flag = models.CharField(max_length=1)
    ida = models.TextField(blank=True, null=True)
    ida_fk = models.FloatField(blank=True, null=True)
    materialised_path = models.CharField(max_length=1024, blank=True, null=True)
    seq_fk = models.FloatField(blank=True, null=True)
    entry_list = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_proteins_matched'
        unique_together = (('entry_fk', 'dbid', 'protein_ac'),)


class DwEntryRelatedResource(models.Model):
    entry_related_resource_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    dbcode = models.CharField(max_length=1)
    id = models.CharField(primary_key=True, max_length=70)
    xref_name = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_related_resource'


class DwEntrySequence(models.Model):
    entry_ac = models.CharField(max_length=50)
    seq_fk = models.FloatField(blank=True, null=True)
    occurrence_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_sequence'


class DwEntrySignature(models.Model):
    entry_signature_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    dbcode = models.CharField(max_length=1)
    method_ac = models.CharField(max_length=25)
    method_name = models.CharField(max_length=100, blank=True, null=True)
    signature_protein_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_entry_signature'


class DwEntryStructure(models.Model):
    entry_structure_pk = models.FloatField(blank=True,primary_key=True)
    entry_fk = models.FloatField(blank=True, null=True)
    dbcode = models.CharField(max_length=1)
    xref_identifier = models.CharField(max_length=70)

    class Meta:
        managed = False
        db_table = 'dw_entry_structure'
        unique_together = (('entry_structure_pk', 'entry_fk'),)


class DwProteinXref(models.Model):
    xref_pk = models.FloatField(unique=True, blank=True, null=True)
    protein_ac = models.CharField(unique=True, max_length=60)
    fragment = models.CharField(max_length=1)
    dbid = models.IntegerField()
    tax_id = models.IntegerField(blank=True, null=True)
    taxonomy_scientific_name = models.CharField(max_length=255, blank=True, null=True)
    taxonomy_full_name = models.CharField(max_length=513, blank=True, null=True)
    seq_fk = models.FloatField(blank=True, null=True)
    struct_flag = models.CharField(max_length=1)
    protein_name = models.CharField(unique=True, max_length=20, blank=True, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)
    len = models.FloatField(blank=True, null=True)
    entry_list = models.CharField(max_length=4000, blank=True, null=True)
    ida_fk = models.FloatField(blank=True, null=True)
    ida = models.TextField(blank=True, null=True)
    ida_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_protein_xref'


class DwSeqStructPred(models.Model):
    seq_struct_pred_pk = models.FloatField(blank=True, null=True)
    xref_fk = models.FloatField(blank=True, null=True)
    seq_fk = models.FloatField(blank=True, null=True)
    dbname = models.CharField(max_length=20)
    domain_id = models.CharField(max_length=14, blank=True, null=True)
    class_id = models.CharField(max_length=20, blank=True, null=True)
    pos_from = models.IntegerField(blank=True, null=True)
    pos_to = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_seq_struct_pred'


class DwSequence(models.Model):
    seq_pk = models.FloatField(primary_key=True)
    md5 = models.CharField(max_length=32)
    seq = models.TextField(blank=True, null=True)
    len = models.FloatField(blank=True, null=True)
    ida_count = models.FloatField(blank=True, null=True)
    has_struct_xref = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_sequence'


class DwSignatureMatches(models.Model):
    signature_matches_pk = models.FloatField(blank=True, null=True)
    protein_ac = models.CharField(max_length=15, blank=True, null=True)
    method_ac = models.CharField(max_length=25)
    status = models.CharField(max_length=1)
    pos_from = models.IntegerField(blank=True, null=True)
    pos_to = models.IntegerField(blank=True, null=True)
    match_score = models.FloatField(blank=True, null=True)
    method_name = models.CharField(max_length=100, blank=True, null=True)
    method_database_name = models.CharField(max_length=20)
    entry_ac = models.CharField(max_length=9, blank=True, null=True)
    entry_short_name = models.CharField(max_length=30, blank=True, null=True)
    entry_name = models.CharField(max_length=100, blank=True, null=True)
    entry_type = models.CharField(max_length=20, blank=True, null=True)
    seq_fk = models.FloatField(blank=True, null=True)
    xref_fk = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_signature_matches'


class DwSignatureProteinsMatched(models.Model):
    spm_pk = models.FloatField(blank=True, null=True)
    method_ac = models.CharField(max_length=25)
    dbid = models.IntegerField()
    xref_fk = models.FloatField(blank=True, null=True)
    protein_ac = models.CharField(max_length=60)
    description = models.CharField(max_length=4000, blank=True, null=True)
    taxonomy_full_name = models.CharField(max_length=513, blank=True, null=True)
    len = models.IntegerField()
    struct_flag = models.CharField(max_length=1)
    ida = models.TextField(blank=True, null=True)
    seq_fk = models.FloatField(blank=True, null=True)
    entry_list = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_signature_proteins_matched'
        unique_together = (('method_ac', 'dbid', 'protein_ac'),)


class DwSupermatch(models.Model):
    seq_fk = models.FloatField()
    entry_ac = models.CharField(max_length=50)
    pos_from = models.IntegerField()
    pos_to = models.IntegerField()
    entry_type = models.CharField(max_length=1)
    ida_fk = models.FloatField()

    class Meta:
        managed = False
        db_table = 'dw_supermatch'
        unique_together = (('seq_fk', 'ida_fk', 'entry_ac', 'pos_from', 'pos_to'),)


class DwTaxEntryCount(models.Model):
    tax_entry_count_pk = models.FloatField(blank=True, null=True)
    entry_fk = models.FloatField(blank=True, null=True)
    entry_ac = models.CharField(max_length=9)
    tax_entry_count = models.FloatField(blank=True, null=True)
    count_specified_tax_id = models.FloatField(blank=True, null=True)
    tax_id = models.IntegerField()
    parent_id = models.IntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=513, blank=True, null=True)
    materialised_path = models.CharField(max_length=1024, blank=True, null=True)
    parent_tec_fk = models.BigIntegerField(blank=True, null=True)
    has_children = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_tax_entry_count'


class DwXrefPdbe(models.Model):
    xref_pdbe_pk = models.FloatField(blank=True, null=True)
    xref_fk = models.FloatField(blank=True, null=True)
    entry_id = models.CharField(max_length=4)
    title = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dw_xref_pdbe'