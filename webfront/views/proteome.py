from webfront.models import Proteome
from webfront.serializers.proteome import ProteomeSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.views.modifiers import passing, add_extra_fields, filter_by_field, filter_by_boolean_field


class ProteomeAccessionHandler(CustomView):
    level_description = 'Proteome accession level'
    serializer_class = ProteomeSerializer
    queryset = Proteome.objects.all()
    many = False
    serializer_detail_filter = SerializerDetail.PROTEOME_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("proteome", accession=endpoint_levels[level - 1].lower())
        # self.serializer_detail = SerializerDetail.PROTEIN_DETAIL
        return super(ProteomeAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("proteome", accession=level_name.lower())
        return queryset


class UniprotHandler(CustomView):
    level_description = 'proteome db level'
    child_handlers = [
        (r'UP\d{9}', ProteomeAccessionHandler),
    ]
    queryset = Proteome.objects.all()
    serializer_class = ProteomeSerializer
    serializer_detail_filter = SerializerDetail.PROTEOME_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.main_endpoint = "proteome"
        self.serializer_detail = SerializerDetail.PROTEOME_HEADERS
        general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
        general_handler.modifiers.register(
            "extra_fields",
            add_extra_fields(Proteome, "counters"),
        )

        return super(UniprotHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
        return queryset


class ProteomeHandler(CustomView):
    level_description = 'Proteome level'
    from_model = False
    child_handlers = [
        ("uniprot", UniprotHandler),
    ]
    many = False
    serializer_class = ProteomeSerializer
    serializer_detail = SerializerDetail.PROTEOME_OVERVIEW
    serializer_detail_filter = SerializerDetail.PROTEOME_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Proteome.objects.filter(accession__in=queryset)
        return {"proteomes": {"uniprot": qs.count()}}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.modifiers.register("is_reference", filter_by_boolean_field("proteome",'is_reference'))
        general_handler.queryset_manager.reset_filters("proteome", endpoint_levels)

        return super(ProteomeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
        return queryset
