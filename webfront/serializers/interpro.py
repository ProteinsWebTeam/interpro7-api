from webfront.models import Entry
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
import webfront.serializers.uniprot
import webfront.serializers.pdb


class EntrySerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)

        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL or detail == SerializerDetail.ENTRY_DETAIL:
            representation["metadata"] = self.to_metadata_representation(instance, self.solr)
        elif detail == SerializerDetail.ENTRY_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.ENTRY_HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(instance)
        # if SerializerDetail.ENTRY_PROTEIN_HEADERS in detail_filters:
        #     representation["proteins"] = EntrySerializer.to_proteins_count_representation(instance)
        # if SerializerDetail.STRUCTURE_HEADERS in detail_filters:
        #     representation["structures"] = EntrySerializer.to_structures_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        # if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
        #     representation["structures"] = EntrySerializer.to_structures_overview_representation(instance, True)

        if detail != SerializerDetail.ENTRY_OVERVIEW:
            if SerializerDetail.PROTEIN_DB in detail_filters:
                representation["proteins"] = EntrySerializer.to_proteins_detail_representation(instance, self.solr)
            if SerializerDetail.STRUCTURE_DB in detail_filters:
                representation["structures"] = EntrySerializer.to_structures_detail_representation(instance, self.solr)
            if SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = EntrySerializer.to_proteins_detail_representation(instance, self.solr, True)
            if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = EntrySerializer.to_structures_detail_representation(instance, self.solr, True)

        return representation

    @staticmethod
    def to_metadata_representation(instance, solr):
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
                "proteins": solr.get_number_of_field_by_endpoint("entry", "protein_acc", instance.accession),
                "structures": solr.get_number_of_field_by_endpoint("entry", "structure_acc", instance.accession)
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

    @staticmethod
    def to_proteins_detail_representation(instance, solr, is_full=False):
        solr_query = "entry_acc:" + instance.accession
        response = [
            webfront.serializers.uniprot.ProteinSerializer.get_protein_header_from_solr_object(
                r["doclist"]["docs"][0],
                include_protein=is_full,
                solr=solr
            )
            for r in solr.get_group_obj_of_field_by_query(None, "protein_acc", fq=solr_query, rows=10)["groups"]
        ]
        if len(response) == 0:
            raise ReferenceError('There are not proteins for this request')
        return response

    @staticmethod
    def to_structures_detail_representation(instance, solr, is_full=False):
        solr_query = "entry_acc:" + instance.accession
        response = [
            webfront.serializers.pdb.StructureSerializer.get_structure_from_solr_object(
                r,
                include_structure = is_full,
                solr = solr
            )
            for r in solr.execute_query(None, fq=solr_query, rows=10)
        ]
        if len(response) == 0:
            raise ReferenceError('There are not structures for this request')
        return response

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
    def serialize_counter_bucket(bucket):
        output = bucket["unique"]
        if "protein" in bucket or "structure" in bucket:
            output = {"entries": bucket["unique"]}
            if "protein" in bucket:
                output["proteins"] = bucket["protein"]
            if "structure" in bucket:
                output["structures"] = bucket["structure"]
        return output

    @staticmethod
    def to_counter_representation(instance):
        if "entries" not in instance:
            if instance["count"] == 0 or (
                        len(instance["databases"]["buckets"]) == 0 and instance["unintegrated"]["unique"] == 0
            ):
                raise ReferenceError('There are not entries for this request')
            result = {
                "entries": {
                    "member_databases": {
                        bucket["val"]: EntrySerializer.serialize_counter_bucket(bucket)
                        for bucket in instance["databases"]["buckets"]
                    },
                    "unintegrated": 0,
                    "interpro": 0,
                }
            }
            if "unintegrated" in instance and instance["unintegrated"]["count"] > 0:
                result["entries"]["unintegrated"] = EntrySerializer.serialize_counter_bucket(instance["unintegrated"])
            if "interpro" in result["entries"]["member_databases"]:
                result["entries"]["interpro"] = result["entries"]["member_databases"]["interpro"]
                del result["entries"]["member_databases"]["interpro"]
            return result
        return instance

    def to_proteins_count_representation(self, instance):
        solr_query = "entry_acc:"+instance.accession if hasattr(instance, 'accession') else None
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.solr.get_counter_object("protein", solr_query, self.get_extra_endpoints_to_count())
        )["proteins"]

    def to_structures_count_representation(self, instance):
        solr_query = "entry_acc:"+instance.accession if hasattr(instance, 'accession') else None
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.solr.get_counter_object("structure", solr_query, self.get_extra_endpoints_to_count())
        )["structures"]
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
    @staticmethod
    def get_entry_header_from_solr_object(obj, for_structure=False, include_entry=False, solr=None):
        header = {
            "accession": obj["entry_acc"],
            "coordinates": obj["entry_protein_coordinates"],
            # "name": "PTHP_BUCAI",
            # "length": 85,
            "source_database": obj["entry_db"],
            "entry_type": obj["entry_type"],
        }
        if for_structure:
            header["chain"] = obj["chain"]
            header["protein"] = obj["protein_acc"]
        if include_entry:
            header["entry"] = EntrySerializer.to_metadata_representation(
                Entry.objects.get(accession__iexact=obj["entry_acc"]), solr
            )

        return header

    class Meta:
        model = Entry
