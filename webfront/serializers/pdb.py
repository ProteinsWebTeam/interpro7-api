from webfront.exceptions import EmptyQuerysetError
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
        if self.queryset_manager.other_fields is not None:
            def counter_function():
                return StructureSerializer.get_counters(
                    instance,
                    self.searcher,
                    self.queryset_manager.get_searcher_query()
                )
            representation = self.add_other_fields(
                representation,
                instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function}
            )
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
        base_query = self.queryset_manager.get_searcher_query()
        counters = None
        if self.queryset_manager.is_single_endpoint():
            counters = instance.counts
            self.reformatEntryCounters(counters)
        return {
            "metadata": self.to_metadata_representation(instance, self.searcher, base_query, counters),
        }

    def filter_representation(self, representation, instance):
        s = self.searcher
        detail_filters = self.detail_filters
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(representation)
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(representation)
        if SerializerDetail.TAXONOMY_OVERVIEW in detail_filters:
            representation["taxa"] = self.to_taxonomy_count_representation(representation)
        if SerializerDetail.PROTEOME_OVERVIEW in detail_filters:
            representation["proteomes"] = self.to_proteome_count_representation(representation)
        if SerializerDetail.SET_OVERVIEW in detail_filters:
            representation["sets"] = self.to_set_count_representation(representation)

        if self.detail != SerializerDetail.STRUCTURE_OVERVIEW:
            sq = self.queryset_manager.get_searcher_query()
            if SerializerDetail.PROTEIN_DB in detail_filters or \
                    SerializerDetail.PROTEIN_DETAIL in detail_filters:
                key = "proteins" if SerializerDetail.PROTEIN_DETAIL in detail_filters else "protein_subset"
                representation[key] = StructureSerializer.to_proteins_detail_representation(
                    instance, s, "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=True,
                    base_query = sq
                )
            if SerializerDetail.ENTRY_DB in detail_filters or \
                    SerializerDetail.ENTRY_DETAIL in detail_filters:
                key = "entries" if SerializerDetail.ENTRY_DETAIL in detail_filters else "entry_subset"
                representation[key] = self.to_entries_detail_representation(
                    instance, s, "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=True,
                    for_structure=True,
                    base_query=sq
                )
            if SerializerDetail.TAXONOMY_DB in detail_filters or \
                    SerializerDetail.TAXONOMY_DETAIL in detail_filters:
                key = "taxa" if SerializerDetail.TAXONOMY_DETAIL in detail_filters else "taxonomy_subset"
                representation[key] = self.to_taxonomy_detail_representation(
                    instance,
                    self.searcher,
                    "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=True
                )
            if SerializerDetail.PROTEOME_DB in detail_filters or \
                    SerializerDetail.PROTEOME_DETAIL in detail_filters:
                key = "proteomes" if SerializerDetail.PROTEOME_DETAIL in detail_filters else "proteome_subset"
                representation[key] = self.to_proteomes_detail_representation(
                    self.searcher,
                    "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=True
                )
            if SerializerDetail.SET_DB in detail_filters or \
                    SerializerDetail.SET_DETAIL in detail_filters:
                key = "sets" if SerializerDetail.SET_DETAIL in detail_filters else "set_subset"
                representation[key] = self.to_set_detail_representation(
                    instance,
                    self.searcher,
                    "structure_acc:" + escape(instance.accession.lower()),
                    include_chains=True
                )

        return representation

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "experiment_type": instance.experiment_type,
                "resolution": instance.resolution,
            }
        }

    @staticmethod
    def to_metadata_representation(instance, searcher, base_query, counters=None):
        return {
            "accession": instance.accession,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                "other": instance.other_names,
            },
            "experiment_type": instance.experiment_type,
            "release_date": instance.release_date,
            "literature": instance.literature,
            "chains": instance.chains,
            "resolution": instance.resolution,
            "source_database": instance.source_database,
            "counters": StructureSerializer.get_counters(instance, searcher, base_query) if counters is None else counters
        }

    @staticmethod
    def get_counters(instance, searcher, base_query):
        return {
            "entries": searcher.get_number_of_field_by_endpoint("structure", "entry_acc", instance.accession, base_query),
            "proteins": searcher.get_number_of_field_by_endpoint("structure", "protein_acc", instance.accession, base_query),
            "taxa": searcher.get_number_of_field_by_endpoint("structure", "tax_id", instance.accession, base_query),
            "proteomes": searcher.get_number_of_field_by_endpoint("structure", "proteome_acc", instance.accession, base_query),
            "sets": searcher.get_number_of_field_by_endpoint("structure", "set_acc", instance.accession, base_query),
        }

    @staticmethod
    def get_search_query_from_representation(representation):
        query = None
        if "metadata" in representation:
            query = "structure_acc:" + escape(representation["metadata"]["accession"])
            # if "chains" in representation["metadata"] and len(representation["metadata"]["chains"]) == 1:
            #     query += " && ({})".format(" OR ".join(
            #         ["structure_chain_acc:"+x for x in representation["metadata"]["chains"]]
            #     ))
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

    def to_taxonomy_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.taxonomy.TaxonomySerializer.to_counter_representation(
            self.searcher.get_counter_object("taxonomy", query, self.get_extra_endpoints_to_count())
        )["taxa"]

    def to_proteome_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.proteome.ProteomeSerializer.to_counter_representation(
            self.searcher.get_counter_object("proteome", query, self.get_extra_endpoints_to_count())
        )["proteomes"]

    def to_set_count_representation(self, representation):
        query = StructureSerializer.get_search_query_from_representation(representation)
        return webfront.serializers.collection.SetSerializer.to_counter_representation(
            self.searcher.get_counter_object("set", query, self.get_extra_endpoints_to_count())
        )["sets"]

    @staticmethod
    def to_chains_representation(chains):
        if len(chains) < 1:
            raise EmptyQuerysetError('Trying to display an empty list of chains')
        return {
            ch["structure_chain_acc"]: StructureSerializer.get_chain_from_search_object(ch)
            for ch in chains
        }

    @staticmethod
    def get_chain_from_search_object(obj):
        output = {
            "structure_protein_locations": obj["structure_protein_locations"],
            "protein_structure_mapping": obj["protein_structure"],
            "organism": {
                "taxid": obj["tax_id"]
            },
            "accession": obj["protein_acc"],
            "chain": obj["structure_chain_acc"],
            "protein_length": obj["protein_length"],
            "resolution": obj["structure_resolution"],
            "experiment_type": obj["structure_evidence"],
            "source_database": obj["protein_db"]
        }
        if "entry_protein_locations" in obj:
            output["entry_protein_locations"] = obj["entry_protein_locations"]
        return output

    @staticmethod
    def get_structure_from_search_object(obj, include_structure=False, search=None, base_query="*:*"):
        output = StructureSerializer.get_chain_from_search_object(obj)
        output["accession"] = obj["structure_acc"]
        output["protein"] = obj["protein_acc"]
        output["source_database"] = "pdb"
        if include_structure:
            output["structure"] = StructureSerializer.to_metadata_representation(
                Structure.objects.get(accession=obj["structure_acc"].lower()), search, base_query
            )
        return output

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if StructureSerializer.grouper_is_empty(instance):
                raise EmptyQuerysetError(ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Structure"))
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
    def to_counter_representation(instance, filters=None):
        if "structures" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise EmptyQuerysetError(ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Structure"))
            instance = {
                "structures": {
                    "pdb": StructureSerializer.serialize_counter_bucket(instance["databases"], "structures")
                }
            }

        return instance

    class Meta:
        model = Structure
