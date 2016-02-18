from rest_framework import serializers

from webfront.models import interpro,DwEntrySignature, DwEntry
from webfront.serializers.content_serializers import ModelContentSerializer
from .utils import flat_to_nested
databases = {
    "l": "PfamClan",
    "I": "InterPro",
    "S": "UniProt/Swiss-Prot",
    "T": "UniProt/TrEMBL",
    "P": "PROSITE patterns",
    "M": "PROSITE profiles",
    "H": "Pfam",
    "F": "PRINTS",
    "D": "ProDom",
    "B": "Impala",
    "L": "Blocks",
    "p": "PROSITE doc",
    "e": "ENZYME",
    "R": "SMART",
    "N": "TIGRFAMs",
    "G": "GO Classification",
    "c": "CAZy",
    "Y": "SUPERFAMILY",
    "U": "PIRSF",
    "m": "MEROPS",
    "Z": "IUPHAR receptor code",
    "V": "PANTHER",
    "O": "COG",
    "y": "SCOP",
    "h": "CATH",
    "X": "GENE3D",
    "b": "PDB",
    "K": "COMe",
    "C": "PANDIT",
    "E": "MSDsite",
    "W": "SWISS-MODEL",
    "o": "OMIM",
    "A": "MODBASE",
    "a": "ADAN",
    "d": "DBD",
    "u": "UniProt",
    "Q": "HAMAP",
    "f": "PfamB",
    "J": "CDD",
    "i": "PRIAM",
    "k": "KEGG",
    "w": "UniPathway",
    "t": "MetaCyc",
    "r": "Reactome",
}

class CommonAnnotationSerializer(serializers.ModelSerializer):
    order_in = serializers.SerializerMethodField()

    def get_order_in(self, obj):
        return obj.entry2common_set.all().values()[0]['order_in']

    class Meta:
        model = interpro.CommonAnnotation
        fields = ('ann_id', 'name', 'text', 'comments', 'order_in')


class CvDatabaseSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = interpro.CvDatabase
        fields = ('dbcode', 'dbname', 'dborder', 'dbshort')


class CvEntryTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = interpro.CvEntryType
        fields = ('code', 'abbrev', 'description')


class CvIfcSerializer(serializers.ModelSerializer):

    class Meta:
        model = interpro.CvIfc
        fields = ('code', 'name')


class CvRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = interpro.CvRelation
        fields = ('code', 'abbrev', 'description', 'forward', 'reverse')


class Entry2CommonSerializer(serializers.ModelSerializer):
    order_in = serializers.SerializerMethodField()

    def get_order_in(self, obj):
        return obj.entry2common_set.values()

    class Meta:
        model = interpro.Entry2Common
        fields = ('order_in', )


class EntrySerializerFlat(serializers.ModelSerializer):

    class Meta:
        model = interpro.Entry
        fields = ('entry_ac', 'entry_type', 'name', 'checked', 'created', 'timestamp', 'userstamp', 'short_name')


class CitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = interpro.Citation
        fields = ('pub_id', 'pub_type', 'pubmed_id', 'isbn', 'volume', 'issue', 'year', 'title', 'url', 'rawpages', 'medline_journal', 'iso_journal', 'authors', 'doi_url')


class Entry2PubSerializer(serializers.ModelSerializer):
    pub = CitationSerializer()

    class Meta:
        model = interpro.Entry2Pub
        fields = ('entry_ac', 'order_in', 'pub')


class Entry2CompSerializer(serializers.ModelSerializer):
    entry2_ac = EntrySerializerFlat()
    relation = CvRelationSerializer()

    class Meta:
        model = interpro.Entry2Comp
        fields = ('entry2_ac', 'relation', 'timestamp', 'userstamp')


class Entry2EntrySerializer(serializers.ModelSerializer):
    parent_ac = EntrySerializerFlat()
    relation = CvRelationSerializer()

    class Meta:
        model = interpro.Entry2Entry
        fields = ('entry_ac', 'parent_ac', 'relation', 'timestamp', 'userstamp')


class Entry2IfcSerializer(serializers.ModelSerializer):
    code = CvIfcSerializer()

    class Meta:
        mode  = interpro.Entry2Ifc
        fields = ('entry_ac', 'code')


class MethodSerializer(serializers.ModelSerializer):
    dbcode = CvDatabaseSerializer()
    sig_type = CvEntryTypeSerializer()

    class Meta:
        model = interpro.Method
        fields = ('method_ac', 'name', 'dbcode', 'method_date', 'timestamp', 'userstamp', 'skip_flag', 'candidate', 'description', 'sig_type', 'abstract', 'abstract_long', 'deleted')


class CvEvidenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = interpro.CvEvidence
        fields = ('code', 'abbrev', 'description')


class Entry2MethodSerializer(serializers.ModelSerializer):
    method_ac = MethodSerializer()
    evidence = CvEvidenceSerializer()

    class Meta:
        model = interpro.Entry2Method
        fields = ('entry_ac', 'method_ac', 'evidence', 'timestamp', 'userstamp', 'ida')


class EntryAccpairSerializer(serializers.ModelSerializer):

    class Meta:
        model = interpro.EntryAccpair
        fields = ('entry_ac', 'secondary_ac', 'timestamp', 'userstamp')


class EntryXrefSerializer(serializers.ModelSerializer):
    dbcode = CvDatabaseSerializer()

    class Meta:
        model = interpro.EntryXref
        fields = ('entry_ac', 'dbcode', 'ac', 'name')


class ProteinSerializer(serializers.ModelSerializer):
    dbcode = CvDatabaseSerializer()

    class Meta:
        model = interpro.EntryXref
        fields = ('protein_ac', 'name', 'dbcode', 'crc64', 'len', 'timestamp', 'userstamp', 'fragment', 'struct_flag', 'tax_id')


class ExampleSerializer(serializers.ModelSerializer):
    protein_ac = ProteinSerializer()

    class Meta:
        model = interpro.Example
        fields = ('entry_ac', 'protein_ac')


class EntryDWSerializer(ModelContentSerializer):
    class Meta:
        model = DwEntry
        fields = ('entry_ac', 'entry_type', 'checked', 'name', 'short_name', 'annotation', 'pathways_and_interactions', 'proteins_matched', 'domain_organisations', 'structures', 'related_resources', 'citations')


class EntryOverviewSerializer(ModelContentSerializer):
    dbcode = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    @staticmethod
    def get_total(obj):
        return obj["total"]

    @staticmethod
    def get_dbcode(obj):
        return databases[obj["dbcode"]]

    class Meta:
        model = DwEntrySignature
        fields = ('dbcode', 'total')

