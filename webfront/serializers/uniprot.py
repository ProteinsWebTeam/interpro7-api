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
        s = self.searcher
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        if detail != SerializerDetail.PROTEIN_OVERVIEW:
            if SerializerDetail.ENTRY_DB in detail_filters:
                representation["entries"] = ProteinSerializer.to_entries_detail_representation(instance, s)
            if SerializerDetail.STRUCTURE_DB in detail_filters:
                representation["structures"] = ProteinSerializer.to_structures_detail_representation(instance, s)
            if SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = ProteinSerializer.to_entries_detail_representation(instance, s)
            if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = ProteinSerializer.to_structures_detail_representation(instance, s)
        return representation

    def to_full_representation(self, instance):
        return {
            "metadata": self.to_metadata_representation(instance, self.searcher),
            "representation": instance.feature,
            "genomic_context": instance.genomic_context,
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
            "protein_evidence": 4, #TODO
            "source_database": instance.source_database,
            "residues": instance.residues,
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

            ins2 = {"proteins": {
                       ProteinSerializer.get_key_from_bucket(bucket): ProteinSerializer.serialize_counter_bucket(bucket)
                       for bucket in instance["databases"]["buckets"]
                   }}
            ins2["proteins"]["uniprot"] = ProteinSerializer.serialize_counter_bucket(
                instance["uniprot"]
            )
            instance = ins2
        return instance

    @staticmethod
    def get_key_from_bucket(bucket):
        key = (bucket["val"] if "val" in bucket else bucket["key"]).upper()
        if key == "S":
            return "swissprot"
        if key == "T":
            return "trembl"
        return key

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
        solr_query = "protein_acc:" + instance.accession.lower()
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
        query = "protein_acc:" + instance.accession.lower()
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

    @staticmethod
    def get_protein_header_from_search_object(obj, for_entry=True, include_protein=False, solr=None):
        key_coord = "entry_protein_coordinates" if for_entry else "protein_structure_coordinates"
        header = {
            "accession": obj["protein_acc"],
            key_coord: obj[key_coord],
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
