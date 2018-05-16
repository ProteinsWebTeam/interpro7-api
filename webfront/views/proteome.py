from webfront.models import Proteome
from webfront.serializers.proteome import ProteomeSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.views.modifiers import passing, add_extra_fields

# class UniprotHandler(CustomView):
#     level_description = 'proteome db level'
#     child_handlers = [
#         # (r'UP\d{9}', ProteomeAccessionHandler),
#     ]
#     queryset = Proteome.objects.all()
#     serializer_class = OrganismSerializer
#     serializer_detail_filter = SerializerDetail.ORGANISM_DB
#
#     def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
#             parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
#         general_handler.queryset_manager.main_endpoint = "proteome"
#         self.serializer_detail = SerializerDetail.ORGANISM_PROTEOME_HEADERS
#         general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
#         general_handler.modifiers.unregister("with_names")
#         general_handler.modifiers.register(
#             "extra_fields",
#             add_extra_fields(Proteome, "counters"),
#         )
#
#         if "accession" in general_handler.queryset_manager.filters["taxonomy"]:
#             tax_id = general_handler.queryset_manager.remove_filter("taxonomy", "accession")
#             general_handler.queryset_manager.add_filter(
#                 "proteome",
#                 taxonomy__lineage__contains=" {} ".format(tax_id)
#             )
#         return super(ProteomeHandler, self).get(
#             request, endpoint_levels, available_endpoint_handlers, level,
#             self.queryset, handler, general_handler, *args, **kwargs
#         )
#
#     @staticmethod
#     def filter(queryset, level_name="", general_handler=None):
#         general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
#         return queryset

class ProteomeHandler(CustomView):
    level_description = 'Proteome level'
    from_model = False
    child_handlers = [
        # ("uniprot", UniprotHandler),
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

        general_handler.queryset_manager.reset_filters("proteome", endpoint_levels)

        return super(ProteomeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
        return queryset
