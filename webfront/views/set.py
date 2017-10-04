from django.db.models import Count

from webfront.models import Set
from webfront.serializers.collection import SetSerializer
from webfront.views.custom import CustomView, SerializerDetail

class SetAccessionHandler(CustomView):
    level_description = 'Set accession level'
    serializer_class = SetSerializer
    queryset = Set.objects.all()
    many = False
    child_handlers = [
        # ("proteome", ProteomeHandler),
    ]
    serializer_detail_filter = SerializerDetail.SET_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("set", accession=endpoint_levels[level - 1].upper())
        return super(SetAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    # @staticmethod
    # def filter(queryset, level_name="", general_handler=None):
    #     general_handler.queryset_manager.add_filter("taxonomy", accession=level_name.upper())
    #     return queryset

class SetTypeHandler(CustomView):
    level_description = 'set type level'
    child_handlers = [
        (r'.+', SetAccessionHandler),
        # ("proteome", ProteomeHandler),
    ]
    queryset = Set.objects.all()
    serializer_class = SetSerializer
    serializer_detail = SerializerDetail.SET_HEADERS
    # serializer_detail_filter = SerializerDetail.ORGANISM_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("set", source_database=endpoint_levels[level - 1])
        return super(SetTypeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    # @staticmethod
    # def filter(queryset, level_name="", general_handler=None):
    #     general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
    #     return queryset



class SetHandler(CustomView):
    level_description = 'Set level'
    from_model = False
    child_handlers = [
        (r'.+', SetTypeHandler),
        # ("proteome", ProteomeHandler),
    ]
    many = False
    serializer_class = SetSerializer
    serializer_detail = SerializerDetail.SET_OVERVIEW
    # serializer_detail_filter = SerializerDetail.ORGANISM_OVERVIEW

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