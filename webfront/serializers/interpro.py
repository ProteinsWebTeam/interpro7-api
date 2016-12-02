from webfront.models import Entry
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import SerializerDetail
import webfront.serializers.interpro


class EntrySerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters)

        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL or detail == SerializerDetail.ENTRY_DETAIL:
            representation["metadata"] = self.to_metadata_representation(instance)
        elif detail == SerializerDetail.ENTRY_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.ENTRY_HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def filter_representation(self, representation, instance, detail_filters):
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = EntrySerializer.to_proteins_count_representation(instance, self.solr)
        # if SerializerDetail.PROTEIN_DETAIL in detail_filters:
        #     representation["proteins"] = EntrySerializer.to_proteins_detail_representation(instance)
        # if SerializerDetail.ENTRY_PROTEIN_HEADERS in detail_filters:
        #     representation["proteins"] = EntrySerializer.to_proteins_count_representation(instance)
        # if SerializerDetail.STRUCTURE_HEADERS in detail_filters:
        #     representation["structures"] = EntrySerializer.to_structures_count_representation(instance)
        # if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
        #     representation["structures"] = EntrySerializer.to_structures_overview_representation(instance)
        # if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
        #     representation["structures"] = EntrySerializer.to_structures_overview_representation(instance, True)
        return representation

    def to_metadata_representation(self, instance):
        # results = SearchQuerySet().filter(entry_acc=instance.accession).facet("protein_acc")
        obj = {
            "accession": instance.accession,
            "entry_id": instance.entry_id,
            "type": instance.type,
            "go_terms": instance.go_terms,
            "source_database": instance.source_database,
            "member_databases": instance.member_databases,
            "integrated": instance.integrated,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                "other": instance.other_names,
            },
            "description": instance.description,
            "wikipedia": instance.wikipedia,
            "literature": instance.literature,
            "counters": {
                "proteins": self.solr.get_number_of_field_by_endpoint("entry", "protein_acc", instance.accession),
                "structures": self.solr.get_number_of_field_by_endpoint("entry", "structure_acc", instance.accession)
            }
        }
        # Just showing the accesion number instead of recursively show the entry to which has been integrated
        if instance.integrated:
            obj["integrated"] = instance.integrated.accession
        return obj
    #
    # @staticmethod
    # def to_proteins_count_representation(instance):
    #     return instance.proteinentryfeature_set.count()
    #
    # @staticmethod
    # def to_proteins_overview_representation(instance):
    #     return [
    #         EntrySerializer.to_match_representation(match)
    #         for match in instance.proteinentryfeature_set.all()
    #         ]
    #
    # @staticmethod
    # def to_match_representation(match, full=False):
    #     output = {
    #         "accession": match.protein_id,
    #         "coordinates": match.coordinates,
    #         "length": match.protein.length,
    #         "source_database": match.protein.source_database,
    #         "name": match.protein.name,
    #     }
    #     if full:
    #         output["protein"] = ProteinSerializer.to_metadata_representation(match.protein)
    #
    #     return output
    #
    # @staticmethod
    # def to_proteins_detail_representation(instance):
    #     return [
    #         EntrySerializer.to_match_representation(match, True)
    #         for match in instance.proteinentryfeature_set.all()
    #     ]

    def to_headers_representation(self, instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "type": instance.type
            }
        }

    @staticmethod
    def to_counter_representation(instance):
        if "entries" not in instance:
            if instance["count"] == 0:
                return {"entries": 0}
            result = {
                "entries": {
                    "member_databases": {
                        bucket["val"]: bucket["unique"]
                        for bucket in instance["databases"]["buckets"]
                    },
                    "unintegrated": 0,
                    "interpro": 0,
                }
            }
            if "unintegrated" in instance and instance["unintegrated"]["count"]>0:
                result["entries"]["unintegrated"] = instance["unintegrated"]["unique"]
            if "interpro" in result["entries"]["member_databases"]:
                result["entries"]["interpro"] = result["entries"]["member_databases"]["interpro"]
                del result["entries"]["member_databases"]["interpro"]
            return result
        return instance

    @staticmethod
    def to_proteins_count_representation(instance, solr):
        return webfront.serializers.interpro.ProteinSerializer.to_counter_representation(
            solr.get_counter_object("protein")
        )["proteins"]
    #
    # @staticmethod
    # def to_structures_count_representation(instance):
    #     return instance.structures.distinct().count()
    #
    # @staticmethod
    # def to_structure_representation(instance, full=False):
    #     from webfront.serializers.pdb import StructureSerializer
    #
    #     chain = {
    #         "chain": instance.chain,
    #         "accession": instance.structure.accession,
    #         "coordinates": instance.coordinates,
    #         "source_database": instance.structure.source_database,
    #     }
    #     if full:
    #         chain["structure"] = StructureSerializer.to_metadata_representation(instance.structure)
    #     return chain
    #
    # @staticmethod
    # def to_structures_overview_representation(instance, is_full=False):
    #     return [
    #         EntrySerializer.to_structure_representation(match, is_full)
    #         for match in instance.entrystructurefeature_set.all()
    #         ]

    class Meta:
        model = Entry
