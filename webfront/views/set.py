from django.db.models import Count

from webfront.models import Set, Alignment
from webfront.serializers.collection import SetSerializer
from webfront.views.custom import CustomView, SerializerDetail
from django.conf import settings

from webfront.views.modifiers import add_extra_fields, get_set_alignment

entry_sets = "|".join(settings.ENTRY_SETS) + "|all"
entry_sets_accessions = r"^({})$".format(
    "|".join((set["accession"] for (_, set) in settings.ENTRY_SETS.items()))
)


#
# class SetAlignmentHandler(CustomView):
#     level_description = 'Set alignment level'
#     many = False
#     serializer_class = SetSerializer
#     serializer_detail = SerializerDetail.SET_ALIGNMENTS
#     def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
#             parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
#         general_handler.queryset_manager.set_main_endpoint("set_alignment")
#         # general_handler.queryset_manager.add_filter("set", accession__iexact=endpoint_levels[level - 1].lower())
#         return super(SetAlignmentHandler, self).get(
#             request._request, endpoint_levels, available_endpoint_handlers,
#             level, self.queryset, handler, general_handler, request, *args, **kwargs
#         )


class SetAccessionHandler(CustomView):
    level_description = "Set accession level"
    serializer_class = SetSerializer
    queryset = Set.objects.all()
    many = False
    # child_handlers = [
    #     ("alignment", SetAlignmentHandler),
    # ]
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
            get_set_alignment,
            use_model_as_payload=True,
            many=True,
            serializer=SerializerDetail.SET_ALIGNMENT,
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


def get_aligments(clan, entry, limit=20):
    qs = Alignment.objects.filter(set_acc=clan, entry_acc=entry).order_by("score")[
        :limit
    ]
    return {
        al.target_acc.accession: {
            "set_acc": None
            if al.target_set_acc is None
            else al.target_set_acc.accession,
            "score": al.score,
            "length": al.seq_length,
            "domains": al.domains,
        }
        for al in qs
    }
