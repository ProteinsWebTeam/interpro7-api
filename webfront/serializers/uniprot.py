from webfront.exceptions import EmptyQuerysetError
from webfront.models import Protein

from webfront.serializers.content_serializers import ModelContentSerializer
import webfront.serializers.interpro
import webfront.serializers.pdb
from webfront.views.custom import SerializerDetail
from webfront.views.queryset_manager import escape

mamberDBNames = {"REVIEWED": "reviewed", "UNREVIEWED": "unreviewed"}


def formatMemberDBName(name):
    return mamberDBNames[name] if name in mamberDBNames else name


class ProteinSerializer(ModelContentSerializer):
    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(
            representation, instance, self.detail
        )
        representation = self.filter_representation(
            representation, instance, self.detail_filters, self.detail
        )
        if self.queryset_manager.other_fields is not None:

            def counter_function(counters_to_include):
                return ProteinSerializer.get_counters(
                    instance, self.searcher, self.queryset_manager, counters_to_include
                )

            representation = self.add_other_fields(
                representation,
                instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function},
            )
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
            representation["structures"] = self.to_structures_count_representation(
                instance
            )
        if SerializerDetail.TAXONOMY_OVERVIEW in detail_filters:
            representation["taxa"] = self.to_taxonomy_count_representation(instance)
        if SerializerDetail.PROTEOME_OVERVIEW in detail_filters:
            representation["proteomes"] = self.to_proteome_count_representation(
                instance
            )
        if SerializerDetail.SET_OVERVIEW in detail_filters:
            representation["sets"] = self.to_set_count_representation(instance)
        if detail != SerializerDetail.PROTEIN_OVERVIEW:
            if (
                SerializerDetail.ENTRY_DB in detail_filters
                or SerializerDetail.ENTRY_DETAIL in detail_filters
            ):
                key = self.get_entries_key(
                    detail_filters, self.queryset_manager.show_subset
                )

                representation[key] = self.to_entries_detail_representation(
                    instance,
                    s,
                    "protein_acc:" + escape(instance.accession.lower()),
                    key == "entries_url",
                    queryset_manager=self.queryset_manager,
                    request=self.context["request"],
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
                    "protein_acc:" + escape(instance.accession.lower()),
                    include_chain=True,
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
                    instance,
                    self.searcher,
                    "protein_acc:" + escape(instance.accession.lower()),
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
                    self.searcher, "protein_acc:" + escape(instance.accession.lower())
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
                    instance,
                    self.searcher,
                    "protein_acc:" + escape(instance.accession.lower()),
                )
        return representation

    def to_full_representation(self, instance):
        counters = None
        if self.queryset_manager.is_single_endpoint():
            counters = instance.counts
            self.reformatEntryCounters(counters)
            counters["proteome"] = 0 if instance.proteome is None else 1
            counters["taxonomy"] = 0 if instance.tax_id is None else 1
        return {
            "metadata": self.to_metadata_representation(
                instance, self.searcher, self.queryset_manager, counters
            )
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
                "gene": instance.gene,
                "in_alphafold": instance.in_alphafold,
            }
        }

    @staticmethod
    def to_metadata_representation(instance, searcher, queryset_manager, counters=None):
        protein = {
            "accession": instance.accession,
            "id": instance.identifier,
            "source_organism": instance.organism,
            "name": instance.name,
            "description": instance.description,
            "length": instance.length,
            "sequence": instance.sequence,
            "proteome": instance.proteome,
            "gene": instance.gene,
            "go_terms": instance.go_terms,
            "protein_evidence": instance.evidence_code,
            "source_database": instance.source_database,
            "is_fragment": instance.is_fragment,
            "in_alphafold": instance.in_alphafold,
            "ida_accession": instance.ida_id,
            "counters": (
                ProteinSerializer.get_counters(instance, searcher, queryset_manager)
                if counters is None
                else counters
            ),
        }
        if instance.ida_id is not None:
            protein["counters"]["similar_proteins"] = Protein.objects.filter(
                ida_id=instance.ida_id
            ).count()
        return protein

    @staticmethod
    def get_counters(instance, searcher, queryset_manager, counters_to_include=None):
        endpoints = {
            "entry": ["entries", "entry_acc"],
            "structure": ["structures", "structure_acc"],
            "taxonomy": ["taxa", "tax_id"],
            "proteome": ["proteomes", "proteome_acc"],
            "set": ["sets", "set_acc"],
        }
        return ModelContentSerializer.generic_get_counters(
            "protein",
            endpoints,
            instance,
            searcher,
            queryset_manager,
            counters_to_include,
        )

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if ProteinSerializer.grouper_is_empty(instance):
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Protein")
                )
            return {
                ProteinSerializer.get_key_from_bucket(
                    bucket
                ): ProteinSerializer.serialize_counter_bucket(bucket, "proteins")
                for bucket in instance["groups"]["buckets"]
            }
        elif "match_presence" in instance or "is_fragment" in instance:
            return instance
        else:
            return {
                formatMemberDBName(field_value): total
                for field_value, total in instance
            }

    @staticmethod
    def to_counter_representation(instance, filters=None):
        if filters is None:
            filters = []
        if "proteins" not in instance:
            if ProteinSerializer.grouper_is_empty(instance, "databases"):
                raise EmptyQuerysetError(
                    ModelContentSerializer.NO_DATA_ERROR_MESSAGE.format("Protein")
                )

            ins2 = {
                "proteins": {
                    ProteinSerializer.get_key_from_bucket(
                        bucket
                    ): ProteinSerializer.serialize_counter_bucket(bucket, "proteins")
                    for bucket in instance["databases"]["buckets"]
                }
            }
            ins2["proteins"]["uniprot"] = ProteinSerializer.serialize_counter_bucket(
                instance["uniprot"], "proteins"
            )
            instance = ins2
        return instance

    @staticmethod
    def grouper_is_empty(instance, field="groups"):
        return ("count" in instance and instance["count"] == 0) or (
            "buckets" in instance[field] and len(instance[field]["buckets"]) == 0
        )

    def to_entries_count_representation(self, instance):
        query = (
            "protein_acc:" + escape(instance.accession)
            if hasattr(instance, "accession")
            else None
        )
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "entry", query, self.get_extra_endpoints_to_count()
            ),
            self.detail_filters,
        )["entries"]

    def to_structures_count_representation(self, instance):
        query = (
            "protein_acc:" + escape(instance.accession)
            if hasattr(instance, "accession")
            else None
        )
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "structure", query, self.get_extra_endpoints_to_count()
            )
        )["structures"]

    def to_taxonomy_count_representation(self, instance):
        query = (
            "protein_acc:" + escape(instance.accession)
            if hasattr(instance, "accession")
            else None
        )
        return (
            webfront.serializers.taxonomy.TaxonomySerializer.to_counter_representation(
                self.searcher.get_counter_object(
                    "taxonomy", query, self.get_extra_endpoints_to_count()
                )
            )["taxa"]
        )

    def to_proteome_count_representation(self, instance):
        query = (
            "protein_acc:" + escape(instance.accession)
            if hasattr(instance, "accession")
            else None
        )
        return (
            webfront.serializers.proteome.ProteomeSerializer.to_counter_representation(
                self.searcher.get_counter_object(
                    "proteome", query, self.get_extra_endpoints_to_count()
                )
            )["proteomes"]
        )

    def to_set_count_representation(self, instance):
        query = (
            "protein_acc:" + escape(instance.accession)
            if hasattr(instance, "accession")
            else None
        )
        return webfront.serializers.collection.SetSerializer.to_counter_representation(
            self.searcher.get_counter_object(
                "set", query, self.get_extra_endpoints_to_count()
            )
        )["sets"]

    @staticmethod
    def get_protein_header_from_search_object(
        obj,
        for_entry=True,
        include_protein=False,
        searcher=None,
        include_coordinates=True,
        queryset_manager=None,
    ):
        header = {
            "accession": obj["protein_acc"],
            "protein_length": obj["protein_length"],
            "source_database": obj["protein_db"],
            "organism": obj["tax_id"],
            "in_alphafold": not obj["protein_af_score"] == -1,
        }
        if not for_entry and "structure_chain_acc" in obj:
            header["chain"] = obj["structure_chain_acc"]
        if include_coordinates:
            key_coord = (
                "entry_protein_locations"
                if for_entry
                else "structure_protein_locations"
            )
            header[key_coord] = obj[key_coord] if key_coord in obj else None
            # if not for_entry:
            #     header["protein_structure_mapping"] = (
            #         obj["protein_structure"] if "protein_structure" in obj else None
            #     )
        if include_protein:
            header["protein"] = ProteinSerializer.to_metadata_representation(
                Protein.objects.get(accession__iexact=obj["protein_acc"].lower()),
                searcher,
                queryset_manager,
            )
        return header

    class Meta:
        model = Protein
