from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Structure
import webfront.serializers.uniprot
import webfront.serializers.interpro
from webfront.views.queryset_manager import escape


class StructureSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(representation, instance)
        return representation

    def endpoint_representation(self, representation, instance):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.STRUCTURE_CHAIN:
            representation = self.to_full_representation(instance)
            representation["metadata"]["chains"] = self.to_chains_representation(
                self.searcher.get_chain()
            )
        elif detail == SerializerDetail.GROUP_BY:
            representation = self.to_group_representation(instance)
        return representation

    def to_full_representation(self, instance):
        return {
            "metadata": self.to_metadata_representation(instance, self.searcher),
        }

    def filter_representation(self, representation, instance):
        s = self.searcher
        detail_filters = self.detail_filters
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(representation)
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(representation)
        if SerializerDetail.ORGANISM_OVERVIEW in detail_filters:
            representation["organisms"] = self.to_organism_count_representation(representation)
        if SerializerDetail.SET_OVERVIEW in detail_filters:
            representation["sets"] = self.to_set_count_representation(representation)

        if self.detail != SerializerDetail.STRUCTURE_OVERVIEW:
            if SerializerDetail.PROTEIN_DB in detail_filters or \
                    SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = StructureSerializer.to_proteins_detail_representation(
                    instance, s, "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=SerializerDetail.PROTEIN_DETAIL not in detail_filters
                )
            if SerializerDetail.ENTRY_DB in detail_filters or \
                    SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = self.to_entries_detail_representation(
                    instance, s, "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=SerializerDetail.ENTRY_DETAIL not in detail_filters,
                    for_structure=True
                )
            if SerializerDetail.ORGANISM_DB in detail_filters or \
                    SerializerDetail.ORGANISM_DETAIL in detail_filters:
                representation["organisms"] = self.to_organisms_detail_representation(
                    instance,
                    self.searcher,
                    "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=SerializerDetail.ORGANISM_DETAIL not in detail_filters
                )
            if SerializerDetail.SET_DB in detail_filters or \
                    SerializerDetail.SET_DETAIL in detail_filters:
                representation["sets"] = self.to_set_detail_representation(
                    instance,
                    self.searcher,
                    "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=SerializerDetail.SET_DETAIL not in detail_filters
                )

        return representation

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "experiment_type": instance.experiment_type
            }
        }

    @staticmethod
    def to_metadata_representation(instance, searcher):
        return {
            "accession": instance.accession,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                "other": instance.other_names,
            },
            "experiment_type": instance.experiment_type,
            "release_date": instance.release_date,
            "authors": instance.authors,
            "chains": instance.chains,
            "source_database": instance.source_database,
            "counters": {
                "entries": searcher.get_number_of_field_by_endpoint("structure", "entry_acc", instance.accession),
                "proteins": searcher.get_number_of_field_by_endpoint("structure", "protein_acc", instance.accession),
            }
        }

    @staticmethod
    def get_search_query_from_representation(representation):
        query = None
        if "metadata" in representation:
            query = "structure_acc:" + escape(representation["metadata"]["accession"])
            if "chains" in representation["metadata"] and len(representation["metadata"]["chains"]) == 1:
                query += " && ({})".format(" OR ".join(
                    ["chain:"+x for x in representation["metadata"]["chains"]]
                ))
        return query

    def to_proteins_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.searcher.get_counter_object("protein", query, self.get_extra_endpoints_to_count())
        )["proteins"]

    def to_entries_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object("entry", query, self.get_extra_endpoints_to_count()),
            self.detail_filters
        )["entries"]

    def to_organism_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.taxonomy.OrganismSerializer.to_counter_representation(
            self.searcher.get_counter_object("organism", query, self.get_extra_endpoints_to_count())
        )["organisms"]

    def to_set_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.collection.SetSerializer.to_counter_representation(
            self.searcher.get_counter_object("set", query, self.get_extra_endpoints_to_count())
        )["sets"]

    # @staticmethod
    # def to_proteins_detail_representation(instance, searcher, is_full=False):
    #     query = "structure_acc:" + escape(instance.accession.lower())
    #     response = [
    #         webfront.serializers.uniprot.ProteinSerializer.get_protein_header_from_search_object(
    #             r,
    #             for_entry=False,
    #             include_protein=is_full,
    #             solr=searcher
    #         )
    #         for r in searcher.get_group_obj_of_field_by_query(None, "structure_chain", fq=query, rows=10)["groups"]
    #         ]
    #     if len(response) == 0:
    #         raise ReferenceError('There are not structures for this request')
    #     return response

    @staticmethod
    def to_chains_representation(chains):
        if len(chains) < 1:
            raise ReferenceError('Trying to display an empty list of chains')
        return {
            ch["chain"]: StructureSerializer.get_chain_from_search_object(ch)
            for ch in chains
        }

    @staticmethod
    def get_chain_from_search_object(obj):
        output = {
            "protein_structure_locations": obj["protein_structure_locations"],
            "organism": {
                "taxid": obj["tax_id"]
            },
            "accession": obj["protein_acc"],
            "chain": obj["chain"],
            "protein_length": obj["protein_length"],
            "source_database": obj["protein_db"]
        }
        if "entry_protein_locations" in obj:
            output["entry_protein_locations"] = obj["entry_protein_locations"]
        return output

    @staticmethod
    def get_structure_from_search_object(obj, include_structure=False, search=None):
        output = StructureSerializer.get_chain_from_search_object(obj)
        output["accession"] = obj["structure_acc"]
        output["protein"] = obj["protein_acc"]
        output["source_database"] = "pdb"
        if include_structure:
            output["structure"] = StructureSerializer.to_metadata_representation(
                Structure.objects.get(accession__iexact=obj["structure_acc"]), search
            )
        return output

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if StructureSerializer.grouper_is_empty(instance):
                raise ReferenceError('There are not entries for this request')
            return {
                StructureSerializer.get_key_from_bucket(bucket): StructureSerializer.serialize_counter_bucket(bucket, "structures")
                for bucket in instance["groups"]["buckets"]
            }
        else:
            return {field_value: total for field_value, total in instance}

    @staticmethod
    def grouper_is_empty(instance, field="groups"):
        return ("count" in instance and instance["count"] == 0) or \
               ("buckets" in instance[field] and len(instance[field]["buckets"]) == 0)

    @staticmethod
    def to_counter_representation(instance):
        if "structures" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise ReferenceError('There are not structures for this request')
            instance = {
                "structures": {
                    "pdb": StructureSerializer.serialize_counter_bucket(instance["databases"], "structures")
                }
            }

        return instance

    # @staticmethod
    # def serialize_counter_bucket(bucket):
    #     output = bucket["unique"]
    #     is_solr = True
    #     if isinstance(output, dict):
    #         output = output["value"]
    #         is_solr = False
    #     if "entry" in bucket or "protein" in bucket:
    #         output = {"structures": output}
    #         if "entry" in bucket:
    #             output["entries"] = bucket["entry"] if is_solr else bucket["entry"]["value"]
    #         if "protein" in bucket:
    #             output["proteins"] = bucket["protein"] if is_solr else bucket["protein"]["value"]
    #     return output

    class Meta:
        model = Structure
