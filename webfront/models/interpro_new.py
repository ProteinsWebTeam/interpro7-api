from django.db import models
from jsonfield import JSONField


class Entry(models.Model):
    entry_id = models.CharField(max_length=10, null=True)
    accession = models.CharField(primary_key=True, max_length=19)
    type = models.CharField(max_length=14)
    name = models.TextField()
    short_name = models.CharField(max_length=30)
    other_names = JSONField()
    source_database = models.CharField(max_length=20, db_index=True)
    member_databases = JSONField()
    integrated = models.ForeignKey("Entry", null=True, blank=True)
    go_terms = JSONField()
    description = JSONField()
    wikipedia = models.TextField(null=True)
    literature = JSONField()
    # Array of the string representing the domain architecture
    hierarchy = JSONField(null=True)


class Protein(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    identifier = models.CharField(max_length=20, unique=True, null=False)
    organism = JSONField()
    name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField()
    description = JSONField()
    sequence = models.TextField(null=False)
    length = models.IntegerField(null=False)
    proteome = models.CharField(max_length=20)
    gene = models.CharField(max_length=20, null=False)
    go_terms = JSONField()
    evidence_code = models.IntegerField()
    feature = JSONField()
    genomic_context = JSONField()
    source_database = models.CharField(max_length=20, default="uniprot", db_index=True)
    residues = JSONField()
    structure = JSONField(default={})
    fragment = models.CharField(max_length=1, null=False)
    # Domain arch string e.g. 275/UPI0004FEB881#29021:2-66~20422&29021&340&387:103-266#
    # domain_architectures = models.TextField(null=True)


class Structure(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField()
    experiment_type = models.CharField(max_length=30)
    release_date = models.DateField()
    authors = JSONField()
    chains = JSONField()
    source_database = models.CharField(max_length=20, default="pdb", db_index=True)
    #TODO add description
