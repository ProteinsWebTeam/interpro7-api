from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer
import webfront.serializers.interpro
import webfront.serializers.pdb
from webfront.views.custom import SerializerDetail
# from webfront.serializers.utils import recategorise_go_terms
from webfront.views.queryset_manager import escape

mamberDBNames = {
    "REVIEWED": "reviewed",
    "UNREVIEWED": "unreviewed",
}

def formatMemberDBName(name):
    return mamberDBNames[name] if name in mamberDBNames else name


class ProteinSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
        if self.queryset_manager.other_fields is not None:
            representation = self.add_other_fields(representation, instance, self.queryset_manager.other_fields)
        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.PROTEIN_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.PROTEIN_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.GROUP_BY:
            representation = self.to_group_representation(instance)
        else:
            representation = instance
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        s = self.searcher
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        if SerializerDetail.ORGANISM_OVERVIEW in detail_filters:
            representation["organisms"] = self.to_organism_count_representation(instance)
        if SerializerDetail.SET_OVERVIEW in detail_filters:
            representation["sets"] = self.to_set_count_representation(instance)
        if detail != SerializerDetail.PROTEIN_OVERVIEW:
            if SerializerDetail.ENTRY_DB in detail_filters or \
                    SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = self.to_entries_detail_representation(
                    instance, s, "protein_acc:" + escape(instance.accession.lower())
                )
            if SerializerDetail.STRUCTURE_DB in detail_filters or \
                    SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = self.to_structures_detail_representation(
                    instance, s, "protein_acc:" + escape(instance.accession.lower()),
                    include_chain=SerializerDetail.STRUCTURE_DETAIL not in detail_filters
                )
            if SerializerDetail.ORGANISM_DB in detail_filters or \
                    SerializerDetail.ORGANISM_DETAIL in detail_filters:
                representation["organisms"] = self.to_organisms_detail_representation(
                    instance,
                    self.searcher, "protein_acc:" + escape(instance.accession.lower())
                )
            if SerializerDetail.SET_DB in detail_filters or \
                    SerializerDetail.SET_DETAIL in detail_filters:
                representation["sets"] = self.to_set_detail_representation(
                    instance,
                    self.searcher,
                    "protein_acc:" + escape(instance.accession.lower())
                )
        return representation

    def to_full_representation(self, instance):
        return {
            "metadata": self.to_metadata_representation(instance, self.searcher),
        }

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "length": instance.length,
                "source_organism": instance.organism,
            }
        }

    @staticmethod
    def to_metadata_representation(instance, searcher):
        # recategorise_go_terms(instance.go_terms)
        
        protein = {
            "accession": instance.accession,
            "id": instance.identifier,
            "source_organism": instance.organism,
            "name": {
                "name": instance.name,
                "other": instance.other_names,
            },
            "description": instance.description,
            "length": instance.length,
            "sequence": instance.sequence,
            "proteomes": instance.proteomes,
            "gene": instance.gene,
            "go_terms": instance.go_terms,
            "protein_evidence": 4,  # TODO
            "source_database": instance.source_database,
            'fragment': instance.fragment,
            "counters": {
                "entries": searcher.get_number_of_field_by_endpoint("protein", "entry_acc", instance.accession),
                "structures": searcher.get_number_of_field_by_endpoint("protein", "structure_acc", instance.accession),
                "organisms": searcher.get_number_of_field_by_endpoint("protein", "tax_id", instance.accession)
            }
        }
        return protein

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if ProteinSerializer.grouper_is_empty(instance):
                raise ReferenceError('There are not entries for this request')
            return {
                ProteinSerializer.get_key_from_bucket(bucket):
                    ProteinSerializer.serialize_counter_bucket(bucket, "proteins")
                for bucket in instance["groups"]["buckets"]
            }
        else:
            return {formatMemberDBName(field_value): total for field_value, total in instance}

    @staticmethod
    def to_counter_representation(instance):
        if "proteins" not in instance:
            if ProteinSerializer.grouper_is_empty(instance, "databases"):
                raise ReferenceError('There are not entries for this request')

            ins2 = {"proteins": {
                       ProteinSerializer.get_key_from_bucket(bucket):
                           ProteinSerializer.serialize_counter_bucket(bucket, "proteins")
                       for bucket in instance["databases"]["buckets"]
                   }}
            ins2["proteins"]["uniprot"] = ProteinSerializer.serialize_counter_bucket(
                instance["uniprot"], "proteins"
            )
            instance = ins2
        return instance

    @staticmethod
    def grouper_is_empty(instance, field="groups"):
        return ("count" in instance and instance["count"] == 0) or \
               ("buckets" in instance[field] and len(instance[field]["buckets"]) == 0)

    def to_entries_count_representation(self, instance):
        query = "protein_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object("entry", query, self.get_extra_endpoints_to_count()),
            self.detail_filters
        )["entries"]

    def to_structures_count_representation(self, instance):
        query = "protein_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object("structure", query, self.get_extra_endpoints_to_count())
        )["structures"]

    def to_organism_count_representation(self, instance):
        query = "protein_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.taxonomy.OrganismSerializer.to_counter_representation(
            self.searcher.get_counter_object("organism", query, self.get_extra_endpoints_to_count())
        )["organisms"]

    def to_set_count_representation(self, instance):
        query = "protein_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.collection.SetSerializer.to_counter_representation(
            self.searcher.get_counter_object("set", query, self.get_extra_endpoints_to_count())
        )["sets"]

    @staticmethod
    def get_protein_header_from_search_object(obj, for_entry=True, include_protein=False, solr=None, include_coordinates=True):
        header = {
            "accession": obj["protein_acc"],
            "protein_length": obj["protein_length"],
            "source_database": obj["protein_db"],
            "organism": obj["tax_id"],
        }
        if not for_entry:
            header["chain"] = obj["chain"]
        if include_coordinates:
            key_coord = "entry_protein_locations" if for_entry else "protein_structure_locations"
            header[key_coord] = obj[key_coord] if key_coord in obj else None
        if include_protein:
            header["protein"] = ProteinSerializer.to_metadata_representation(
                Protein.objects.get(accession__iexact=obj["protein_acc"]), solr
            )
        return header

    class Meta:
        model = Protein
