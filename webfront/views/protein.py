from django.db.models import Count
from django.shortcuts import redirect

from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.views.modifiers import (
    group_by,
    sort_by,
    filter_by_field,
    filter_by_boolean_field,
    get_single_value,
    get_domain_architectures,
    filter_by_contains_field,
    filter_by_match_presence,
    add_extra_fields,
    get_isoforms,
    calculate_residue_conservation,
)
from webfront.models import Protein
from django.conf import settings

entry_db_members = "|".join(settings.DB_MEMBERS)

db_members = r"((un)?reviewed)|(uniprot)"


class UniprotAccessionHandler(CustomView):
    level_description = "uniprot accession level"
    serializer_class = ProteinSerializer
    queryset = Protein.objects
    many = False
    serializer_detail_filter = SerializerDetail.PROTEIN_DETAIL

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):
        general_handler.queryset_manager.add_filter(
            "protein", accession__iexact=endpoint_levels[level - 1]
        )
        general_handler.modifiers.register(
            "residues", get_single_value("residues"), use_model_as_payload=True
        )
        general_handler.modifiers.register(
            "structureinfo", get_single_value("structure"), use_model_as_payload=True
        )
        general_handler.modifiers.register(
            "ida", get_single_value("ida", True), use_model_as_payload=True
        )
        general_handler.modifiers.register(
            "extra_features",
            get_single_value("extra_features"),
            use_model_as_payload=True,
        )
        general_handler.modifiers.register(
            "isoforms", get_isoforms, use_model_as_payload=True
        )
        general_handler.modifiers.register(
            "conservation", calculate_residue_conservation, use_model_as_payload=True
        )
        return super(UniprotAccessionHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter(
            "protein", accession__iexact=level_name.lower()
        )
        return queryset


class IDAccessionHandler(UniprotAccessionHandler):
    level_description = "uniprot id level"

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):
        if parent_queryset is not None:
            self.queryset = parent_queryset

        general_handler.queryset_manager.add_filter(
            "protein", identifier=endpoint_levels[level - 1]
        )
        queryset = general_handler.queryset_manager.get_queryset(
            only_main_endpoint=True
        )
        if len(queryset) > 0:
            new_url = settings.INTERPRO_CONFIG[
                "url_path_prefix"
            ] + request.get_full_path().replace(
                endpoint_levels[level - 1], queryset.first().accession
            )

            return redirect(new_url)
        return super(IDAccessionHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )


class UniprotHandler(CustomView):
    level_description = "uniprot level"
    child_handlers = [
        (
            r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}",
            UniprotAccessionHandler,
        ),
        (r".+", IDAccessionHandler),
    ]
    queryset = Protein.objects.all()
    serializer_class = ProteinSerializer
    serializer_detail = SerializerDetail.PROTEIN_HEADERS
    serializer_detail_filter = SerializerDetail.PROTEIN_DB

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):
        ds = endpoint_levels[level - 1].lower()
        if ds != "uniprot":
            general_handler.queryset_manager.add_filter("protein", source_database=ds)
        general_handler.modifiers.register(
            "ida",
            get_domain_architectures,
            use_model_as_payload=True,
            serializer=SerializerDetail.PROTEIN_HEADERS,
            many=True,
        )
        general_handler.modifiers.register(
            "id", filter_by_field("protein", "identifier")
        )
        general_handler.modifiers.register(
            "go_term",
            filter_by_contains_field("protein", "go_terms", '"identifier": "{}"'),
        )
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Protein, "counters")
        )
        return super(UniprotHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        if level_name.lower() != "uniprot":
            general_handler.queryset_manager.add_filter(
                "protein", source_database=level_name.lower()
            )
        else:
            general_handler.queryset_manager.add_filter(
                "protein", source_database__isnull=False
            )
        return queryset


class ProteinHandler(CustomView):
    serializer_class = ProteinSerializer
    many = False
    serializer_detail = SerializerDetail.PROTEIN_OVERVIEW
    level_description = "Protein level"
    from_model = False
    child_handlers = [(db_members, UniprotHandler)]
    to_add = None
    serializer_detail_filter = SerializerDetail.PROTEIN_OVERVIEW

    def get_database_contributions(self, queryset):
        if Protein.objects.count() == queryset.count():
            qs = Protein.objects
        else:
            qs = Protein.objects.filter(accession__in=queryset)
        protein_counter = qs.values_list("source_database").annotate(
            total=Count("source_database")
        )
        output = {}
        for (source_database, total) in protein_counter:
            output[source_database] = total

        output["uniprot"] = sum(output.values())
        return {"proteins": output}

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        general_handler.queryset_manager.reset_filters("protein", endpoint_levels)
        general_handler.queryset_manager.add_filter("protein", accession__isnull=False)
        general_handler.modifiers.register(
            "group_by",
            group_by(
                Protein,
                {
                    "tax_id": "tax_id",
                    "source_database": "protein_db",
                    "go_terms": "text",
                    "match_presence": "match_presence",
                    "is_fragment": "protein_is_fragment",
                },
            ),
            use_model_as_payload=True,
            serializer=SerializerDetail.GROUP_BY,
        )

        general_handler.modifiers.register(
            "sort_by", sort_by({"accession": "protein_acc", "length": "length"})
        )
        general_handler.modifiers.register(
            "tax_id", filter_by_field("protein", "tax_id")
        )
        general_handler.modifiers.register(
            "protein_evidence", filter_by_field("protein", "evidence_code")
        )
        general_handler.modifiers.register("match_presence", filter_by_match_presence)
        general_handler.modifiers.register(
            "is_fragment", filter_by_boolean_field("protein", "is_fragment")
        )

        return super(ProteinHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("protein", accession__isnull=False)
        return queryset
