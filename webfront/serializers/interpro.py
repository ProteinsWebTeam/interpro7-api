from webfront.models import Entry
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import SerializerDetail


class EntrySerializer(ModelContentSerializer):
    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filter)

        return representation

    @staticmethod
    def endpoint_representation(representation, instance, detail):
        if detail == SerializerDetail.ALL or detail == SerializerDetail.ENTRY_DETAIL:
            representation["metadata"] = EntrySerializer.to_metadata_representation(instance)

        # elif self.detail == SerializerDetail.PROTEIN_ENTRY_DETAIL:
        #     representation["metadata"] = self.to_metadata_representation(instance.entry)
        #     representation["proteins"] = self.to_proteins_detail_representation(instance.protein)
        elif detail == SerializerDetail.ENTRY_HEADERS:
            representation = EntrySerializer.to_headers_representation(instance)
            # representation["metadata"] = self.to_metadata_representation(instance.entry)
            # representation["proteins"] = [ProteinSerializer.to_metadata_representation(instance.protein)]
        return representation

    @staticmethod
    def filter_representation(representation, instance, detail_filter):
        if detail_filter == SerializerDetail.PROTEIN_OVERVIEW:
            representation["proteins"] = EntrySerializer.to_proteins_overview_representation(instance)
        elif detail_filter == SerializerDetail.PROTEIN_DETAIL:
            representation["proteins"] = EntrySerializer.to_proteins_detail_representation(instance)
        elif detail_filter == SerializerDetail.ENTRY_PROTEIN_HEADERS or \
                detail_filter == SerializerDetail.ENTRY_PROTEIN_DETAIL:
            representation["proteins"] = EntrySerializer.to_proteins_count_representation(instance)

        return representation

    @staticmethod
    def to_metadata_representation(instance):
        obj = {
            "accession": instance.accession,
            "entry_id": instance.entry_id,
            "type": instance.type,
            "go_terms": instance.go_terms,
            "source_database": instance.source_database,
            "member_databases": instance.member_databases,
            "integrated": instance.integrated,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                "other": instance.other_names,
            },
            "description": instance.description,
            "wikipedia": instance.wikipedia,
            "literature": instance.literature,
        }
        # Just showing the accesion number instead of recursively show the entry to which has been integrated
        if instance.integrated:
            obj["integrated"] = instance.integrated.accession
        return obj

    @staticmethod
    def to_proteins_count_representation(instance):
        return instance.proteinentryfeature_set.count()

    @staticmethod
    def to_proteins_overview_representation(instance):
        return [
            EntrySerializer.to_match_representation(match)
            for match in instance.proteinentryfeature_set.all()
            ]

    @staticmethod
    def to_match_representation(match, full=False):
        output = {
            "accession": match.protein_id,
            "match_start": match.match_start,
            "match_end": match.match_end,
            "length": match.protein.length,
            "source_database": match.protein.source_database,
            "name": match.protein.name,
        }
        if full:
            output["protein"] = ProteinSerializer.to_metadata_representation(match.protein)

        return output

    @staticmethod
    def to_proteins_detail_representation(instance):
        return [
            EntrySerializer.to_match_representation(match, True)
            for match in instance.proteinentryfeature_set.all()
            ]

    @staticmethod
    def to_headers_representation(instance):
        return {"accession": instance.accession}

    class Meta:
        model = Entry
