from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail

class SetSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        # representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
        return representation

    def endpoint_representation(self, representation, instance):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        # elif detail == SerializerDetail.ORGANISM_TAXONOMY_PROTEOME:
        #     representation = self.to_full_representation(instance, True)
        # elif detail == SerializerDetail.ORGANISM_PROTEOME:
        #     representation = self.to_full_proteome_representation(instance)
        elif detail == SerializerDetail.SET_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.SET_HEADERS:
            representation = self.to_headers_representation(instance)
        # elif detail == SerializerDetail.ORGANISM_PROTEOME_HEADERS:
        #     representation = self.to_headers_proteome_representation(instance)
        # elif detail == SerializerDetail.ORGANISM_TAXONOMY_PROTEOME_HEADERS:
        #     representation = self.to_headers_representation(instance, True)
        return representation

    # def filter_representation(self, representation, instance, detail_filters, detail):
    #   s = self.searcher
    #     if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
    #         representation["entries"] = self.to_entries_count_representation(instance)
    #     if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
    #         representation["proteins"] = self.to_proteins_count_representation(instance)
    #     if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
    #         representation["structures"] = self.to_structures_count_representation(instance)
    #     if detail != SerializerDetail.ORGANISM_OVERVIEW:
    #         if SerializerDetail.ENTRY_DB in detail_filters or \
    #                 SerializerDetail.ENTRY_DETAIL in detail_filters:
    #             representation["entries"] = self.to_entries_detail_representation(
    #                 instance, s, self.get_searcher_query(instance)
    #             )
    #         if SerializerDetail.STRUCTURE_DB in detail_filters or \
    #                 SerializerDetail.STRUCTURE_DETAIL in detail_filters:
    #             representation["structures"] = self.to_structures_detail_representation(
    #                 instance, s, self.get_searcher_query(instance)
    #             )
    #         if SerializerDetail.PROTEIN_DB in detail_filters or \
    #                 SerializerDetail.PROTEIN_DETAIL in detail_filters:
    #             representation["proteins"] = self.to_proteins_detail_representation(
    #                 instance, self.searcher, self.get_searcher_query(instance),
    #                 include_chains=True, include_coordinates=False
    #             )
    #     return representation

    @staticmethod
    def to_counter_representation(instance):
        if "sets" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise ReferenceError('There are not structures for this request')
            instance = {
                "sets": {
                        SetSerializer.get_key_from_bucket(bucket): SetSerializer.serialize_counter_bucket(bucket, "sets")
                        for bucket in instance["databases"]["buckets"]
                }
            }
        return instance

    @staticmethod
    def to_full_representation(instance):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "description": instance.description,
                "integrated": instance.integrated,
                "relationships": instance.relationships,
            },
            "counters": {}
        }
        return obj

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
