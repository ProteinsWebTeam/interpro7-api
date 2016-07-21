from webfront.constants import get_queryset_type, QuerysetType
from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer
import webfront.serializers.interpro
from webfront.views.custom import SerializerDetail


class ProteinSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filter)

        return representation

    @staticmethod
    def endpoint_representation(representation, instance, detail):
        if detail == SerializerDetail.ALL:
            representation = ProteinSerializer.to_full_representation(instance)
        # if self.detail == SerializerDetail.ENTRY_PROTEIN:
        #     representation = self.to_full_representation(instance.protein)
        #     representation["entries"] = [self.to_match_representation(instance)]
        # el
        elif detail == SerializerDetail.PROTEIN_HEADERS:
            representation = ProteinSerializer.to_headers_representation(instance)
        return representation

    @staticmethod
    def filter_representation(representation, instance, detail_filter):
        qs_type = get_queryset_type(instance)
        if detail_filter == SerializerDetail.ENTRY_OVERVIEW:
            representation["entries"] = ProteinSerializer.to_entries_count_representation(instance)
        elif detail_filter == SerializerDetail.ENTRY_MATCH:
            representation = ProteinSerializer.to_match_representation(instance, False)
        elif detail_filter == SerializerDetail.ENTRY_DETAIL:
            representation = ProteinSerializer.to_match_representation(instance, True)
        # elif detail_filter == SerializerDetail.STRUCTURE_HEADERS:
        #     representation["structures"] = ProteinSerializer.to_structures_count_representation(instance)
        elif detail_filter == SerializerDetail.STRUCTURE_OVERVIEW:
            representation["structures"] = ProteinSerializer.to_structures_overview_representation(instance)
        elif detail_filter == SerializerDetail.STRUCTURE_DETAIL:
            if qs_type == QuerysetType.PROTEIN:
                representation["structures"] = ProteinSerializer.to_structures_overview_representation(instance, True)
        return representation

    @staticmethod
    def to_full_representation(instance):
        return {
            "metadata": ProteinSerializer.to_metadata_representation(instance),
            "representation": instance.feature,
            "genomic_context": instance.genomic_context,
            # "source_database": instance.source_database
        }

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "length": instance.length
            }
        }

    @staticmethod
    def to_metadata_representation(instance):
        return {
            "accession": instance.accession,
            "id": instance.identifier,
            "source_organism": instance.organism,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                "other": instance.other_names,
            },
            "description": instance.description,
            "length": instance.length,
            "sequence": instance.sequence,
            "proteome": instance.proteome,
            "gene": instance.gene,
            "go_terms": instance.go_terms,
            "protein_evidence": 4,
            "source_database": instance.source_database,
            "counters": {
                "entries": instance.proteinentryfeature_set.count(),
                "structures": instance.structures.distinct().count(),
            }
        }

    @staticmethod
    def to_match_representation(match, full=False):
        output = {
            "coordinates": match.coordinates,
            "accession": match.entry_id,
            "source_database": match.entry.source_database,
            "name": match.entry.name,
        }
        if full:
            output["entry"] = webfront.serializers.interpro.EntrySerializer.to_metadata_representation(match.entry)

        return output

    # @staticmethod
    # def to_entries_representation(instance):
    #     return [
    #         ProteinSerializer.to_match_representation(match)
    #         for match in instance.proteinentryfeature_set.all()
    #     ]

    @staticmethod
    def to_entries_count_representation(instance):
        return instance.proteinentryfeature_set.count()
    #
    # @staticmethod
    # def to_structures_count_representation(instance):
    #     return instance.structures.distinct().count()

    @staticmethod
    def to_chain_representation(instance, full=False):
        from webfront.serializers.pdb import StructureSerializer

        chain = {
            "chain": instance.chain,
            "structure": instance.structure.accession,
            "source_database": instance.structure.source_database,
            "length": instance.length,
            "organism": instance.organism,
            "coordinates": instance.coordinates,
        }
        if full:
            chain["structure"] = StructureSerializer.to_metadata_representation(instance.structure)
        return chain

    @staticmethod
    def to_structures_overview_representation(instance, is_full=False):
        return [
            ProteinSerializer.to_chain_representation(match, is_full)
            for match in instance.proteinstructurefeature_set.all()
            ]

    class Meta:
        model = Protein
