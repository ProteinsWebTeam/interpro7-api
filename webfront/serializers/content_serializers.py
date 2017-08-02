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
    def to_organisms_detail_representation(instance, solr, query):
        response = {r['tax_id']:
            webfront.serializers.taxonomy.OrganismSerializer.get_organism_from_search_object(
                r,
            )
            for r in solr.execute_query(None, fq=query, rows=10)
        }.values()
        if len(response) == 0:
            raise ReferenceError('There are not structures for this request')
        return response
