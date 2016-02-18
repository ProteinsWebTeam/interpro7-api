from rest_framework import serializers
from webfront.models import DwEntryProteinsMatched

from webfront.serializers.content_serializers import ModelContentSerializer,ContentSerializer


class ProteinSerializer(ModelContentSerializer):

    class Meta:
        model = DwEntryProteinsMatched
        fields = ('protein_ac', 'entry_fk', 'dbid', 'xref_fk', 'protein_ac', 'description', 'tax_id', 'taxonomy_full_name', 'len', 'struct_flag', 'ida', 'ida_fk', 'materialised_path', 'seq_fk', 'entry_list')


class ProteinOverviewSerializer(ContentSerializer):
    uniprot = serializers.SerializerMethodField()

    def get_uniprot(self,obj):
        return obj

    class Meta:
        fields = {'uniprot'}