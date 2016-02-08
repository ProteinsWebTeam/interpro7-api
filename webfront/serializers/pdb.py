from webfront.models import DwEntryStructure
from webfront.serializers.content_serializers import ContentSerializer, ModelContentSerializer
from rest_framework import serializers


class StructureOverviewSerializer(ContentSerializer):
    pdb = serializers.SerializerMethodField()

    def get_pdb(self,obj):
        return obj

    class Meta:
        fields = {'pdb'}


class StructureSerializer(ModelContentSerializer):
    class Meta:
        fields = ('entry_structure_pk','entry_fk','xref_identifier','dbcode')
        model = DwEntryStructure
