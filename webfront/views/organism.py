from webfront.models import Taxonomy
from webfront.serializers.taxonomy import OrganismSerializer
from webfront.views.custom import CustomView


class OrganismHandler(CustomView):
    level_description = 'Organism level'
    from_model = False
    child_handlers = [
        # ("pdb", PDBHandler),
    ]
    many = False
    serializer_class = OrganismSerializer
    # serializer_detail = SerializerDetail.STRUCTURE_OVERVIEW
    # serializer_detail_filter = SerializerDetail.STRUCTURE_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Taxonomy.objects.filter(accession__in=queryset)
        # protein_counter = qs.values_list('source_database').annotate(total=Count('source_database'))
        # output = {"pdb": 0}
        # for (source_database, total) in protein_counter:
        #     output[source_database] = total
        return {"taxonomy": qs.count()}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.reset_filters("organism", endpoint_levels)

        return super(OrganismHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )
