from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail


class ProteinSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        if self.detail == SerializerDetail.ALL:
            representation = self.to_metadata_representation(instance)
            representation["entries"] = self.to_entries_representation(instance)
        if self.detail == SerializerDetail.HEADERS:
            return self.to_headers_representation(instance)
        return representation

    @staticmethod
    def to_headers_representation(instance):
        return {"accession": instance.accession}

    @staticmethod
    def to_metadata_representation(instance):
        return {
            "metadata": {
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
                "proteinEvidence": 4
            },
            "representation": instance.feature,
            "structure": instance.structure,
            "genomicContext": instance.genomic_context,
            "source_database": instance.source_database
        }

    @staticmethod
    def to_entries_representation(instance):
        return [
            {
                "accession": match.entry_id,
                "match_start": match.match_start,
                "match_end": match.match_end
            }
            for match in instance.proteinentryfeature_set.all()
        ]

    class Meta:
        model = Protein
