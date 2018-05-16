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
        # representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
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
        # elif detail == SerializerDetail.ORGANISM_TAXONOMY_PROTEOME:
        #     representation = self.to_full_representation(instance, True)
        # elif detail == SerializerDetail.ORGANISM_PROTEOME:
        #     representation = self.to_full_proteome_representation(instance)
        elif detail == SerializerDetail.TAXONOMY_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.TAXONOMY_HEADERS:
            representation = self.to_headers_representation(instance)
        # elif detail == SerializerDetail.ORGANISM_PROTEOME_HEADERS:
        #     representation = self.to_headers_proteome_representation(instance)
        # elif detail == SerializerDetail.ORGANISM_TAXONOMY_PROTEOME_HEADERS:
        #     representation = self.to_headers_representation(instance, True)
        elif detail == SerializerDetail.TAXONOMY_DETAIL_NAMES:
            representation = self.to_full_representation(instance)
            representation["names"] = self.get_names_map(instance)
        return representation



    # @staticmethod
    # def serialize_counter_bucket(bucket, plural):
    #     output = {
    #         "taxonomy": bucket["unique"],
    #         "proteome": bucket["proteomes"]
    #     }
    #     is_searcher = True
    #     if isinstance(output["taxonomy"], dict):
    #         output["taxonomy"] = output["taxonomy"]["value"]
    #         output["proteome"] = output["proteome"]["value"]
    #         is_searcher = False
    #     if "entry" in bucket or "protein" in bucket or "structure" in bucket or "set" in bucket:
    #         output = {
    #             "taxonomy": {"organisms": output["taxonomy"]},
    #             "proteome": {"organisms": output["proteome"]},
    #         }
    #         # output = {"organisms": output}
    #         if "entry" in bucket:
    #             output["taxonomy"]["entries"] = bucket["entry"] if is_searcher else bucket["entry"]["value"]
    #             output["proteome"]["entries"] = bucket["entry"] if is_searcher else bucket["entry"]["value"]
    #         if "protein" in bucket:
    #             output["taxonomy"]["proteins"] = bucket["protein"] if is_searcher else bucket["protein"]["value"]
    #             output["proteome"]["proteins"] = bucket["protein"] if is_searcher else bucket["protein"]["value"]
    #         if "structure" in bucket:
    #             output["taxonomy"]["structures"] = bucket["structure"] if is_searcher else bucket["structure"]["value"]
    #             output["proteome"]["structures"] = bucket["structure"] if is_searcher else bucket["structure"]["value"]
    #         if "set" in bucket:
    #             output["taxonomy"]["sets"] = bucket["set"] if is_searcher else bucket["set"]["value"]
    #             output["proteome"]["sets"] = bucket["set"] if is_searcher else bucket["set"]["value"]
    #     return output

    def to_full_representation(self, instance):
        searcher = self.searcher
        sq = self.queryset_manager.get_searcher_query()
        return {
            "metadata": {
                "accession": instance.accession,
                "name": {
                    "name": instance.name
                },
                "source_database": "proteome",
                "is_reference": instance.is_reference,
                "strain": instance.strain,
                "assembly": instance.assembly,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None,
                "counters": ProteomeSerializer.get_proteome_counters(instance, searcher, sq)
            }
        }


    def isChildInQuery(self):
        query = self.queryset_manager.get_searcher_query()

        def filter_children(child):
            q = "{} && lineage:{}".format(query, child)
            response = self.searcher._elastic_json_query(q, {"size": 0})
            return response["hits"]["total"] > 0
        return filter_children

    def get_children(self, instance):
        filter_children = lambda x: True
        if len(self.detail_filters) > 0:
            filter_children = self.isChildInQuery()
        return [str(c)for c in instance.children if filter_children(c)]

    @staticmethod
    def to_headers_representation(instance):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.full_name,
                "children": instance.children,
                "parent": instance.parent.accession if instance.parent is not None else None,
                "source_database": "taxonomy"
            }
        }
        return obj
    @staticmethod
    def get_counters(instance, searcher, sq):
        return {
            "entries": searcher.get_number_of_field_by_endpoint("proteome", "entry_acc", instance.accession, sq),
            "structures": searcher.get_number_of_field_by_endpoint("proteome", "structure_acc", instance.accession, sq),
            "proteins": searcher.get_number_of_field_by_endpoint("proteome", "protein_acc", instance.accession, sq),
            "sets": searcher.get_number_of_field_by_endpoint("proteome", "set_acc", instance.accession, sq),
        }
