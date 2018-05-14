from django.db import models
from jsonfield import JSONField

class Database(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    code = models.CharField(max_length=1)
    name_long = models.CharField(max_length=100)
    description = models.TextField(null=True)
    version = models.CharField(max_length=100, null=True)
    release_date = models.DateField(null=True)
    type = models.CharField(max_length=100)


class Entry(models.Model):
    entry_id = models.CharField(max_length=10, null=True)
    accession = models.CharField(primary_key=True, max_length=25)
    type = models.CharField(max_length=50)
    name = models.TextField()
    short_name = models.CharField(max_length=100)
    # other_names = JSONField(null=True)
    source_database = models.CharField(max_length=100, db_index=True)
    member_databases = JSONField(null=True)
    integrated = models.ForeignKey("Entry", on_delete=models.SET_NULL, null=True, blank=True)
    go_terms = JSONField(null=True)
    description = JSONField(null=True)
    wikipedia = models.TextField(null=True)
    literature = JSONField(null=True)
    hierarchy = JSONField(null=True)
    cross_references = JSONField(null=True)
    entry_date = models.DateField(null=True)
    is_featured = models.CharField(max_length=2)


class EntryAnnotation(models.Model):
    annotation_id = models.CharField(max_length=40, primary_key=True)
    accession = models.ForeignKey(Entry, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=32)
    value = models.BinaryField()
    mime_type = models.CharField(max_length=32)


class Protein(models.Model):
    accession = models.CharField(max_length=15, primary_key=True)
    identifier = models.CharField(max_length=16, unique=True, null=False)
    organism = JSONField(null=True)
    name = models.CharField(max_length=20)
    # short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField(null=True)
    description = JSONField(null=True)
    sequence = models.TextField(null=False)
    length = models.IntegerField(null=False)
    proteomes = JSONField(null=True)
    gene = models.CharField(max_length=70, null=True)
    go_terms = JSONField(null=True)
    evidence_code = models.IntegerField()
    # feature = JSONField(null=True)
    # genomic_context = JSONField(null=True)
    source_database = models.CharField(max_length=20, default="unreviewed", db_index=True)
    residues = JSONField(null=True)
    structure = JSONField(default={})
    fragment = models.CharField(max_length=1, null=False)
    tax_id = models.IntegerField(null=False, default=0)
    # Domain arch string e.g. 275/UPI0004FEB881#29021:2-66~20422&29021&340&387:103-266#
    # domain_architectures = models.TextField(null=True)


class Structure(models.Model):
    accession = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=512)
    short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField(null=True)
    experiment_type = models.CharField(max_length=16)
    release_date = models.DateField()
    literature = JSONField(null=True)
    chains = JSONField(null=True)
    source_database = models.CharField(max_length=10, default="pdb", db_index=True)
    resolution = models.FloatField(null=True)
    #TODO add description


class Taxonomy(models.Model):
    accession = models.IntegerField(primary_key=True)
    scientific_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=512)
    lineage = models.CharField(max_length=512)
    parent = models.ForeignKey("Taxonomy", on_delete=models.SET_NULL, null=True, blank=True)
    rank = models.CharField(max_length=20)
    children = JSONField(null=True)
    left_number = models.IntegerField()
    right_number = models.IntegerField()


class Proteome(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    is_reference = models.CharField(max_length=1)
    strain = models.CharField(max_length=512)
    assembly = models.CharField(max_length=512)
    taxonomy = models.ForeignKey("Taxonomy", on_delete=models.SET_NULL, null=True, blank=True)


class Set(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    description = models.TextField()
    source_database = models.CharField(max_length=20, db_index=True)
    integrated = JSONField(null=True)
    relationships = JSONField(null=True)  # {nodes: [{accession:"", type: ""}], links:[source:"", target: ""]}
