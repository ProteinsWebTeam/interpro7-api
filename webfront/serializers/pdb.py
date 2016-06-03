from webfront.constants import get_queryset_type, QuerysetType
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import SerializerDetail


class StructureSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filter)

        return representation

    @staticmethod
    def endpoint_representation(representation, instance, detail):
        if detail == SerializerDetail.ALL:
            representation = StructureSerializer.to_full_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_HEADERS:
            representation = StructureSerializer.to_headers_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_CHAIN:
            representation = StructureSerializer.to_full_representation(instance.structure)
            representation["metadata"]["chains"] = {
                instance.chain: StructureSerializer.to_chain_representation(instance)}
        return representation

    @staticmethod
    def to_full_representation(instance):
        return {
            "metadata": StructureSerializer.to_metadata_representation(instance),
            # "entries": StructureSerializer.to_entries_count_representation(instance),
            # "representation": instance.feature,
            # "structure": instance.structure,
            # "genomicContext": instance.genomic_context,
            # "source_database": instance.source_database
        }

    @staticmethod
    def filter_representation(representation, instance, detail_filter):
        qs_type = get_queryset_type(instance)
        if detail_filter == SerializerDetail.PROTEIN_OVERVIEW:
            if qs_type == QuerysetType.STRUCTURE_PROTEIN:
                representation["proteins"] = [StructureSerializer.to_chain_representation(instance)]
            else:
                representation["proteins"] = StructureSerializer.to_proteins_overview_representation(instance)
        elif detail_filter == SerializerDetail.PROTEIN_DETAIL:
            if qs_type == QuerysetType.STRUCTURE:
                representation["proteins"] = StructureSerializer.to_proteins_overview_representation(instance, True)
            else:
                representation["proteins"] = StructureSerializer.to_proteins_detail_representation(instance)
        elif detail_filter == SerializerDetail.ENTRY_PROTEIN_HEADERS or \
                detail_filter == SerializerDetail.ENTRY_PROTEIN_DETAIL:
            if qs_type == QuerysetType.STRUCTURE_PROTEIN:
                representation["proteins"] = 1
            else:
                representation["proteins"] = StructureSerializer.to_proteins_count_representation(instance)

        return representation

    @staticmethod
    def to_headers_representation(instance):
        return {"accession": instance.accession}

    @staticmethod
    def to_metadata_representation(instance):
        return {
            "accession": instance.accession,
            "name": instance.name,
            "experiment_type": instance.experiment_type,
            "release_date": instance.release_date,
            "authors": instance.authors,
            "chains": instance.chains,
            "source_database": instance.source_database,
        }

    @staticmethod
    def to_proteins_count_representation(instance):
        return instance.proteins.distinct().count()

    @staticmethod
    def to_chain_representation(instance, full=False):
        chain = {
            "chain": instance.chain,
            "protein": instance.protein.accession,
            "source_database": instance.protein.source_database,
            "length": instance.length,
            "organism": instance.organism,
            "start_residue": instance.start_residue,
            "stop_residue": instance.stop_residue,
        }
        if full:
            chain["protein"] = ProteinSerializer.to_metadata_representation(instance.protein)
        return chain

    @staticmethod
    def to_proteins_overview_representation(instance, is_full=False):
        return [
                StructureSerializer.to_chain_representation(match, is_full)
                for match in instance.proteinstructurefeature_set.all()
                ]
    @staticmethod
    def to_proteins_detail_representation(instance):
        return [StructureSerializer.to_chain_representation(instance, True)]
