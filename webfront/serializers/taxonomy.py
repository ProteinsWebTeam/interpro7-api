from webfront.exceptions import EmptyQuerysetError
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Taxonomy
import webfront.serializers.interpro
import webfront.serializers.uniprot
import webfront.serializers.pdb
from webfront.views.queryset_manager import escape


class TaxonomySerializer(ModelContentSerializer):
    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(
            representation, instance, self.detail_filters, self.detail
        )
        if self.queryset_manager.other_fields is not None:

            def counter_function():
                get_c = TaxonomySerializer.get_counters
                return get_c(
                    instance, self.searcher, self.queryset_manager.get_searcher_query()
                )

            representation = self.add_other_fields(
                representation,
                instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function},
            )
        return representation

    def endpoint_representation(self, representation, instance):
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
                key = (
                    "entries"
                    if SerializerDetail.ENTRY_DETAIL in detail_filters
                    else "entry_subset"
                )
                representation[key] = self.to_entries_detail_representation(
                    instance, s, self.get_searcher_query(instance), base_query=sq
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
                    s,
                    self.get_searcher_query(instance),
                    include_chain=True,
                    base_query=sq,
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
                    self.get_searcher_query(instance),
                    base_query=sq,
                )
            if (
                SerializerDetail.PROTEOME_DB in detail_filters
                or SerializerDetail.PROTEOME_DETAIL in detail_filters
            ):
                key = (
                    "proteomes"
                    if SerializerDetail.PROTEOME_DETAIL in detail_filters
                    else "proteome_subset"
                )
                representation[key] = self.to_proteomes_detail_representation(
                    self.searcher, self.get_searcher_query(instance)
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
                    instance, self.searcher, self.get_searcher_query(instance)
                )
        return representation

    def to_full_representation(self, instance):
        searcher = self.searcher
        sq = self.queryset_manager.get_searcher_query()
        counters = instance.counts
        if self.queryset_manager.is_single_endpoint():
            self.reformatEntryCounters(counters)
        else:
            counters = TaxonomySerializer.get_counters(instance, searcher, sq)
        obj = {
            "metadata": {
                "accession": str(instance.accession),
                "lineage": instance.lineage,
                "rank": instance.rank,
                "children": self.get_children(instance),
                "source_database": "uniprot",
                "parent": str(instance.parent.accession)
                if instance.parent is not None
                else None,
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
            return response["hits"]["total"]["value"] > 0

        return filter_children

    def get_children(self, instance):
        filter_children = lambda x: True
        if len(self.detail_filters) > 0:
            filter_children = self.isChildInQuery()
        return [str(c) for c in instance.children if filter_children(c)]

    @staticmethod
    def to_headers_representation(instance):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.full_name,
                "children": instance.children,
                "parent": instance.parent.accession
                if instance.parent is not None
                else None,
                "source_database": "uniprot",
            }
        }
        return obj

    @staticmethod
    def get_counters(instance, searcher, sq):
        return {
            "entries": searcher.get_number_of_field_by_endpoint(
                "taxonomy", "entry_acc", instance.accession, sq
            ),
            "structures": searcher.get_number_of_field_by_endpoint(
                "taxonomy", "structure_acc", instance.accession, sq
            ),
            "proteins": searcher.get_number_of_field_by_endpoint(
                "taxonomy", "protein_acc", instance.accession, sq
            ),
            "sets": searcher.get_number_of_field_by_endpoint(
                "taxonomy", "set_acc", instance.accession, sq
            ),
            "proteomes": searcher.get_number_of_field_by_endpoint(
                "taxonomy", "proteome_acc", instance.accession, sq
            ),
        }

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
        return webfront.serializers.proteome.ProteomeSerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "proteome", query, self.get_extra_endpoints_to_count()
            )
        )[
            "proteomes"
        ]

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
            accession__in=instance.lineage.strip().split() + instance.children
        )
        return {
            t.accession: {"name": t.scientific_name, "short": t.full_name} for t in qs
        }
