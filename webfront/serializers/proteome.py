from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Taxonomy, Proteome
import webfront.serializers.interpro
import webfront.serializers.uniprot
import webfront.serializers.pdb
from webfront.views.queryset_manager import escape


class ProteomeSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
        if self.queryset_manager.other_fields is not None:
            def counter_function():
                get_c = ProteomeSerializer.get_counters
                return get_c(
                    instance,
                    self.searcher,
                    self.queryset_manager.get_searcher_query()
                )
            representation = self.add_other_fields(
                representation,
                instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function}
            )
        return representation

    def endpoint_representation(self, representation, instance):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.PROTEOME_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.PROTEOME_HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        serializer2endpoint = {
            SerializerDetail.ENTRY_OVERVIEW: "entry",
            SerializerDetail.PROTEIN_OVERVIEW: "protein",
            SerializerDetail.STRUCTURE_OVERVIEW: "structure",
            SerializerDetail.TAXONOMY_OVERVIEW: "taxonomy",
            SerializerDetail.SET_OVERVIEW: "set",
        }
        query_searcher = "proteome_acc:" + escape(instance.accession).lower() if hasattr(instance, 'accession') else None
        for df in detail_filters:
            if df in serializer2endpoint:
                endpoint = serializer2endpoint[df]
                representation[self.plurals[endpoint]] = self.to_count_representation(endpoint, query_searcher)
        if detail != SerializerDetail.PROTEOME_OVERVIEW:
            sq = self.queryset_manager.get_searcher_query()
            if SerializerDetail.ENTRY_DB in detail_filters or \
                    SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = self.to_entries_detail_representation(
                    instance, self.searcher, query_searcher,
                    base_query=sq
                )
            if SerializerDetail.STRUCTURE_DB in detail_filters or \
                    SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = self.to_structures_detail_representation(
                    instance, self.searcher, query_searcher,
                    include_chain=True,
                    base_query=sq
                )
            if SerializerDetail.PROTEIN_DB in detail_filters or \
                    SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = self.to_proteins_detail_representation(
                    instance, self.searcher, query_searcher,
                    base_query=sq
                )
            if SerializerDetail.TAXONOMY_DB in detail_filters or \
                    SerializerDetail.TAXONOMY_DETAIL in detail_filters:
                representation["taxa"] = self.to_taxonomy_detail_representation(None,
                    self.searcher, query_searcher
                )
            if SerializerDetail.SET_DB in detail_filters or \
                    SerializerDetail.SET_DETAIL in detail_filters:
                representation["sets"] = self.to_set_detail_representation(
                    instance,
                    self.searcher,
                    query_searcher
                )
        return representation

    def to_full_representation(self, instance):
        searcher = self.searcher
        sq = self.queryset_manager.get_searcher_query()
        return {
            "metadata": {
                "accession": instance.accession,
                "name": {
                    "name": instance.name
                },
                "source_database": "uniprot",
                "is_reference": instance.is_reference,
                "strain": instance.strain,
                "assembly": instance.assembly,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None,
                "lineage": instance.taxonomy.lineage if instance.taxonomy is not None else None,
                "counters": ProteomeSerializer.get_counters(instance, searcher, sq)
            }
        }

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "is_reference": instance.is_reference,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None,
                "lineage": instance.taxonomy.lineage if instance.taxonomy is not None else None,
                "source_database": "uniprot",
            }
        }

    @staticmethod
    def get_counters(instance, searcher, sq):
        return {
            "entries": searcher.get_number_of_field_by_endpoint("proteome", "entry_acc", instance.accession, sq),
            "structures": searcher.get_number_of_field_by_endpoint("proteome", "structure_acc", instance.accession, sq),
            "proteins": searcher.get_number_of_field_by_endpoint("proteome", "protein_acc", instance.accession, sq),
            "taxa": searcher.get_number_of_field_by_endpoint("proteome", "tax_id", instance.accession, sq),
            "sets": searcher.get_number_of_field_by_endpoint("proteome", "set_acc", instance.accession, sq),
        }

    @staticmethod
    def to_counter_representation(instance):
        if "proteomes" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise ReferenceError('No proteomes found matching this request')
            instance = {
                "proteomes": {
                    "uniprot": ProteomeSerializer.serialize_counter_bucket(instance["databases"], "proteomes"),
                }
            }
        return instance

    @staticmethod
    def get_proteome_header_from_search_object(obj, include_chain=False):
        header = {
            "taxonomy": obj["tax_id"],
            "accession": obj["proteome_acc"],
            "lineage": obj["tax_lineage"],
            "source_database": "uniprot"
        }
        if include_chain:
            header["chain"] = obj["structure_chain_acc"]
        return header

    def to_count_representation(self, endpoint, query):
        return self.serializers[endpoint].to_counter_representation(
            self.searcher.get_counter_object(endpoint, query, self.get_extra_endpoints_to_count()),
            self.detail_filters
        )[self.plurals[endpoint]]

