from webfront.models import Entry
from webfront.serializers.content_serializers import ModelContentSerializer


class EntrySerializer(ModelContentSerializer):
    content = "ALL"

    def to_representation(self, instance):
        representation = {}
        if self.content == "ALL":
            representation["metadata"] = self.to_metadata_representation(instance)
        return representation

    @staticmethod
    def to_metadata_representation(instance):
        return {
            'id': instance.id,
            'accession': instance.accession,
            'type': instance.type,
            'go_terms': instance.go_terms,
            'source_dataBase': instance.source_database,
            'member_databases': instance.member_databases,
            'integrated': instance.integrated,
            'name': {
                'name': instance.name,
                'short': instance.short_name,
                'other': instance.other_names
            },
            "description": instance.description,
            "wikipedia": instance.wikipedia,
            "literature": instance.literature
        }

    class Meta:
        model = Entry
