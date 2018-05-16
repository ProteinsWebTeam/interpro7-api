from rest_framework import serializers

from webfront.views.custom import SerializerDetail, CustomView
from webfront.views.queryset_manager import escape
import webfront.serializers#.uniprot
# import webfront.serializers.pdb
# import webfront.serializers.taxonomy

class ModelContentSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        content = kwargs.pop('content', [])
        self.queryset_manager = kwargs.pop('queryset_manager', None)
        self.searcher = kwargs.pop('searcher', None)
        # self.searcher = CustomView.get_search_controller(self.queryset_manager)
        self.detail = kwargs.pop('serializer_detail', SerializerDetail.ALL)
        self.detail_filters = kwargs.pop('serializer_detail_filters', SerializerDetail.ALL)

        self.detail_filters = [self.detail_filters[x]["filter_serializer"] for x in self.detail_filters]
        super(ModelContentSerializer, self).__init__(*args, **kwargs)
        try:
            for to_be_removed in set(self.Meta.optionals) - set(content):
                self.fields.pop(to_be_removed)
        except AttributeError:
            pass

    def get_extra_endpoints_to_count(self):
        extra = []
        if SerializerDetail.ENTRY_DB in self.detail_filters:
            extra.append("entry")
        if SerializerDetail.PROTEIN_DB in self.detail_filters:
            extra.append("protein")
        if SerializerDetail.STRUCTURE_DB in self.detail_filters:
            extra.append("structure")
        if SerializerDetail.ORGANISM_DB in self.detail_filters:
            extra.append("organism")
        if SerializerDetail.SET_DB in self.detail_filters:
            extra.append("set")
        return extra

    @staticmethod
    def serialize_counter_bucket(bucket, plural):
        output = bucket["unique"]
        is_search_payload = True
        if isinstance(output, dict):
            output = output["value"]
            is_search_payload = False
        if "entry" in bucket or "protein" in bucket or "structure" in bucket or "organism" in bucket or "set" in bucket:
            output = {plural: output}
            if "entry" in bucket:
                output["entries"] = bucket["entry"] if is_search_payload else bucket["entry"]["value"]
            if "protein" in bucket:
                output["proteins"] = bucket["protein"] if is_search_payload else bucket["protein"]["value"]
            if "structure" in bucket:
                output["structures"] = bucket["structure"] if is_search_payload else bucket["structure"]["value"]
            if "taxa" in bucket:
                output["taxa"] = bucket["taxa"] if is_search_payload else bucket["taxa"]["value"]
            if "set" in bucket:
                output["sets"] = bucket["set"] if is_search_payload else bucket["set"]["value"]
        return output

    @staticmethod
    def to_organisms_detail_representation(instance, searcher, query, include_chains=False):
        fields = ["tax_id", "structure_chain"] if include_chains else "tax_id"

        response = [
            webfront.serializers.taxonomy.OrganismSerializer.get_organism_from_search_object(
                r, include_chain=include_chains
            )
            for r in searcher.get_group_obj_of_field_by_query(None, fields, fq=query, rows=10)["groups"]
            ]


        if len(response) == 0:
            raise ReferenceError('There are not organisms for this request')
        return response

    @staticmethod
    def to_set_detail_representation(instance, searcher, query, include_chains=False):
        fields = ["set_acc", "structure_chain"] if include_chains else "set_acc"
        response = [
            webfront.serializers.collection.SetSerializer.get_set_from_search_object(r, include_chains)
            for r in searcher.get_group_obj_of_field_by_query(None, fields, fq=query, rows=10)["groups"]
            ]
        if len(response) == 0:
            raise ReferenceError('There are not sets for this request')
        return response


    @staticmethod
    def to_structures_detail_representation(instance, searcher, query, include_structure=True, include_chain=True, base_query="*:*"):
        field = "structure_chain" if include_chain else "structure_acc"
        response = [
            webfront.serializers.pdb.StructureSerializer.get_structure_from_search_object(
                r,
                include_structure=include_structure,
                search=searcher,
                base_query=base_query
            )
            for r in searcher.get_group_obj_of_field_by_query(None, field, fq=query, rows=10)["groups"]
            ]
        if len(response) == 0:
            raise ReferenceError('There are not entries for this request')
        return response

    @staticmethod
    def to_entries_detail_representation(instance, searcher, searcher_query, include_chains=False, for_structure=False, base_query=None):
        if include_chains:
            # search = searcher.execute_query(None, fq=searcher_query, rows=10)
            search = searcher.get_group_obj_of_field_by_query(None, ["structure_chain","entry_acc"], fq=searcher_query, rows=10)["groups"]
        else:
            search = searcher.get_group_obj_of_field_by_query(None, "entry_acc", fq=searcher_query, rows=10)["groups"]

        response = [
            webfront.serializers.interpro.EntrySerializer.get_entry_header_from_search_object(
                r, searcher=searcher, for_structure=for_structure, sq=base_query
            )
            for r in search
            ]
        if len(response) == 0:
            raise ReferenceError('There are not entries for this request')

        for entry in response:
            if hasattr(instance, 'residues') and entry['accession'] in instance.residues:
                entry['residues'] = instance.residues
        return response

    @staticmethod
    def to_proteins_detail_representation(instance, searcher, searcher_query, include_chains=False, include_coordinates=True, for_entry=False, base_query="*:*"):
        field = "structure_chain" if include_chains else "protein_acc"
        response = [
            webfront.serializers.uniprot.ProteinSerializer.get_protein_header_from_search_object(
                r,
                for_entry=for_entry,
                searcher=searcher,
                include_coordinates=include_coordinates,
                sq=base_query
            )
            for r in searcher.get_group_obj_of_field_by_query(None, field, fq=searcher_query, rows=10)["groups"]
        ]
        if len(response) == 0:
            raise ReferenceError('There are not proteins for this request')
        return response

    @staticmethod
    def get_key_from_bucket(bucket):
        key = str(bucket["val"] if "val" in bucket else bucket["key"]).lower()
        return key

    @staticmethod
    def add_other_fields(representation, instance, other_fields, functions=None):
        if functions is None:
            functions = []
        representation["extra_fields"] = {
            f: instance.__getattribute__(f)
            for f in other_fields
            if f not in functions
        }
        for f in functions:
            if f in other_fields:
                representation["extra_fields"][f] = functions[f]()
        return representation
