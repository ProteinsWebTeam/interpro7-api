from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer
import webfront.serializers.interpro
from webfront.views.custom import SerializerDetail


class ProteinSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        if self.detail == SerializerDetail.ALL or self.detail == SerializerDetail.ENTRY_OVERVIEW:
            representation = self.to_full_representation(instance)

        if self.detail == SerializerDetail.ENTRY_OVERVIEW:
            representation["entries"] = self.to_entries_representation(instance)
        elif self.detail == SerializerDetail.ENTRY_PROTEIN:
            representation = self.to_full_representation(instance.protein)
            representation["entries"] = self.to_match_representation(instance)
        elif self.detail == SerializerDetail.ENTRY_PROTEIN_DETAIL:
            representation = self.to_full_representation(instance.protein)
            representation["entries"] = self.to_match_representation(instance, True)
        elif self.detail == SerializerDetail.HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def to_full_representation(self, instance):
        return {
            "metadata": self.to_metadata_representation(instance),
            "entries": self.to_entries_count_representation(instance),
            "representation": instance.feature,
            "structure": instance.structure,
            "genomicContext": instance.genomic_context,
            "source_database": instance.source_database
        }

    @staticmethod
    def to_headers_representation(instance):
        return {"accession": instance.accession}

    @staticmethod
    def to_metadata_representation(instance):
        return {
            "accession": instance.accession,
            "id": instance.identifier,
            "sourceOrganism": instance.organism,
            "name": {
                "full": instance.name,
                "short": instance.short_name,
                "other": instance.other_names
            },
            "description": instance.description,
            "length": instance.length,
            "sequence": instance.sequence,
            "proteome": instance.proteome,
            "gene": instance.gene,
            "go_terms": instance.go_terms,
            "proteinEvidence": 4,
            "source_database": instance.source_database
        }


    @staticmethod
    def to_match_representation(match, full=False):
        output = {
            "match_start": match.match_start,
            "match_end": match.match_end
        }
        if full:
            output["entry"] = webfront.serializers.interpro.EntrySerializer.to_metadata_representation(match.entry)
        else:
            output["accession"] = match.entry_id

        return output

    @staticmethod
    def to_entries_representation(instance):
        return [
            ProteinSerializer.to_match_representation(match)
            for match in instance.proteinentryfeature_set.all()
        ]

    @staticmethod
    def to_entries_count_representation(instance):
        return instance.proteinentryfeature_set.count()

    class Meta:
        model = Protein
