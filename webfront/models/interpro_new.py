import gzip

from django.db import models
from jsonfield import JSONField

encoding = "utf-8"


class Database(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    name_long = models.CharField(max_length=100)
    description = models.TextField(null=True)
    version = models.CharField(max_length=100, null=True)
    release_date = models.DateTimeField(null=True)
    type = models.CharField(max_length=100)
    prev_version = models.CharField(max_length=100, null=True)
    prev_release_date = models.DateTimeField(null=True)


class Entry(models.Model):
    entry_id = models.CharField(max_length=10, null=True)
    accession = models.CharField(primary_key=True, max_length=25)
    type = models.CharField(max_length=50)
    name = models.TextField()
    short_name = models.CharField(max_length=100)
    # other_names = JSONField(null=True)
    source_database = models.CharField(max_length=100, db_index=True)
    member_databases = JSONField(null=True)
    integrated = models.ForeignKey(
        "Entry", on_delete=models.SET_NULL, null=True, blank=True
    )
    go_terms = JSONField(null=True)
    description = JSONField(null=True)
    llm_description = models.TextField()
    wikipedia = JSONField(null=True)
    literature = JSONField(null=True)
    hierarchy = JSONField(null=True)
    cross_references = JSONField(null=True)
    entry_date = models.DateTimeField(null=True)
    is_featured = models.BooleanField(default=False)
    overlaps_with = JSONField(default=[])
    is_public = models.BooleanField(default=False)
    deletion_date = models.DateTimeField(null=True)
    counts = JSONField(null=True)
    interactions = JSONField(null=True)
    pathways = JSONField(null=True)
    history = JSONField(null=True)
    details = JSONField(null=True)
    set_info = JSONField(null=True)


class EntryTaxa(models.Model):
    accession = models.OneToOneField(
        Entry, db_column="accession", primary_key=True, on_delete=models.CASCADE
    )
    tree = JSONField(null=True)

    class Meta:
        db_table = "webfront_entrytaxa"


class EntryAnnotation(models.Model):
    annotation_id = models.CharField(max_length=40, primary_key=True)
    accession = models.ForeignKey(
        Entry, db_column="accession", on_delete=models.SET_NULL, null=True
    )
    type = models.CharField(max_length=32)
    value = models.BinaryField()
    mime_type = models.CharField(max_length=32)
    num_sequences = models.IntegerField(null=True)


class Protein(models.Model):
    accession = models.CharField(max_length=15, primary_key=True)
    identifier = models.CharField(max_length=16, unique=True, null=False)
    organism = JSONField(null=True)
    name = models.CharField(max_length=20)
    description = JSONField(null=True)
    sequence_bin = models.BinaryField(db_column="sequence", null=True)
    length = models.IntegerField(null=False)
    proteome = models.CharField(max_length=20, null=True)
    gene = models.CharField(max_length=70, null=True)
    go_terms = JSONField(null=True)
    evidence_code = models.IntegerField()
    source_database = models.CharField(
        max_length=20, default="unreviewed", db_index=True
    )
    # residues = JSONField(null=True)
    # extra_features = JSONField(null=True)
    structure = JSONField(default={}, null=True)
    is_fragment = models.BooleanField(default=False)
    tax_id = models.CharField(max_length=20, null=False, default="")
    ida_id = models.CharField(max_length=40, null=True)
    ida = models.TextField(null=True)
    counts = JSONField(null=True)

    @property
    def sequence(self):
        if self.sequence_bin is not None:
            return gzip.decompress(self.sequence_bin).decode(encoding)
        else:
            return None


class ProteinExtraFeatures(models.Model):
    feature_id = models.IntegerField(primary_key=True)
    protein_acc = models.CharField(max_length=15)
    entry_acc = models.CharField(max_length=25)
    source_database = models.CharField(max_length=10)
    location_start = models.IntegerField()
    location_end = models.IntegerField()
    sequence_feature = models.CharField(max_length=35)

    class Meta:
        db_table = "webfront_proteinfeature"


class ProteinResidues(models.Model):
    residue_id = models.IntegerField(primary_key=True)
    protein_acc = models.CharField(max_length=15)
    entry_acc = models.CharField(max_length=25)
    entry_name = models.CharField(max_length=100)
    source_database = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    fragments = JSONField(null=True)

    class Meta:
        db_table = "webfront_proteinresidue"


class Structure(models.Model):
    accession = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=512)
    experiment_type = models.CharField(max_length=16)
    release_date = models.DateTimeField()
    literature = JSONField(null=True)
    chains = JSONField(null=True)
    source_database = models.CharField(max_length=10, default="pdb", db_index=True)
    resolution = models.FloatField(null=True)
    counts = JSONField(null=True)
    secondary_structures = JSONField(null=True)


class ChainSequence(models.Model):
    id = models.IntegerField(primary_key=True)
    structure = models.ForeignKey(
        "Structure", on_delete=models.SET_NULL, null=True, blank=True, db_column="structure_acc"
    )
    chain = models.CharField(db_column="chain_acc", max_length=10)
    sequence_bin = models.BinaryField(db_column="sequence", null=True)
    length = models.IntegerField(null=False)

    @property
    def sequence(self):
        if self.sequence_bin is not None:
            return gzip.decompress(self.sequence_bin).decode(encoding)
        else:
            return None

    class Meta:
        db_table = "webfront_chain_sequence"


class Taxonomy(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    scientific_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=512)
    lineage = models.CharField(max_length=512)
    parent = models.ForeignKey(
        "Taxonomy", on_delete=models.SET_NULL, null=True, blank=True
    )
    rank = models.CharField(max_length=20)
    children = JSONField(null=True)
    counts = JSONField(null=True)


class TaxonomyPerEntry(models.Model):
    taxonomy = models.ForeignKey(
        "Taxonomy", on_delete=models.SET_NULL, null=True, blank=True, db_column="tax_id"
    )
    entry_acc = models.ForeignKey(
        "Entry", db_column="entry_acc", on_delete=models.SET_NULL, null=True
    )
    counts = JSONField(null=True)


class TaxonomyPerEntryDB(models.Model):
    taxonomy = models.ForeignKey(
        "Taxonomy", on_delete=models.SET_NULL, null=True, blank=True, db_column="tax_id"
    )
    source_database = models.CharField(max_length=100, db_index=True)
    counts = JSONField(null=True)


class Proteome(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    is_reference = models.BooleanField(default=False)
    strain = models.CharField(max_length=512)
    assembly = models.CharField(max_length=512)
    taxonomy = models.ForeignKey(
        "Taxonomy", on_delete=models.SET_NULL, null=True, blank=True
    )
    counts = JSONField(null=True)


class Set(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=512)
    description = models.TextField()
    source_database = models.CharField(max_length=20, db_index=True)
    relationships = JSONField(null=True)
    counts = JSONField(null=True)
    authors = JSONField(null=True)
    literature = JSONField(null=True)


class Release_Note(models.Model):
    version = models.CharField(max_length=20, primary_key=True)
    release_date = models.DateTimeField(null=True)
    content = JSONField(null=True)


class Alignment(models.Model):
    class Meta:
        ordering = ["set_acc", "entry_acc"]

    set_acc = models.ForeignKey(
        "Set", db_column="set_acc", on_delete=models.SET_NULL, null=True
    )
    entry_acc = models.ForeignKey(
        "Entry", db_column="entry_acc", on_delete=models.SET_NULL, null=True
    )
    target_acc = models.ForeignKey(
        "Entry",
        db_column="target_acc",
        on_delete=models.SET_NULL,
        null=True,
        related_name="target_acc",
    )
    target_set_acc = models.ForeignKey(
        "Set",
        db_column="target_set_acc",
        on_delete=models.SET_NULL,
        null=True,
        related_name="target_set_acc",
    )
    score = models.FloatField(null=True)
    seq_length = models.IntegerField(null=True)
    domains = JSONField(null=True)


class Isoforms(models.Model):
    accession = models.CharField(max_length=20, primary_key=True)
    protein_acc = models.CharField(max_length=20)
    length = models.IntegerField(null=False)
    sequence = models.TextField(null=False)
    features = JSONField(null=True)

    class Meta:
        db_table = "webfront_varsplic"


class StructuralModel(models.Model):
    model_id = models.IntegerField(primary_key=True)
    accession = models.CharField(max_length=25, null=False)
    algorithm = models.CharField(max_length=20, null=False)
    contacts = models.BinaryField(null=False)
    plddt = models.BinaryField(null=False)
    structure = models.BinaryField(null=False)

    class Meta:
        db_table = "webfront_structuralmodel"
