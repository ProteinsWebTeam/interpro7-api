from django.db.models import Count
from webfront.models import Structure
from webfront.serializers.pdb import StructureSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.views.modifiers import (
    group_by,
    sort_by,
    filter_by_field,
    filter_by_field_or_field_range,
    add_extra_fields,
)
from webfront.constants import ModifierType


class ChainPDBAccessionHandler(CustomView):
    level_description = "structure chain level"
    serializer_class = StructureSerializer
    queryset = Structure.objects
    many = False
    serializer_detail = SerializerDetail.STRUCTURE_CHAIN
    serializer_detail_filter = SerializerDetail.STRUCTURE_DETAIL

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
            "searcher", structure_chain_acc=endpoint_levels[level - 1]
        )
        return super(ChainPDBAccessionHandler, self).get(
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
            "searcher", structure_chain_acc=level_name
        )
        return queryset


class PDBAccessionHandler(CustomView):
    level_description = "pdb accession level"
    serializer_class = StructureSerializer
    queryset = Structure.objects
    many = False
    child_handlers = [(r"[a-zA-Z\d]{1,4}", ChainPDBAccessionHandler)]
    serializer_detail_filter = SerializerDetail.STRUCTURE_DETAIL

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
            "structure", accession__iexact=endpoint_levels[level - 1]
        )
        return super(PDBAccessionHandler, self).get(
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
            "structure", accession__iexact=level_name
        )
        return queryset


class PDBHandler(CustomView):
    level_description = "pdb level"
    child_handlers = [
        (r"[a-zA-Z\d]{4}", PDBAccessionHandler),
        # (r'.+', IDAccessionHandler),
    ]
    queryset = Structure.objects.all()
    serializer_class = StructureSerializer
    serializer_detail = SerializerDetail.STRUCTURE_HEADERS
    serializer_detail_filter = SerializerDetail.STRUCTURE_DB

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
        general_handler.queryset_manager.add_filter("structure", source_database="pdb")
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Structure, "counters")
        )
        return super(PDBHandler, self).get(
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
        general_handler.queryset_manager.add_filter("structure", source_database="pdb")
        return queryset


class StructureHandler(CustomView):
    level_description = "Structure level"
    from_model = False
    child_handlers = [("pdb", PDBHandler)]
    to_add = None
    many = False
    serializer_class = StructureSerializer
    serializer_detail = SerializerDetail.STRUCTURE_OVERVIEW
    serializer_detail_filter = SerializerDetail.STRUCTURE_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Structure.objects.filter(accession__in=queryset)
        protein_counter = qs.values_list("source_database").annotate(
            total=Count("source_database")
        )
        output = {"pdb": 0}
        for source_database, total in protein_counter:
            output[source_database] = total
        return {"structures": output}

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
        general_handler.queryset_manager.reset_filters("structure", endpoint_levels)
        general_handler.queryset_manager.add_filter(
            "structure", accession__isnull=False
        )
        general_handler.modifiers.register(
            "group_by",
            group_by(Structure, {"experiment_type": "structure_evidence"}),
            type=ModifierType.REPLACE_PAYLOAD,
            serializer=SerializerDetail.GROUP_BY,
            many=False,
        )
        general_handler.modifiers.register(
            "sort_by",
            sort_by(
                {
                    "accession": "structure_acc",
                    "experiment_type": "structure_evidence",
                    "name": "name",
                }
            ),
        )
        general_handler.modifiers.register(
            "resolution", filter_by_field_or_field_range("structure", "resolution")
        )
        general_handler.modifiers.register(
            "experiment_type", filter_by_field("structure", "experiment_type")
        )

        return super(StructureHandler, self).get(
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
            "structure", accession__isnull=False
        )
        return queryset
