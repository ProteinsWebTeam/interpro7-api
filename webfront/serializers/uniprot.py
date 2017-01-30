from webfront.constants import get_queryset_type, QuerysetType
from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer
import webfront.serializers.interpro
import webfront.serializers.pdb
from webfront.views.custom import SerializerDetail


class ProteinSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)

        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.PROTEIN_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.PROTEIN_HEADERS:
            representation = self.to_headers_representation(instance)
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        # qs_type = get_queryset_type(instance)
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(instance)

        # if SerializerDetail.ENTRY_MATCH in detail_filters:
        #     representation["entries"] = ProteinSerializer.to_entries_overview_representation(instance, False)
        # if SerializerDetail.ENTRY_DETAIL in detail_filters:
        #     representation["entries"] = ProteinSerializer.to_entries_overview_representation(instance, True)
        # if SerializerDetail.STRUCTURE_HEADERS in detail_filters:
        #     representation["structures"] = ProteinSerializer.to_structures_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        # if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
        #     if qs_type == QuerysetType.PROTEIN:
        #         representation["structures"] = ProteinSerializer.to_structures_overview_representation(instance, True)
        if detail != SerializerDetail.PROTEIN_OVERVIEW:
            if SerializerDetail.ENTRY_DB in detail_filters:
                representation["entries"] = ProteinSerializer.to_entries_detail_representation(instance, self.searcher)
            if SerializerDetail.STRUCTURE_DB in detail_filters:
                representation["structures"] = ProteinSerializer.to_structures_detail_representation(instance, self.searcher)
            if SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = ProteinSerializer.to_entries_detail_representation(instance, self.searcher, True)
            if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = ProteinSerializer.to_structures_detail_representation(instance, self.searcher, True)
        return representation

    def to_full_representation(self, instance):
        return {
            "metadata": self.to_metadata_representation(instance, self.searcher),
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
    def to_metadata_representation(instance, searcher):
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
                "entries": searcher.get_number_of_field_by_endpoint("protein", "entry_acc", instance.accession),
                "structures": searcher.get_number_of_field_by_endpoint("protein", "structure_acc", instance.accession),
            }
        }

    @staticmethod
    def serialize_counter_bucket(bucket):
        output = bucket["unique"]
        is_solr = True
        if isinstance(output, dict):
            output = output["value"]
            is_solr = False
        if "entry" in bucket or "structure" in bucket:
            output = {"proteins": output}
            if "entry" in bucket:
                output["entries"] = bucket["entry"] if is_solr else bucket["entry"]["value"]
            if "structure" in bucket:
                output["structures"] = bucket["structure"] if is_solr else bucket["structure"]["value"]
        return output


    @staticmethod
    def to_counter_representation(instance):
        if "proteins" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("buckets" in instance["databases"] and len(instance["databases"]["buckets"]) == 0):
                raise ReferenceError('There are not entries for this request')

            instance2 = {"proteins": {
                            bucket["val"] if "val" in bucket else bucket["key"]: ProteinSerializer.serialize_counter_bucket(bucket)
                            for bucket in instance["databases"]["buckets"]
                        }}
            instance2["proteins"]["uniprot"] = ProteinSerializer.serialize_counter_bucket(
                instance["uniprot"]
            )
            instance =instance2
        return instance

    #
    # @staticmethod
    # def to_match_representation(match, full=False):
    #     output = {
    #         "coordinates": match.coordinates,
    #         "accession": match.entry_id,
    #         "source_database": match.entry.source_database,
    #         "name": match.entry.name,
    #     }
    #     if match.entry.integrated:
    #         output["integrated"]= match.entry.integrated.accession
    #
    #     if full:
    #         output["entry"] = webfront.serializers.interpro.EntrySerializer.to_metadata_representation(match.entry)
    #
    #     return output
    #
    # @staticmethod
    # def to_entries_representation(instance):
    #     return [
    #         ProteinSerializer.to_match_representation(match)
    #         for match in instance.proteinentryfeature_set.all()
    #     ]
    #
    # @staticmethod
    # def to_entries_count_representation(instance):
    #     return instance.proteinentryfeature_set.count()

    def to_entries_count_representation(self, instance):
        query = "protein_acc:"+instance.accession if hasattr(instance, 'accession') else None
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object("entry", query, self.get_extra_endpoints_to_count())
        )["entries"]

    def to_structures_count_representation(self, instance):
        query = "protein_acc:"+instance.accession if hasattr(instance, 'accession') else None
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object("structure", query, self.get_extra_endpoints_to_count())
        )["structures"]

    @staticmethod
    def to_entries_detail_representation(instance, searcher, is_full=False):
        solr_query = "protein_acc:" + instance.accession
        response = [
            webfront.serializers.interpro.EntrySerializer.get_entry_header_from_solr_object(
                r,
                include_entry=is_full,
                solr=searcher
            )
            for r in searcher.get_group_obj_of_field_by_query(None, "entry_acc", fq=solr_query, rows=10)["groups"]
            ]
        if len(response) == 0:
            raise ReferenceError('There are not entries for this request')
        return response

    @staticmethod
    def to_structures_detail_representation(instance, searcher, is_full=False):
        query = "protein_acc:" + instance.accession
        response = [
            webfront.serializers.pdb.StructureSerializer.get_structure_from_search_object(
                r,
                include_structure=is_full,
                search=searcher
            )
            for r in searcher.get_group_obj_of_field_by_query(None, "structure_chain", fq=query, rows=10)["groups"]
            ]
        if len(response) == 0:
            raise ReferenceError('There are not entries for this request')
        return response

    # #
    # @staticmethod
    # def to_structures_count_representation(instance):
    #     return instance.structures.distinct().count()
    #
    # @staticmethod
    # def to_chain_representation(instance, full=False):
    #     from webfront.serializers.pdb import StructureSerializer
    #
    #     chain = {
    #         "chain": instance.chain,
    #         "accession": instance.structure.accession,
    #         "source_database": instance.structure.source_database,
    #         "length": instance.length,
    #         "organism": instance.organism,
    #         "coordinates": instance.coordinates,
    #     }
    #     if full:
    #         chain["structure"] = StructureSerializer.to_metadata_representation(instance.structure)
    #     return chain
    #
    # @staticmethod
    # def to_structures_overview_representation(instance, is_full=False):
    #     return [
    #         ProteinSerializer.to_chain_representation(match, is_full)
    #         for match in instance.proteinstructurefeature_set.all()
    #         ]
    #
    # @staticmethod
    # def to_entries_overview_representation(instance, is_full=False):
    #     return [
    #         ProteinSerializer.to_match_representation(match, is_full)
    #         for match in instance.proteinentryfeature_set.all()
    #         ]

    @staticmethod
    def get_protein_header_from_search_object(obj, for_entry=True, include_protein=False, solr=None):
        key_coord = "entry_protein_coordinates" if for_entry else "protein_structure_coordinates"
        header = {
            "accession": obj["protein_acc"],
            "coordinates": obj[key_coord],
            # "name": "PTHP_BUCAI",
            # "length": 85,
            "source_database": obj["protein_db"],
            "organism": obj["tax_id"],
        }
        if not for_entry:
            header["chain"] = obj["chain"]
        if include_protein:
            header["protein"] = ProteinSerializer.to_metadata_representation(
                Protein.objects.get(accession__iexact=obj["protein_acc"]), solr
            )
        return header

    class Meta:
        model = Protein
