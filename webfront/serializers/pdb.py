from webfront.constants import get_queryset_type, QuerysetType
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Structure
import webfront.serializers.uniprot
import webfront.serializers.interpro


class StructureSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters)
        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_CHAIN:
            representation = self.to_full_representation(instance)
            representation["metadata"]["chains"] = self.to_chains_representation(
                self.solr.get_chain()
            )
            # {
            #     chain.chain: StructureSerializer.to_chain_representation(chain)
            #     for chain in instance.proteinstructurefeature_set.all()}
        return representation

    def to_full_representation(self, instance):
        return {
            "metadata": self.to_metadata_representation(instance),
        }

    def filter_representation(self, representation, instance, detail_filters):
        # qs_type = get_queryset_type(instance)
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = StructureSerializer.to_proteins_count_representation(representation, self.solr)
        # if SerializerDetail.PROTEIN_DETAIL in detail_filters:
        #     representation["proteins"] = StructureSerializer.to_proteins_overview_representation(instance, True)
        # if SerializerDetail.ENTRY_PROTEIN_HEADERS in detail_filters:
        #     representation["proteins"] = StructureSerializer.to_proteins_count_representation(instance)
        # if SerializerDetail.ENTRY_DETAIL in detail_filters:
        #     if qs_type == QuerysetType.STRUCTURE:
        #         representation["entries"] = StructureSerializer.to_entries_overview_representation(instance, True)
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = StructureSerializer.to_entries_count_representation(representation, self.solr)

        # if SerializerDetail.ENTRY_MATCH in detail_filters:
        #     representation["entries"] = StructureSerializer.to_entries_overview_representation(instance)

        return representation

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database
            }
        }

    def to_metadata_representation(self, instance):
        return {
            "accession": instance.accession,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                "other": instance.other_names,
            },
            "experiment_type": instance.experiment_type,
            "release_date": instance.release_date,
            "authors": instance.authors,
            "chains": instance.chains,
            "source_database": instance.source_database,
            "counters": {
                "entries": self.solr.get_number_of_field_by_endpoint("structure", "entry_acc", instance.accession),
                "proteins": self.solr.get_number_of_field_by_endpoint("structure", "protein_acc", instance.accession),
            }
        }

    @staticmethod
    def get_solr_from_representation(representation):
        solr_query = None
        if "metadata" in representation:
            solr_query = "structure_acc:" + representation["metadata"]["accession"]
            if "chains" in representation["metadata"] and len(representation["metadata"]["chains"]) == 1:
                solr_query += " AND chain:" + list(representation["metadata"]["chains"].keys())[0]
        return solr_query

    @staticmethod
    def to_proteins_count_representation(representation, solr):
        solr_query = StructureSerializer.get_solr_from_representation(representation)
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            solr.get_counter_object("protein", solr_query)
        )["proteins"]

    @staticmethod
    def to_entries_count_representation(representation, solr):
        solr_query = StructureSerializer.get_solr_from_representation(representation)
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            solr.get_counter_object("entry", solr_query)
        )["entries"]

    # @staticmethod
    # def to_chain_representation(instance, full=False):
    #     chain = {
    #         "chain": instance.chain,
    #         "accession": instance.protein.accession,
    #         "source_database": instance.protein.source_database,
    #         "length": instance.length,
    #         "organism": instance.organism,
    #         "coordinates": instance.coordinates,
    #     }
    #     if full:
    #         chain["protein"] = ProteinSerializer.to_metadata_representation(instance.protein)
    #     return chain
    #
    # @staticmethod
    # def to_proteins_overview_representation(instance, is_full=False):
    #     return [
    #             StructureSerializer.to_chain_representation(match, is_full)
    #             for match in instance.proteinstructurefeature_set.all()
    #             ]
    #
    # # @staticmethod
    # # def to_proteins_detail_representation(instance):
    # #     return [StructureSerializer.to_chain_representation(instance, True)]
    #
    # @staticmethod
    # def to_entries_count_representation(instance):
    #     return instance.entrystructurefeature_set.values("entry").distinct().count()
    #
    # @staticmethod
    # def to_entry_representation(instance, full=False):
    #     from webfront.serializers.interpro import EntrySerializer
    #
    #     chain = {
    #         "chain": instance.chain,
    #         "accession": instance.entry.accession,
    #         "source_database": instance.entry.source_database,
    #         "coordinates": instance.coordinates,
    #     }
    #     if instance.entry.integrated is not None:
    #         chain["integrated"] = instance.entry.integrated.accession,
    #     if full:
    #         chain["entry"] = EntrySerializer.to_metadata_representation(instance.entry)
    #     return chain
    #
    # @staticmethod
    # def to_entries_overview_representation(instance, is_full=False):
    #     return [
    #         StructureSerializer.to_entry_representation(match, is_full)
    #         for match in instance.entrystructurefeature_set.all()
    #         ]

    # TODO: Missing the length
    def to_chains_representation(self, chains):
        if len(chains) < 1:
            raise ValueError('Trying to display an empty list of chains')
        return {ch["chain"]: {
            "coordinates": ch["protein_structure_coordinates"],
            "organism": {
                "taxid": ch["tax_id"]
            },
            "accession": ch["protein_acc"],
            "chain": ch["chain"],
            "source_database": ch["protein_db"]
        } for ch in chains}

    @staticmethod
    def to_counter_representation(instance):
        if "structures" not in instance:
            if instance["ngroups"] == 0:
                raise ReferenceError('There are not structures for this request')
            instance = {"structures": {
                            "pdb": instance["ngroups"]
                        }}
        return instance

    class Meta:
        model = Structure
