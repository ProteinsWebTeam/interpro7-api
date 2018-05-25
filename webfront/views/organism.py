from webfront.models import Taxonomy, Proteome
from webfront.serializers.taxonomy import OrganismSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.views.modifiers import passing, add_extra_fields


class ProteomeAccessionHandler(CustomView):
    level_description = 'Proteome accession level'
    serializer_class = OrganismSerializer
    queryset = Proteome.objects.all()
    many = False
    serializer_detail_filter = SerializerDetail.ORGANISM_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("proteome", accession=endpoint_levels[level - 1].lower())
        self.serializer_detail = SerializerDetail.ORGANISM_PROTEOME
        return super(ProteomeAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("proteome", accession=level_name.lower())
        return queryset


class ProteomeHandler(CustomView):
    level_description = 'proteome level'
    child_handlers = [
        (r'UP\d{9}', ProteomeAccessionHandler),
        # (r'.+', IDAccessionHandler),
    ]
    queryset = Proteome.objects.all()
    serializer_class = OrganismSerializer
    serializer_detail_filter = SerializerDetail.ORGANISM_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.main_endpoint = "proteome"
        self.serializer_detail = SerializerDetail.ORGANISM_PROTEOME_HEADERS
        general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
        general_handler.modifiers.unregister("with_names")
        general_handler.modifiers.register(
            "extra_fields",
            add_extra_fields(Proteome, "counters"),
        )

        if "accession" in general_handler.queryset_manager.filters["taxonomy"]:
            tax_id = general_handler.queryset_manager.remove_filter("taxonomy", "accession")
            general_handler.queryset_manager.add_filter(
                "proteome",
                taxonomy__lineage__contains=" {} ".format(tax_id)
            )
        # if level == 2:
        #     # general_handler.queryset_manager.reset_filters("proteome", endpoint_levels)
        # else:
        #     if level == 4:
        #         self.many = False
        #     self.serializer_detail = SerializerDetail.ORGANISM_TAXONOMY_PROTEOME_HEADERS
        # general_handler.queryset_manager.add_filter("organism", source_database="pdb")
        return super(ProteomeHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("proteome", accession__isnull=False)
        return queryset


class TaxonomyAccessionHandler(CustomView):
    level_description = 'Taxonomy accession level'
    serializer_class = OrganismSerializer
    queryset = Taxonomy.objects.all()
    many = False
    child_handlers = [
        ("proteome", ProteomeHandler),
    ]
    serializer_detail_filter = SerializerDetail.ORGANISM_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("taxonomy", accession=endpoint_levels[level - 1].lower())
        general_handler.modifiers.register(
            "with_names", passing, serializer=SerializerDetail.TAXONOMY_DETAIL_NAMES
        )

        return super(TaxonomyAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("taxonomy", accession=level_name.lower())
        return queryset


class TaxonomyHandler(CustomView):
    level_description = 'taxonomy level'
    child_handlers = [
        (r'\d+', TaxonomyAccessionHandler),
        ("proteome", ProteomeHandler),
    ]
    queryset = Taxonomy.objects.all()
    serializer_class = OrganismSerializer
    serializer_detail = SerializerDetail.ORGANISM_HEADERS
    serializer_detail_filter = SerializerDetail.ORGANISM_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
        general_handler.modifiers.register(
            "extra_fields",
            add_extra_fields(Taxonomy, "counters"),
        )
        return super(TaxonomyHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
        return queryset


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
    serializer_detail_filter = SerializerDetail.ORGANISM_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Taxonomy.objects.filter(accession__in=queryset)
        qs2 = Proteome.objects.filter(taxonomy__in=qs)
        return {"organisms": {"taxonomy": qs.count(), "proteome": qs2.count()}}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.reset_filters("taxonomy", endpoint_levels)

        return super(OrganismHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
        return queryset
