from django.db.models import Count

from webfront.models import Set
from webfront.serializers.collection import SetSerializer
from webfront.views.custom import CustomView, SerializerDetail
from django.conf import settings

from webfront.views.modifiers import add_extra_fields, get_deprecated_response

entry_sets = "|".join(settings.ENTRY_SETS) + "|all"
entry_sets_accessions = r"^({})$".format(
    "|".join((set["accession"] for (_, set) in settings.ENTRY_SETS.items()))
)


class SetAccessionHandler(CustomView):
    level_description = "Set accession level"
    serializer_class = SetSerializer
    queryset = Set.objects.all()
    many = False
    serializer_detail_filter = SerializerDetail.SET_DETAIL

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
            "set", accession__iexact=endpoint_levels[level - 1].lower()
        )
        general_handler.modifiers.register(
            "alignments",
            get_deprecated_response("Profile-profile alignments have been permanently removed in InterPro 97.0.")
        )

        return super(SetAccessionHandler, self).get(
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
            "set", accession__iexact=level_name.lower()
        )
        return queryset


class SetTypeHandler(CustomView):
    level_description = "set type level"
    child_handlers = [
        (entry_sets_accessions, SetAccessionHandler),
        # ("proteome", ProteomeHandler),
    ]
    queryset = Set.objects.all()
    serializer_class = SetSerializer
    serializer_detail = SerializerDetail.SET_HEADERS
    serializer_detail_filter = SerializerDetail.SET_DB

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
        db = endpoint_levels[level - 1]
        if db.lower() != "all":
            general_handler.queryset_manager.add_filter("set", source_database=db)
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Set, "counters")
        )
        return super(SetTypeHandler, self).get(
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
        if level_name.lower() != "all":
            general_handler.queryset_manager.add_filter(
                "set", source_database=level_name
            )
        return queryset


class SetHandler(CustomView):
    level_description = "Set level"
    from_model = False
    child_handlers = [
        (entry_sets, SetTypeHandler),
        # ("proteome", ProteomeHandler),
    ]
    many = False
    serializer_class = SetSerializer
    serializer_detail = SerializerDetail.SET_OVERVIEW
    serializer_detail_filter = SerializerDetail.SET_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Set.objects.filter(accession__in=queryset)
        set_counter = qs.values_list("source_database").annotate(
            total=Count("source_database")
        )
        output = {c[0]: c[1] for c in set_counter if c[0] != "node"}
        output["all"] = sum(output.values())
        return {"sets": output}

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
        general_handler.queryset_manager.reset_filters("set", endpoint_levels)
        general_handler.queryset_manager.add_filter("set", accession__isnull=False)

        return super(SetHandler, self).get(
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
        general_handler.queryset_manager.add_filter("set", accession__isnull=False)
        return queryset

