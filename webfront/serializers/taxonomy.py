from webfront.exceptions import EmptyQuerysetError
from webfront.serializers.content_serializers import (
    ModelContentSerializer,
    process_counters_attribute,
    select_counters,
)
from webfront.views.custom import SerializerDetail
from webfront.models import Taxonomy, TaxonomyPerEntry, TaxonomyPerEntryDB
import webfront.serializers.interpro
import webfront.serializers.uniprot
import webfront.serializers.pdb
from webfront.views.queryset_manager import (
    escape,
    can_use_taxonomy_per_entry,
    can_use_taxonomy_per_db,
)


class TaxonomySerializer(ModelContentSerializer):
    def to_representation(self, instance):
        representation = {}
        tax_instance = instance
        if isinstance(instance, TaxonomyPerEntry) or isinstance(
            instance, TaxonomyPerEntryDB
        ):
            tax_instance = instance.taxonomy
        representation = self.endpoint_representation(
            representation, tax_instance, instance
        )
        representation = self.filter_representation(
            representation, tax_instance, self.detail_filters, self.detail
        )
        if self.queryset_manager.other_fields is not None:

            def counter_function(counters_to_include):
                get_c = TaxonomySerializer.get_counters
                return get_c(
                    tax_instance,
                    self.searcher,
                    self.queryset_manager,
                    counters_to_include,
                )

            representation = self.add_other_fields(
                representation,
                tax_instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function},
            )
        return representation

    def endpoint_representation(self, representation, instance, original_instance=None):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.TAXONOMY_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.TAXONOMY_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.TAXONOMY_DETAIL_NAMES:
            representation = self.to_full_representation(instance)
            representation["names"] = self.get_names_map(instance)
        elif detail == SerializerDetail.TAXONOMY_PER_ENTRY:
            representation = self.to_full_representation(original_instance.taxonomy)
            representation["metadata"]["counters"] = original_instance.counts
            representation["names"] = self.get_names_map(original_instance.taxonomy)
            representation["children"] = self.get_counter_for_children_filtered_by_acc(
                original_instance
            )
            representation["metadata"]["children"] = list(
                representation["children"].keys()
            )
        elif detail == SerializerDetail.TAXONOMY_PER_ENTRY_DB:
            representation = self.to_full_representation(original_instance.taxonomy)
            representation["metadata"]["counters"] = original_instance.counts
            representation["names"] = self.get_names_map(original_instance.taxonomy)
            representation["children"] = self.get_counter_for_children_filtered_by_db(
                original_instance
            )
            representation["metadata"]["children"] = list(
                representation["children"].keys()
            )
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        s = self.searcher
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(instance)
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(
                instance
            )
        if SerializerDetail.PROTEOME_OVERVIEW in detail_filters:
            representation["proteomes"] = self.to_proteomes_count_representation(
                instance
            )
        if SerializerDetail.SET_OVERVIEW in detail_filters:
            representation["sets"] = self.to_set_count_representation(instance)
        if detail != SerializerDetail.TAXONOMY_OVERVIEW:
            sq = self.queryset_manager.get_searcher_query()
            if (
                SerializerDetail.ENTRY_DB in detail_filters
                or SerializerDetail.ENTRY_DETAIL in detail_filters
            ):
                key = self.get_endpoint_key(
                    "entry",
                    SerializerDetail.ENTRY_DETAIL,
                    detail_filters,
                    self.queryset_manager.show_subset,
                )
                representation[key] = self.to_entries_detail_representation(
                    instance,
                    s,
                    self.get_searcher_query(instance),
                    self.context["request"],
                    key == "entries_url",
                    queryset_manager=self.queryset_manager,
                )
            if (
                SerializerDetail.STRUCTURE_DB in detail_filters
                or SerializerDetail.STRUCTURE_DETAIL in detail_filters
            ):
                key = self.get_endpoint_key(
                    "structure",
                    SerializerDetail.STRUCTURE_DETAIL,
                    detail_filters,
                    self.queryset_manager.show_subset,
                )
                representation[key] = self.to_structures_detail_representation(
                    instance,
                    s,
                    self.get_searcher_query(instance),
                    self.context["request"],
                    key == "structures_url",
                    include_chain=True,
                    queryset_manager=self.queryset_manager,
                )
            if (
                SerializerDetail.PROTEIN_DB in detail_filters
                or SerializerDetail.PROTEIN_DETAIL in detail_filters
            ):
                key = self.get_endpoint_key(
                    "protein",
                    SerializerDetail.PROTEIN_DETAIL,
                    detail_filters,
                    self.queryset_manager.show_subset,
                )
                representation[key] = self.to_proteins_detail_representation(
                    instance,
                    self.searcher,
                    self.get_searcher_query(instance),
                    self.context["request"],
                    key == "proteins_url",
                    queryset_manager=self.queryset_manager,
                )
            if (
                SerializerDetail.PROTEOME_DB in detail_filters
                or SerializerDetail.PROTEOME_DETAIL in detail_filters
            ):
                key = self.get_endpoint_key(
                    "proteome",
                    SerializerDetail.PROTEOME_DETAIL,
                    detail_filters,
                    self.queryset_manager.show_subset,
                )
                representation[key] = self.to_proteomes_detail_representation(
                    instance,
                    self.searcher,
                    self.get_searcher_query(instance),
                    self.context["request"],
                    key == "proteomes_url",
                )
            if (
                SerializerDetail.SET_DB in detail_filters
                or SerializerDetail.SET_DETAIL in detail_filters
            ):
                key = self.get_endpoint_key(
                    "set",
                    SerializerDetail.SET_DETAIL,
                    detail_filters,
                    self.queryset_manager.show_subset,
                )
                representation[key] = self.to_set_detail_representation(
                    instance,
                    self.searcher,
                    self.get_searcher_query(instance),
                    self.context["request"],
                    key == "sets_url",
                )
        return representation

    def to_full_representation(self, instance):
        searcher = self.searcher
        counters = instance.counts
        if self.queryset_manager.is_single_endpoint():
            self.reformatEntryCounters(counters)
        else:
            counters = TaxonomySerializer.get_counters(
                instance, searcher, self.queryset_manager
            )
        obj = {
            "metadata": {
                "accession": str(instance.accession),
                "lineage": instance.lineage,
                "rank": instance.rank,
                "children": self.get_children(instance),
                "source_database": "uniprot",
                "parent": (
                    str(instance.parent.accession)
                    if instance.parent is not None
                    else None
                ),
                "name": {"name": instance.scientific_name, "short": instance.full_name},
                "counters": counters,
            }
        }
        return obj

    def isChildInQuery(self):
        query = self.queryset_manager.get_searcher_query()

        def filter_children(child):
            q = "{} && tax_lineage:{}".format(query, child)
            response = self.searcher._elastic_json_query(q, {"size": 0})
            value = response["hits"]["total"]
            if type(value) == dict:
                value = response["hits"]["total"]["value"]
            return value > 0

        return filter_children

    def get_children(self, instance):
        filter_children = lambda x: True
        if len(self.detail_filters) > 0:
            filter_children = self.isChildInQuery()
        children = instance.children or []
        return [str(c) for c in children if filter_children(c)]

    @staticmethod
    def to_headers_representation(instance):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.full_name,
                "children": instance.children,
                "parent": (
                    instance.parent.accession if instance.parent is not None else None
                ),
                "source_database": "uniprot",
            }
        }
        return obj

    @staticmethod
    def get_counters(instance, searcher, queryset_manager, counters_to_include=None):
        endpoints = {
            "entry": ["entries", "entry_acc"],
            "structure": ["structures", "structure_acc"],
            "protein": ["proteins", "protein_acc"],
            "set": ["sets", "set_acc"],
            "proteome": ["proteomes", "proteome_acc"],
        }
        counter_endpoints = process_counters_attribute(counters_to_include, endpoints)
        if can_use_taxonomy_per_entry(queryset_manager.filters):
            match = TaxonomyPerEntry.objects.filter(
                entry_acc=queryset_manager.filters["entry"]["accession"].upper(),
                taxonomy_id=instance.accession,
            ).first()
            if not match:
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Taxonomy")
                )

            return select_counters(match.counts, counter_endpoints, counters_to_include)
        if can_use_taxonomy_per_db(queryset_manager.filters):
            match = TaxonomyPerEntryDB.objects.filter(
                source_database=queryset_manager.filters["entry"]["source_database"],
                taxonomy_id=instance.accession,
            ).first()
            if not match:
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Taxonomy")
                )
            return select_counters(match.counts, counter_endpoints, counters_to_include)
        return ModelContentSerializer.generic_get_counters(
            "taxonomy",
            endpoints,
            instance,
            searcher,
            queryset_manager,
            counters_to_include,
        )

    @staticmethod
    def to_counter_representation(instance, filter=None):
        if "taxa" not in instance:
            if ("count" in instance and instance["count"] == 0) or (
                "doc_count" in instance["databases"]
                and instance["databases"]["doc_count"] == 0
            ):
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Taxonomy")
                )
            instance = {
                "taxa": {
                    "uniprot": TaxonomySerializer.serialize_counter_bucket(
                        instance["databases"], "taxa"
                    )
                }
            }
        return instance

    @staticmethod
    def get_searcher_query(instance):
        if isinstance(instance, Taxonomy):
            return (
                "tax_lineage:" + escape(instance.accession).lower()
                if hasattr(instance, "accession")
                else None
            )
        elif isinstance(instance, dict) and "metadata" in instance:
            if "taxonomy" in instance["metadata"]:
                return "tax_lineage:" + escape(instance["metadata"]["taxonomy"]).lower()
            elif "accession" in instance["metadata"]:
                return (
                    "tax_lineage:" + escape(instance["metadata"]["accession"]).lower()
                )
        return None

    def to_entries_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "entry", query, self.get_extra_endpoints_to_count()
            ),
            self.detail_filters,
        )["entries"]

    def to_proteins_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "protein", query, self.get_extra_endpoints_to_count()
            )
        )["proteins"]

    def to_structures_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "structure", query, self.get_extra_endpoints_to_count()
            )
        )["structures"]

    def to_proteomes_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return (
            webfront.serializers.proteome.ProteomeSerializer.to_counter_representation(
                self.searcher.get_counter_object(
                    "proteome", query, self.get_extra_endpoints_to_count()
                )
            )["proteomes"]
        )

    def to_set_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.collection.SetSerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "set", query, self.get_extra_endpoints_to_count()
            )
        )["sets"]

    @staticmethod
    def get_taxonomy_from_search_object(obj, include_chain=False):
        header = {
            "accession": obj["tax_id"],
            "lineage": obj["tax_lineage"],
            "source_database": "uniprot",
        }
        if include_chain:
            header["chain"] = obj["structure_chain_acc"]
        return header

    @staticmethod
    def get_names_map(instance):
        qs = Taxonomy.objects.filter(
            accession__in=instance.lineage.strip().split() + (instance.children or [])
        )
        return {
            t.accession: {"name": t.scientific_name, "short": t.full_name} for t in qs
        }

    @staticmethod
    def get_counter_for_children_filtered_by_acc(instance):
        qs = TaxonomyPerEntry.objects.filter(entry_acc=instance.entry_acc)
        counts = {}
        children = instance.taxonomy.children or []
        for child in children:
            hit = qs.filter(taxonomy__accession=child)
            if len(hit) > 0:
                counts[child] = hit.first().counts
        # return {match.taxonomy.accession: match.counts for match in qs}
        return counts

    @staticmethod
    def get_counter_for_children_filtered_by_db(instance):
        qs = TaxonomyPerEntryDB.objects.filter(
            taxonomy__in=(instance.taxonomy.children or [])
        ).filter(source_database=instance.source_database)
        return {match.taxonomy.accession: match.counts for match in qs}
