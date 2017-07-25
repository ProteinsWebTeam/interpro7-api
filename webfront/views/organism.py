from webfront.models import Taxonomy, Proteome
from webfront.serializers.taxonomy import OrganismSerializer
from webfront.views.custom import CustomView, SerializerDetail


class TaxonomyAccessionHandler(CustomView):
    level_description = 'Taxonomy accession level'
    serializer_class = OrganismSerializer
    queryset = Taxonomy.objects.all()
    many = False
    child_handlers = [
        # (r'[a-zA-Z\d]{1,4}', ChainPDBAccessionHandler),
    ]
    serializer_detail_filter = SerializerDetail.ORGANISM_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("taxonomy", accession=endpoint_levels[level - 1].upper())
        return super(TaxonomyAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

class TaxonomyHandler(CustomView):
    level_description = 'taxonomy level'
    child_handlers = [
        (r'\d+', TaxonomyAccessionHandler),
        # (r'.+', IDAccessionHandler),
    ]
    queryset = Taxonomy.objects.all()
    serializer_class = OrganismSerializer
    serializer_detail = SerializerDetail.ORGANISM_HEADERS
    # serializer_detail_filter = SerializerDetail.STRUCTURE_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        # general_handler.queryset_manager.add_filter("organism", source_database="pdb")
        return super(TaxonomyHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

class ProteomeAccessionHandler(CustomView):
    level_description = 'Proteome accession level'
    serializer_class = OrganismSerializer
    queryset = Proteome.objects.all()
    many = False
    serializer_detail = SerializerDetail.ORGANISM_PROTEOME

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("proteome", accession=endpoint_levels[level - 1].upper())
        return super(ProteomeAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

class ProteomeHandler(CustomView):
    level_description = 'proteome level'
    child_handlers = [
        (r'UP\d{9}', ProteomeAccessionHandler),
        # (r'.+', IDAccessionHandler),
    ]
    queryset = Proteome.objects.all()
    serializer_class = OrganismSerializer
    serializer_detail = SerializerDetail.ORGANISM_PROTEOME_HEADERS
    # serializer_detail_filter = SerializerDetail.STRUCTURE_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        if level == 2:
            general_handler.queryset_manager.reset_filters("proteome", endpoint_levels)
        # general_handler.queryset_manager.add_filter("organism", source_database="pdb")
        return super(ProteomeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

class OrganismHandler(CustomView):
    level_description = 'Organism level'
    from_model = False
    child_handlers = [
        ("taxonomy", TaxonomyHandler),
        ("proteome", ProteomeHandler),
    ]
    many = False
    serializer_class = OrganismSerializer
    serializer_detail = SerializerDetail.ORGANISM_OVERVIEW
    # serializer_detail_filter = SerializerDetail.STRUCTURE_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Taxonomy.objects.filter(accession__in=queryset)
        qs2 = Proteome.objects.filter(taxonomy__in=qs)
        return {"taxonomy": qs.count(), "proteome": qs2.count()}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.reset_filters("taxonomy", endpoint_levels)

        return super(OrganismHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )
