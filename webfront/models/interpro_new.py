from django.db import models
from jsonfield import JSONField


class Entry(models.Model):
    entry_id = models.CharField(max_length=10,null=True)
    accession = models.CharField(primary_key=True, max_length=10)
    type = models.CharField(max_length=10)
    name = models.TextField()
    short_name = models.CharField(max_length=12)
    other_names = JSONField()
    source_database = models.CharField(max_length=20)
    member_databases = JSONField()
    integrated = models.ForeignKey("Entry",null=True,blank=True)
    go_terms = JSONField()
    description = models.TextField()
    wikipedia = models.TextField(null=True)
    literature = JSONField()

class Protein(models.Model):
    identifier = models.CharField(max_length=20, unique=True, null=False, primary_key=True)
    accession = models.CharField(max_length=20)
    organism = JSONField()
    name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField()
    description = models.TextField(null=True)
    sequence = models.TextField(null=False)
    length = models.IntegerField(null=False)
    proteome = models.CharField(max_length=20)
    gene = models.CharField(max_length=20, null=False)
    go_terms = JSONField()
    evidence_code  = models.IntegerField()
    feature  = JSONField() #signalpeptide, transmembrane, coiledCoil, lowComplexityDisorder, activeSites. PerResidue, diSulphideBridges
    structure = JSONField()
    genomic_context = JSONField()

class ProteinEntryFeature(models.Model):
    protein = models.ForeignKey("Protein", null=False)
    entry = models.ForeignKey("Entry", null=False)
    match_start = models.IntegerField()
    match_end = models.IntegerField()
