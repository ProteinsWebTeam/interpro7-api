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
        return extra

    @staticmethod
    def serialize_counter_bucket(bucket, plural):
        output = bucket["unique"]
        is_search_payload = True
        if isinstance(output, dict):
            output = output["value"]
            is_search_payload = False
        if "entry" in bucket or "protein" in bucket or "structure" in bucket or "organism" in bucket:
            output = {plural: output}
            if "entry" in bucket:
                output["entries"] = bucket["entry"] if is_search_payload else bucket["entry"]["value"]
            if "protein" in bucket:
                output["proteins"] = bucket["protein"] if is_search_payload else bucket["protein"]["value"]
            if "structure" in bucket:
                output["structures"] = bucket["structure"] if is_search_payload else bucket["structure"]["value"]
            if "organism" in bucket:
                output["organisms"] = bucket["organism"] if is_search_payload else bucket["organism"]["value"]
        return output

    @staticmethod
    def to_organisms_detail_representation(instance, solr, query, include_chains=False):
        response = list({"{}_{}".format(r['tax_id'], r['chain']) if include_chains else r['tax_id']:
            webfront.serializers.taxonomy.OrganismSerializer.get_organism_from_search_object(
                r, include_chain=include_chains
            )
            for r in solr.execute_query(None, fq=query, rows=10)
        }.values())
        if len(response) == 0:
            raise ReferenceError('There are not structures for this request')
        return response

    @staticmethod
    def to_structures_detail_representation(instance, searcher, query, is_full=False):
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
    def to_entries_detail_representation(instance, searcher, searcher_query, for_structure=False):
        if for_structure:
            search = searcher.execute_query(None, fq=searcher_query, rows=10)
        else:
            search = searcher.get_group_obj_of_field_by_query(None, "entry_acc", fq=searcher_query, rows=10)["groups"]
        response = [
            webfront.serializers.interpro.EntrySerializer.get_entry_header_from_solr_object(
                r, solr=searcher, for_structure=for_structure
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
    def to_proteins_detail_representation(instance, searcher, searcher_query, include_chains=False, include_coordinates=True):
        field = "structure_chain" if not include_chains else "protein_acc"
        response = [
            webfront.serializers.uniprot.ProteinSerializer.get_protein_header_from_search_object(
                r,
                for_entry=include_chains,
                solr=searcher,
                include_coordinates=include_coordinates
            )
            for r in searcher.get_group_obj_of_field_by_query(None, field, fq=searcher_query, rows=10)["groups"]
        ]
        if len(response) == 0:
            raise ReferenceError('There are not proteins for this request')
        return response
