from webfront.exceptions import EmptyQuerysetError
from webfront.models import ProteomePerEntry, ProteomePerEntryDB
from webfront.serializers.content_serializers import (
    ModelContentSerializer,
    select_counters,
    process_counters_attribute,
)
from webfront.views.custom import SerializerDetail
from webfront.views.queryset_manager import (
    escape,
    can_use_proteome_per_entry,
    can_use_proteome_per_db,
)


class ProteomeSerializer(ModelContentSerializer):
    def to_representation(self, instance):
        representation = {}
        proteome_instance = instance
        if isinstance(instance, ProteomePerEntry) or isinstance(
            instance, ProteomePerEntryDB
        ):
            proteome_instance = instance.proteome

        representation = self.endpoint_representation(representation, proteome_instance)
        representation = self.filter_representation(
            representation, proteome_instance, self.detail_filters, self.detail
        )
        if self.queryset_manager.other_fields is not None:

            def counter_function(counters_to_include):
                get_c = ProteomeSerializer.get_counters
                return get_c(
                    proteome_instance,
                    self.searcher,
                    self.queryset_manager,
                    counters_to_include,
                )

            representation = self.add_other_fields(
                representation,
                proteome_instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function},
            )
        return representation

    def endpoint_representation(self, representation, instance):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.PROTEOME_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.PROTEOME_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.GROUP_BY:
            representation = self.to_group_representation(instance)
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        serializer2endpoint = {
            SerializerDetail.ENTRY_OVERVIEW: "entry",
            SerializerDetail.PROTEIN_OVERVIEW: "protein",
            SerializerDetail.STRUCTURE_OVERVIEW: "structure",
            SerializerDetail.TAXONOMY_OVERVIEW: "taxonomy",
            SerializerDetail.SET_OVERVIEW: "set",
        }
        query_searcher = (
            "proteome_acc:" + escape(instance.accession).lower()
            if hasattr(instance, "accession")
            else None
        )
        for df in detail_filters:
            if df in serializer2endpoint:
                endpoint = serializer2endpoint[df]
                representation[self.plurals[endpoint]] = self.to_count_representation(
                    endpoint, query_searcher
                )
        if detail != SerializerDetail.PROTEOME_OVERVIEW:
            sq = self.queryset_manager.get_searcher_query()
            if (
                SerializerDetail.ENTRY_DB in detail_filters
                or SerializerDetail.ENTRY_DETAIL in detail_filters
            ):
                key = (
                    "entries"
                    if SerializerDetail.ENTRY_DETAIL in detail_filters
                    else "entry_subset"
                )
                representation[key] = self.to_entries_detail_representation(
                    instance,
                    self.searcher,
                    query_searcher,
                    base_query=sq,
                    queryset_manager=self.queryset_manager,
                )
            if (
                SerializerDetail.STRUCTURE_DB in detail_filters
                or SerializerDetail.STRUCTURE_DETAIL in detail_filters
            ):
                key = (
                    "structures"
                    if SerializerDetail.STRUCTURE_DETAIL in detail_filters
                    else "structure_subset"
                )
                representation[key] = self.to_structures_detail_representation(
                    instance,
                    self.searcher,
                    query_searcher,
                    include_chain=True,
                    queryset_manager=self.queryset_manager,
                )
            if (
                SerializerDetail.PROTEIN_DB in detail_filters
                or SerializerDetail.PROTEIN_DETAIL in detail_filters
            ):
                key = (
                    "proteins"
                    if SerializerDetail.PROTEIN_DETAIL in detail_filters
                    else "protein_subset"
                )
                representation[key] = self.to_proteins_detail_representation(
                    instance,
                    self.searcher,
                    query_searcher,
                    queryset_manager=self.queryset_manager,
                )
            if (
                SerializerDetail.TAXONOMY_DB in detail_filters
                or SerializerDetail.TAXONOMY_DETAIL in detail_filters
            ):
                key = (
                    "taxa"
                    if SerializerDetail.TAXONOMY_DETAIL in detail_filters
                    else "taxonomy_subset"
                )
                representation[key] = self.to_taxonomy_detail_representation(
                    None, self.searcher, query_searcher
                )
            if (
                SerializerDetail.SET_DB in detail_filters
                or SerializerDetail.SET_DETAIL in detail_filters
            ):
                key = (
                    "sets"
                    if SerializerDetail.SET_DETAIL in detail_filters
                    else "set_subset"
                )
                representation[key] = self.to_set_detail_representation(
                    instance, self.searcher, query_searcher
                )
        return representation

    def to_full_representation(self, instance):
        searcher = self.searcher
        sq = self.queryset_manager.get_searcher_query()
        counters = instance.counts
        if self.queryset_manager.is_single_endpoint():
            self.reformatEntryCounters(counters)
        else:
            counters = ProteomeSerializer.get_counters(
                instance, searcher, self.queryset_manager
            )
        return {
            "metadata": {
                "accession": instance.accession,
                "name": {"name": instance.name},
                "source_database": "uniprot",
                "is_reference": instance.is_reference,
                "strain": instance.strain,
                "assembly": instance.assembly,
                "taxonomy": (
                    instance.taxonomy.accession
                    if instance.taxonomy is not None
                    else None
                ),
                "lineage": (
                    instance.taxonomy.lineage if instance.taxonomy is not None else None
                ),
                "counters": counters,
            }
        }

    @staticmethod
    def to_headers_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "is_reference": instance.is_reference,
                "taxonomy": (
                    instance.taxonomy.accession
                    if instance.taxonomy is not None
                    else None
                ),
                "lineage": (
                    instance.taxonomy.lineage if instance.taxonomy is not None else None
                ),
                "source_database": "uniprot",
            }
        }

    @staticmethod
    def get_counters(instance, searcher, queryset_manager, counters_to_include=None):
        endpoints = {
            "entry": ["entries", "entry_acc"],
            "structure": ["structures", "structure_acc"],
            "protein": ["proteins", "protein_acc"],
            "tax": ["taxa", "tax_id"],
            "set": ["sets", "set_acc"],
        }
        counter_endpoints = process_counters_attribute(counters_to_include, endpoints)
        if can_use_proteome_per_entry(queryset_manager.filters):
            match = ProteomePerEntry.objects.filter(
                entry_acc=queryset_manager.filters["entry"]["accession"].upper(),
                proteome=instance.accession,
            ).first()
            if not match:
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Proteome")
                )

            return select_counters(match.counts, counter_endpoints, counters_to_include)
        if can_use_proteome_per_db(queryset_manager.filters):
            match = ProteomePerEntryDB.objects.filter(
                source_database=queryset_manager.filters["entry"]["source_database"],
                proteome=instance.accession,
            ).first()
            if not match:
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Proteome")
                )
            return select_counters(match.counts, counter_endpoints, counters_to_include)
        return ModelContentSerializer.generic_get_counters(
            "proteome",
            endpoints,
            instance,
            searcher,
            queryset_manager,
            counters_to_include,
        )

    @staticmethod
    def to_counter_representation(instance):
        if "proteomes" not in instance:
            if ("count" in instance and instance["count"] == 0) or (
                "doc_count" in instance["databases"]
                and instance["databases"]["doc_count"] == 0
            ):
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Proteome")
                )
            instance = {
                "proteomes": {
                    "uniprot": ProteomeSerializer.serialize_counter_bucket(
                        instance["databases"], "proteomes"
                    )
                }
            }
        return instance

    @staticmethod
    def get_proteome_header_from_search_object(obj, include_chain=False):
        header = {
            "taxonomy": obj["tax_id"],
            "accession": obj["proteome_acc"],
            "lineage": obj["tax_lineage"],
            "source_database": "uniprot",
        }
        if include_chain:
            header["chain"] = obj["structure_chain_acc"]
        return header

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if ProteomeSerializer.grouper_is_empty(instance):
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Proteome")
                )
            return {
                ProteomeSerializer.get_key_from_bucket(
                    bucket
                ): ProteomeSerializer.serialize_counter_bucket(bucket, "proteomes")
                for bucket in instance["groups"]["buckets"]
            }
        elif "proteome_is_reference" in instance:
            return instance
        else:
            return {field_value: total for field_value, total in instance}

    def to_count_representation(self, endpoint, query):
        return self.serializers[endpoint].to_counter_representation(
            self.searcher.get_counter_object(
                endpoint, query, self.get_extra_endpoints_to_count()
            ),
            self.detail_filters,
        )[self.plurals[endpoint]]
