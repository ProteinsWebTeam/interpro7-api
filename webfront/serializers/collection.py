from webfront.serializers.content_serializers import ModelContentSerializer
import webfront.serializers.interpro
import webfront.serializers.uniprot
import webfront.serializers.pdb
import webfront.serializers.taxonomy

from webfront.views.custom import SerializerDetail
from webfront.views.queryset_manager import escape


class SetSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
        if self.queryset_manager.other_fields is not None:
            def counter_function():
                return SetSerializer.get_counters(
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
        elif detail == SerializerDetail.SET_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.SET_HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        s = self.searcher
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(instance)
        if SerializerDetail.TAXONOMY_OVERVIEW in detail_filters:
            representation["taxa"] = self.to_taxonomy_count_representation(instance)
        if SerializerDetail.PROTEOME_OVERVIEW in detail_filters:
            representation["proteomes"] = self.to_proteome_count_representation(instance)
        if detail != SerializerDetail.SET_OVERVIEW:
            q = "set_acc:" + escape(instance.accession.lower())
            sq = self.queryset_manager.get_searcher_query()
            if SerializerDetail.ENTRY_DB in detail_filters or \
                    SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = self.to_entries_detail_representation(instance, s, q, base_query=sq)
            if SerializerDetail.STRUCTURE_DB in detail_filters or \
                    SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = self.to_structures_detail_representation(
                    instance, s, q,
                    include_chain=True,
                    base_query=sq
                )
            if SerializerDetail.PROTEIN_DB in detail_filters or \
                    SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = self.to_proteins_detail_representation(
                    instance, self.searcher, q, base_query=sq
                )
            if SerializerDetail.TAXONOMY_DB in detail_filters or \
                    SerializerDetail.TAXONOMY_DETAIL in detail_filters:
                representation["taxa"] = self.to_taxonomy_detail_representation(
                    instance, self.searcher, q
                )
            if SerializerDetail.PROTEOME_DB in detail_filters or \
                    SerializerDetail.PROTEOME_DETAIL in detail_filters:
                representation["proteomes"] = self.to_proteomes_detail_representation(
                    self.searcher, q
                )
        return representation

    @staticmethod
    def to_counter_representation(instance, filters=None):
        if "sets" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0) or \
               ("buckets" in instance["databases"] and len(instance["databases"]["buckets"]) == 0) :
                raise ReferenceError('There are not sets for this request')
            ins2 = {
                "sets": {
                        SetSerializer.get_key_from_bucket(bucket): SetSerializer.serialize_counter_bucket(bucket, "sets")
                        for bucket in instance["databases"]["buckets"]
                }
            }
            ins2["sets"]["all"] = SetSerializer.serialize_counter_bucket(
                instance["all"], "sets"
            )
            instance = ins2
            # instance["sets"]["all"] = sum(instance["sets"].values())
        return instance

    def to_full_representation(self, instance):
        searcher = self.searcher
        sq = self.queryset_manager.get_searcher_query()
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": {
                    "name": instance.name,
                },
                "source_database": instance.source_database,
                "description": instance.description,
                "integrated": instance.integrated,
                "relationships": instance.relationships,
                "counters": SetSerializer.get_counters(instance, searcher, sq)
            },
        }
        return obj

    @staticmethod
    def get_counters(instance, searcher, sq):
        return {
            "entries": searcher.get_number_of_field_by_endpoint("set", "entry_acc", instance.accession, sq),
            "structures": searcher.get_number_of_field_by_endpoint("set", "structure_acc", instance.accession, sq),
            "proteins": searcher.get_number_of_field_by_endpoint("set", "protein_acc", instance.accession, sq),
            "taxa": searcher.get_number_of_field_by_endpoint("set", "tax_id", instance.accession, sq),
            "proteomes": searcher.get_number_of_field_by_endpoint("set", "proteome_acc", instance.accession, sq),
        }

    @staticmethod
    def to_headers_representation(instance):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
            }
        }
        return obj

    def to_entries_count_representation(self, instance):
        query = "set_acc:" + escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object("entry", query, self.get_extra_endpoints_to_count()),
            self.detail_filters
        )["entries"]

    def to_proteins_count_representation(self, instance):
        query = "set_acc:" + escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.searcher.get_counter_object("protein", query, self.get_extra_endpoints_to_count())
        )["proteins"]

    def to_structures_count_representation(self, instance):
        query = "set_acc:" + escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object("structure", query, self.get_extra_endpoints_to_count())
        )["structures"]

    def to_taxonomy_count_representation(self, instance):
        query = "set_acc:" + escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.taxonomy.TaxonomySerializer.to_counter_representation(
            self.searcher.get_counter_object("taxonomy", query, self.get_extra_endpoints_to_count())
        )["taxa"]

    def to_proteome_count_representation(self, instance):
        query = "set_acc:" + escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.proteome.ProteomeSerializer.to_counter_representation(
            self.searcher.get_counter_object("proteome", query, self.get_extra_endpoints_to_count())
        )["proteomes"]

    @staticmethod
    def get_set_from_search_object(obj, include_chain=False):
        header = {
            "accession": obj["set_acc"],
            "source_database": obj["set_db"],
        }
        if "set_integrated" in obj:
            header["integrated"] = obj["set_integrated"]
        if include_chain:
            header["chain"] = obj["chain"]
        return header
