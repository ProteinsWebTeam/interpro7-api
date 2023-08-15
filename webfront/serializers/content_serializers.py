from rest_framework import serializers
from rest_framework.utils.urls import replace_query_param, remove_query_param

from webfront.pagination import replace_url_host
from webfront.exceptions import EmptyQuerysetError
from webfront.views.custom import SerializerDetail
import webfront.serializers


class ModelContentSerializer(serializers.ModelSerializer):
    plurals = {
        "entry": "entries",
        "protein": "proteins",
        "structure": "structures",
        "proteome": "proteomes",
        "taxonomy": "taxa",
        "set": "sets",
    }

    NO_DATA_ERROR_MESSAGE = "No {} data matched this request"

    def __init__(self, *args, **kwargs):
        content = kwargs.pop("content", [])
        self.queryset_manager = kwargs.pop("queryset_manager", None)
        self.searcher = kwargs.pop("searcher", None)
        # self.searcher = CustomView.get_search_controller(self.queryset_manager)
        self.detail = kwargs.pop("serializer_detail", SerializerDetail.ALL)
        self.detail_filters = kwargs.pop(
            "serializer_detail_filters", SerializerDetail.ALL
        )

        self.detail_filters = [
            self.detail_filters[x]["filter_serializer"] for x in self.detail_filters
        ]

        self.serializers = {
            "entry": webfront.serializers.interpro.EntrySerializer,
            "protein": webfront.serializers.uniprot.ProteinSerializer,
            "structure": webfront.serializers.pdb.StructureSerializer,
            "taxonomy": webfront.serializers.taxonomy.TaxonomySerializer,
            "proteome": webfront.serializers.proteome.ProteomeSerializer,
            "set": webfront.serializers.collection.SetSerializer,
        }

        super(ModelContentSerializer, self).__init__(*args, **kwargs)
        try:
            for to_be_removed in set(self.Meta.optionals) - set(content):
                self.fields.pop(to_be_removed)
        except AttributeError:
            pass

    def to_representation(self, instance):
        return instance

    def get_extra_endpoints_to_count(self):
        extra = []
        if SerializerDetail.ENTRY_DB in self.detail_filters:
            extra.append("entry")
        if SerializerDetail.PROTEIN_DB in self.detail_filters:
            extra.append("protein")
        if SerializerDetail.STRUCTURE_DB in self.detail_filters:
            extra.append("structure")
        if SerializerDetail.TAXONOMY_DB in self.detail_filters:
            extra.append("taxonomy")
        if SerializerDetail.PROTEOME_DB in self.detail_filters:
            extra.append("proteome")
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
        if (
            "entry" in bucket
            or "protein" in bucket
            or "structure" in bucket
            or "taxonomy" in bucket
            or "proteome" in bucket
            or "set" in bucket
        ):
            output = {plural: output}
            if "entry" in bucket:
                output["entries"] = (
                    bucket["entry"] if is_search_payload else bucket["entry"]["value"]
                )
            if "protein" in bucket:
                output["proteins"] = (
                    bucket["protein"]
                    if is_search_payload
                    else bucket["protein"]["value"]
                )
            if "structure" in bucket:
                output["structures"] = (
                    bucket["structure"]
                    if is_search_payload
                    else bucket["structure"]["value"]
                )
            if "taxonomy" in bucket:
                output["taxa"] = (
                    bucket["taxonomy"]
                    if is_search_payload
                    else bucket["taxonomy"]["value"]
                )
            if "proteome" in bucket:
                output["proteomes"] = (
                    bucket["proteome"]
                    if is_search_payload
                    else bucket["proteome"]["value"]
                )
            if "set" in bucket:
                output["sets"] = (
                    bucket["set"] if is_search_payload else bucket["set"]["value"]
                )
        return output

    @staticmethod
    def to_taxonomy_detail_representation(
        instance, searcher, query, include_chains=False
    ):
        fields = ["tax_id", "structure_chain"] if include_chains else "tax_id"

        response = [
            webfront.serializers.taxonomy.TaxonomySerializer.get_taxonomy_from_search_object(
                r, include_chain=include_chains
            )
            for r in searcher.get_group_obj_of_field_by_query(
                None, fields, fq=query, rows=20
            )["groups"]
        ]

        if len(response) == 0:
            raise EmptyQuerysetError("No organisms found matching this request")
        return response

    @staticmethod
    def to_set_detail_representation(instance, searcher, query, include_chains=False):
        fields = ["set_acc", "structure_chain"] if include_chains else "set_acc"
        response = [
            webfront.serializers.collection.SetSerializer.get_set_from_search_object(
                r, include_chains
            )
            for r in searcher.get_group_obj_of_field_by_query(
                None, fields, fq=query, rows=20
            )["groups"]
        ]
        if len(response) == 0:
            raise EmptyQuerysetError("No sets found matching this request")
        return response

    @staticmethod
    def to_structures_detail_representation(
        instance,
        searcher,
        query,
        include_structure=True,
        include_matches=False,
        include_chain=True,
        base_query="*:*",
    ):
        field = "structure_chain" if include_chain else "structure_acc"
        response = [
            webfront.serializers.pdb.StructureSerializer.get_structure_from_search_object(
                r,
                include_structure=include_structure,
                include_matches=include_matches,
                search=searcher,
                base_query=base_query,
            )
            for r in searcher.get_group_obj_of_field_by_query(
                None, field, fq=query, rows=20
            )["groups"]
        ]
        if len(response) == 0:
            raise EmptyQuerysetError("No entries found matching this request")
        return response

    @staticmethod
    def to_entries_detail_representation(
        instance,
        searcher,
        searcher_query,
        include_chains=False,
        for_structure=False,
        base_query=None,
    ):
        if include_chains:
            search = searcher.get_group_obj_of_field_by_query(
                None, ["structure_chain", "entry_acc"], fq=searcher_query, rows=20
            )["groups"]
        else:
            search = searcher.get_group_obj_of_field_by_query(
                None, "entry_acc", fq=searcher_query, rows=20
            )["groups"]

        response = [
            webfront.serializers.interpro.EntrySerializer.get_entry_header_from_search_object(
                r, searcher=searcher, for_structure=for_structure, sq=base_query
            )
            for r in search
        ]
        if len(response) == 0:
            raise EmptyQuerysetError("No entries found matching this request")

        for entry in response:
            if (
                hasattr(instance, "residues")
                and instance.residues is not None
                and entry["accession"] in instance.residues
            ):
                entry["residues"] = instance.residues
        return response

    @staticmethod
    def to_proteins_detail_representation(
        instance,
        searcher,
        searcher_query,
        include_chains=False,
        include_coordinates=True,
        for_entry=False,
        base_query="*:*",
    ):
        field = "structure_chain" if include_chains else "protein_acc"
        response = [
            webfront.serializers.uniprot.ProteinSerializer.get_protein_header_from_search_object(
                r,
                for_entry=for_entry,
                searcher=searcher,
                include_coordinates=include_coordinates,
                sq=base_query,
            )
            for r in searcher.get_group_obj_of_field_by_query(
                None, field, fq=searcher_query, rows=20
            )["groups"]
        ]
        if len(response) == 0:
            raise EmptyQuerysetError("No proteins found matching this request")
        return response

    @staticmethod
    def to_proteomes_detail_representation(searcher, query, include_chains=False):
        fields = (
            ["proteome_acc", "structure_chain"] if include_chains else "proteome_acc"
        )
        response = [
            webfront.serializers.proteome.ProteomeSerializer.get_proteome_header_from_search_object(
                r, include_chain=include_chains
            )
            for r in searcher.get_group_obj_of_field_by_query(
                None, fields, fq=query, rows=20
            )["groups"]
        ]
        if len(response) == 0:
            raise EmptyQuerysetError("No proteomes found matching this request")
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
            f: instance.__getattribute__(f) for f in other_fields if f not in functions
        }
        for f in functions:
            if f in other_fields:
                representation["extra_fields"][f] = functions[f]()
        return representation

    @staticmethod
    def reformatEntryCounters(counters):
        if counters is None:
            return None
        counters["dbEntries"] = {
            e: c for [e, c] in counters["entries"].items() if e != "total"
        }
        if "total" in counters["entries"]:
            counters["entries"] = counters["entries"]["total"]
        else:
            counters["entries"] = sum(counters["entries"].values())

    def add_pagination(self, payload, obj):
        url = self.context["request"].build_absolute_uri()
        url = replace_url_host(url)
        next_page = None
        previous = None
        if "after_key" in obj and obj["after_key"] is not None:
            next_page = replace_query_param(url, "cursor", obj["after_key"])
        if "before_key" in obj and obj["before_key"] is not None:
            previous = replace_query_param(url, "cursor", obj["before_key"])
        return {"next": next_page, "previous": previous, **payload}
