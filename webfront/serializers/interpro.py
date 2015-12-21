from rest_framework import serializers

from webfront.models import interpro
from .utils import flat_to_nested


class CommonAnnotationSerializer(serializers.ModelSerializer):
    order_in = serializers.SerializerMethodField()

    def get_order_in(self, obj):
        print(dir(obj.pk))
        return obj.entry2common_set.all().values()[0]['order_in']

    class Meta:
        model  = interpro.CommonAnnotation
        fields = ('ann_id', 'name', 'text', 'comments', 'order_in')


class CvDatabaseSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model  = interpro.CvDatabase
        fields = ('dbcode', 'dbname', 'dborder', 'dbshort')


class CvEntryTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model  = interpro.CvEntryType
        fields = ('code', 'abbrev', 'description')


class CvIfcSerializer(serializers.ModelSerializer):

    class Meta:
        model  = interpro.CvIfc
        fields = ('code', 'name')


class CvRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = interpro.CvRelation
        fields = ('code', 'abbrev', 'description', 'forward', 'reverse')


class Entry2CommonSerializer(serializers.ModelSerializer):
    #ann = CommonAnnotationSerializer()
    order_in = serializers.SerializerMethodField()

    def get_order_in(self, obj):
        print(dir(obj.entry2common_set))
        return obj.entry2common_set.values()

    class Meta:
        model  = interpro.Entry2Common
        #fields = ('entry_ac', 'order_in', 'ann')
        fields = ('order_in', )


class EntrySerializer(serializers.ModelSerializer):
    entry_type = CvEntryTypeSerializer()
    commons    = serializers.SerializerMethodField()
    comps      = serializers.SerializerMethodField()
    entries    = serializers.SerializerMethodField()
    ifcs       = serializers.SerializerMethodField()
    methods    = serializers.SerializerMethodField()
    citations  = serializers.SerializerMethodField()
    accpairs   = serializers.SerializerMethodField()
    xrefs      = serializers.SerializerMethodField()
    examples   = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        content = kwargs.pop('content', [])

        super(EntrySerializer, self).__init__(*args, **kwargs)
        for to_be_removed in set(self.Meta.optionals) - set(content):
            self.fields.pop(to_be_removed)

    def get_commons(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entry2common_set.order_by('order_in').values(
                'order_in', 'ann_id__ann_id',
                'ann_id__name', 'ann_id__text', 'ann_id__comments'
            )
        ]

    def get_comps(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entry2comp_set.values(
                'timestamp', 'userstamp', 'entry2_ac', 'entry2_ac__entry_type',
                'entry2_ac__entry_type__abbrev',
                'entry2_ac__entry_type__description', 'entry2_ac__name',
                'entry2_ac__checked', 'entry2_ac__created', 'entry2_ac__timestamp',
                'entry2_ac__userstamp', 'entry2_ac__short_name', 'relation',
                'relation__abbrev', 'relation__description', 'relation__forward',
                'relation__reverse'
            )
        ]

    def get_entries(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entry2entry_set.values(
                'timestamp', 'userstamp', 'parent_ac', 'parent_ac__entry_type',
                'parent_ac__entry_type__abbrev',
                'parent_ac__entry_type__description', 'parent_ac__name',
                'parent_ac__checked', 'parent_ac__created', 'parent_ac__timestamp',
                'parent_ac__userstamp', 'parent_ac__short_name', 'relation',
                'relation__abbrev', 'relation__description', 'relation__forward',
                'relation__reverse'
            )
        ]

    def get_ifcs(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entry2ifc_set.values(
                'code', 'code__name'
            )
        ]

    def get_methods(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entry2method_set.order_by('method_ac__dbcode__dborder').values(
                'timestamp', 'userstamp', 'ida', 'method_ac__method_ac', 'method_ac__name',
                'method_ac__dbcode__dbcode', 'method_ac__dbcode__dbname',
                'method_ac__dbcode__dborder', 'method_ac__dbcode__dbshort',
                'method_ac__method_date', 'method_ac__timestamp',
                'method_ac__userstamp', 'method_ac__skip_flag',
                'method_ac__candidate', 'method_ac__description',
                'method_ac__sig_type__code', 'method_ac__sig_type__abbrev',
                'method_ac__sig_type__description', 'method_ac__abstract',
                'method_ac__abstract_long', 'method_ac__deleted', 'evidence__code',
                'evidence__abbrev', 'evidence__description'
            )
        ]

    def get_citations(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entry2pub_set.order_by('order_in').values(
                'pub_id__pub_id', 'pub_id__pub_type', 'pub_id__pubmed_id', 'pub_id__isbn',
                'pub_id__volume', 'pub_id__issue', 'pub_id__year', 'pub_id__title',
                'pub_id__url', 'pub_id__rawpages', 'pub_id__medline_journal',
                'pub_id__iso_journal', 'pub_id__authors', 'pub_id__doi_url'
            )
        ]

    def get_accpairs(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entryaccpair_set.values(
                'secondary_ac', 'timestamp', 'userstamp'
            )
        ]

    def get_xrefs(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.entryxref_set.order_by('dbcode__dborder').values(
                'name', 'ac', 'dbcode__dbcode',
                'dbcode__dbname', 'dbcode__dborder', 'dbcode__dbshort'
            )
        ]

    def get_examples(self, obj):
        return [
            flat_to_nested(related) for related in
            obj.example_set.order_by('protein_ac__dbcode__dborder').values(
                'protein_ac', 'protein_ac__name', 'protein_ac__crc64',
                'protein_ac__len', 'protein_ac__timestamp',
                'protein_ac__userstamp', 'protein_ac__fragment',
                'protein_ac__struct_flag', 'protein_ac__tax_id',
                'protein_ac__dbcode', 'protein_ac__dbcode__dbname',
                'protein_ac__dbcode__dborder', 'protein_ac__dbcode__dbshort'
            )
        ]

    class Meta:
        model  = interpro.Entry
        fields = ('entry_ac', 'entry_type', 'name', 'checked', 'created', 'timestamp', 'userstamp', 'short_name', 'commons', 'comps', 'entries', 'ifcs', 'methods', 'citations', 'accpairs', 'xrefs', 'examples')
        optionals = ('commons', 'comps', 'entries', 'ifcs', 'methods', 'citations', 'accpairs', 'xrefs', 'examples')

# class EntrySerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = interpro.Entry
#         fields = ('entry_ac', 'entry_type', 'name', 'commons', 'comps', 'entries', 'ifcs')
#         depth = 1

class EntrySerializerFlat(serializers.ModelSerializer):

    class Meta:
        model  = interpro.Entry
        fields = ('entry_ac', 'entry_type', 'name', 'checked', 'created', 'timestamp', 'userstamp', 'short_name')


class CitationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = interpro.Citation
        fields = ('pub_id', 'pub_type', 'pubmed_id', 'isbn', 'volume', 'issue', 'year', 'title', 'url', 'rawpages', 'medline_journal', 'iso_journal', 'authors', 'doi_url')


class Entry2PubSerializer(serializers.ModelSerializer):
    pub = CitationSerializer()

    class Meta:
        model  = interpro.Entry2Pub
        fields = ('entry_ac', 'order_in', 'pub')


class Entry2CompSerializer(serializers.ModelSerializer):
    entry2_ac = EntrySerializerFlat()
    relation  = CvRelationSerializer()

    class Meta:
        model  = interpro.Entry2Comp
        fields = ('entry2_ac', 'relation', 'timestamp', 'userstamp')


class Entry2EntrySerializer(serializers.ModelSerializer):
    parent_ac = EntrySerializerFlat()
    relation  = CvRelationSerializer()

    class Meta:
        model  = interpro.Entry2Entry
        fields = ('entry_ac', 'parent_ac', 'relation', 'timestamp', 'userstamp')


class Entry2IfcSerializer(serializers.ModelSerializer):
    code = CvIfcSerializer()

    class Meta:
        model  = interpro.Entry2Ifc
        fields = ('entry_ac', 'code')


class MethodSerializer(serializers.ModelSerializer):
    dbcode   = CvDatabaseSerializer()
    sig_type = CvEntryTypeSerializer()

    class Meta:
        model  = interpro.Method
        fields = ('method_ac', 'name', 'dbcode', 'method_date', 'timestamp', 'userstamp', 'skip_flag', 'candidate', 'description', 'sig_type', 'abstract', 'abstract_long', 'deleted')


class CvEvidenceSerializer(serializers.ModelSerializer):

    class Meta:
        model  = interpro.CvEvidence
        fields = ('code', 'abbrev', 'description')


class Entry2MethodSerializer(serializers.ModelSerializer):
    method_ac = MethodSerializer()
    evidence  = CvEvidenceSerializer()

    class Meta:
        model  = interpro.Entry2Method
        fields = ('entry_ac', 'method_ac', 'evidence', 'timestamp', 'userstamp', 'ida')


class EntryAccpairSerializer(serializers.ModelSerializer):

    class Meta:
        model  = interpro.EntryAccpair
        fields = ('entry_ac', 'secondary_ac', 'timestamp', 'userstamp')


class EntryXrefSerializer(serializers.ModelSerializer):
    dbcode = CvDatabaseSerializer()

    class Meta:
        model  = interpro.EntryXref
        fields = ('entry_ac', 'dbcode', 'ac', 'name')


class ProteinSerializer(serializers.ModelSerializer):
    dbcode = CvDatabaseSerializer()

    class Meta:
        model  = interpro.EntryXref
        fields = ('protein_ac', 'name', 'dbcode', 'crc64', 'len', 'timestamp', 'userstamp', 'fragment', 'struct_flag', 'tax_id')


class ExampleSerializer(serializers.ModelSerializer):
    protein_ac = ProteinSerializer()

    class Meta:
        model  = interpro.Example
        fields = ('entry_ac', 'protein_ac')
