from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer


class ProteinSerializer(ModelContentSerializer):

    @staticmethod
    def to_representation(instance):
        obj = {
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
        return obj

    class Meta:
        model = Protein
