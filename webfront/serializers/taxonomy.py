from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Taxonomy

class OrganismSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(representation, instance)
        return representation

    def endpoint_representation(self, representation, instance):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.ORGANISM_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.ORGANISM_HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def filter_representation(self, representation, instance):
        return representation

    @staticmethod
    def to_full_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "scientific_name": instance.scientific_name,
                "full_name": instance.full_name,
                "lineage": instance.lineage,
                "rank": instance.rank,
                "children": instance.children,
                "parent": instance.parent.accession if instance.parent is not None else None
            }
        }

    @staticmethod
    def to_counter_representation(instance):
        if "taxonomy" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise ReferenceError('There are not structures for this request')
            # instance = {
            #     "structures": {
            #         "pdb": StructureSerializer.serialize_counter_bucket(instance["databases"])
            #     }
            # }
        return instance

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "full_name": instance.full_name,
                "children": instance.children,
                "parent": instance.parent.accession if instance.parent is not None else None
            }
        }
