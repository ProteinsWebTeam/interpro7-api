from django.db import models
from jsonfield import JSONField


class Entry(models.Model):
    entry_id = models.CharField(max_length=10, null=True)
    accession = models.CharField(primary_key=True, max_length=19)
    type = models.CharField(max_length=14)
    name = models.TextField()
    short_name = models.CharField(max_length=30)
    other_names = JSONField(null=True)
    source_database = models.CharField(max_length=20, db_index=True)
    member_databases = JSONField(null=True)
    integrated = models.ForeignKey("Entry", null=True, blank=True)
    go_terms = JSONField(null=True)
    description = JSONField(null=True)
    wikipedia = models.TextField(null=True)
    literature = JSONField(null=True)
    # Array of the string representing the domain architecture
    hierarchy = JSONField(null=True)
    cross_references = JSONField(null=True)

class EntryAnnotation(models.Model):
    annotation_id = models.CharField(max_length=40, primary_key=True)
    accession = models.ForeignKey(Entry)
    type = models.CharField(max_length=20)
    value = models.BinaryField()
    mime_type = models.CharField(max_length=64)

class Protein(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    identifier = models.CharField(max_length=20, unique=True, null=False)
    organism = JSONField(null=True)
    name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField(null=True)
    description = JSONField(null=True)
    sequence = models.TextField(null=False)
    length = models.IntegerField(null=False)
    proteomes = JSONField(null=True)
    gene = models.CharField(max_length=20, null=False)
    go_terms = JSONField(null=True)
    evidence_code = models.IntegerField()
    feature = JSONField(null=True)
    genomic_context = JSONField(null=True)
    source_database = models.CharField(max_length=20, default="uniprot", db_index=True)
    residues = JSONField(null=True)
    structure = JSONField(default={})
    fragment = models.CharField(max_length=1, null=False)
    tax_id = models.IntegerField(null=False, default=0)
    # Domain arch string e.g. 275/UPI0004FEB881#29021:2-66~20422&29021&340&387:103-266#
    # domain_architectures = models.TextField(null=True)


class Structure(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    short_name = models.CharField(max_length=20, null=True)
    other_names = JSONField(null=True)
    experiment_type = models.CharField(max_length=30)
    release_date = models.DateField()
    authors = JSONField(null=True)
    chains = JSONField(null=True)
    source_database = models.CharField(max_length=20, default="pdb", db_index=True)
    #TODO add description


class Taxonomy(models.Model):
    accession = models.IntegerField(primary_key=True)
    scientific_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=512)
    lineage = models.CharField(max_length=512)
    parent = models.ForeignKey("Taxonomy", null=True, blank=True)
    rank = models.CharField(max_length=20)
    children = JSONField(null=True)
    left_number = models.IntegerField()
    right_number = models.IntegerField()


class Proteome(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    is_reference = models.BooleanField()
    strain = models.CharField(max_length=512)
    assembly = models.CharField(max_length=512)
    taxonomy = models.ForeignKey("Taxonomy", null=True, blank=True)


class Set(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    description = models.TextField()
    source_database = models.CharField(max_length=20, db_index=True)
    integrated = JSONField(null=True)
    relationships = JSONField(null=True)  # {nodes: [{accession:"", type: ""}], links:[source:"", target: ""]}
