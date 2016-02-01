from rest_framework import serializers

from webfront.models import Protein, Entry
from webfront.serializers.content_serializers import ModelContentSerializer,ContentSerializer


class ProteinSerializer(ModelContentSerializer):

    class Meta:
        model = Protein
        fields = ('protein_ac', 'name', 'dbcode', 'crc64', 'len', 'timestamp', 'userstamp', 'fragment', 'struct_flag', 'tax_id')


class EntryProteinSerializer(ModelContentSerializer):
    proteins = serializers.SerializerMethodField()

    def get_proteins(self, entry):
        Protein.objects.filter()
        serializer = ProteinSerializer(many=True)
        return serializer.data

    class Meta:
        model = Entry
        fields = ('entry_ac','proteins')


class ProteinOverviewSerializer(ContentSerializer):
    uniprot = serializers.SerializerMethodField()

    def get_uniprot(self,obj):
        return obj

    class Meta:
        fields = {'uniprot'}