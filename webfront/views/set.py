from django.db.models import Count

from webfront.models import Set
from webfront.serializers.collection import SetSerializer
from webfront.views.custom import CustomView, SerializerDetail
from django.conf import settings

entry_sets = '|'.join(settings.ENTRY_SETS)
entry_sets_accessions = (
    r'^({})$'.format('|'.join((set['accession'] for (_, set) in settings.ENTRY_SETS.items())))
)


class SetNodeAccessionHandler(CustomView):
    level_description = 'Set nodeaccession level'
    serializer_class = SetSerializer
    queryset = Set.objects.all()
    many = False
    child_handlers = []
    serializer_detail_filter = SerializerDetail.SET_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("set", accession=endpoint_levels[level - 1].upper())
        return super(SetNodeAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("set", accession=level_name.upper())
        return queryset


class SetNodeHandler(CustomView):
    serializer_class = SetSerializer
    serializer_detail = SerializerDetail.SET_HEADERS
    serializer_detail_filter = SerializerDetail.SET_DB
    level_description = 'set type level'
    child_handlers = [
        (r'.+', SetNodeAccessionHandler),
        # ("proteome", ProteomeHandler),
    ]
    queryset = Set.objects.all()

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("set", integrated__contains=endpoint_levels[level - 2].lower())
        # general_handler.queryset_manager.add_filter("set", source_database='node')
        general_handler.queryset_manager.remove_filter("set", "accession")
        general_handler.queryset_manager.remove_filter("set", "source_database")
        return super(SetNodeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.update_integrated_filter("set")
        # general_handler.queryset_manager.add_filter("set", source_database__iexact=level_name)
        return queryset


class SetAccessionHandler(CustomView):
    level_description = 'Set accession level'
    serializer_class = SetSerializer
    queryset = Set.objects.all()
    many = False
    child_handlers = [
        ("node", SetNodeHandler),
    ]
    serializer_detail_filter = SerializerDetail.SET_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("set", accession=endpoint_levels[level - 1].upper())
        return super(SetAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("set", accession=level_name.upper())
        return queryset

class SetTypeHandler(CustomView):
    level_description = 'set type level'
    child_handlers = [
        (entry_sets_accessions, SetAccessionHandler),
        # ("proteome", ProteomeHandler),
    ]
    queryset = Set.objects.all()
    serializer_class = SetSerializer
    serializer_detail = SerializerDetail.SET_HEADERS
    serializer_detail_filter = SerializerDetail.SET_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("set", source_database=endpoint_levels[level - 1])
        return super(SetTypeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("set", source_database=level_name)
        return queryset



class SetHandler(CustomView):
    level_description = 'Set level'
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
        set_counter = qs.values_list('source_database').annotate(total=Count('source_database'))
        return {"sets": {c[0]: c[1] for c in set_counter if c[0] != "node"}}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.reset_filters("set", endpoint_levels)

        return super(SetHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    # @staticmethod
    # def filter(queryset, level_name="", general_handler=None):
    #     general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
    #     return queryset
