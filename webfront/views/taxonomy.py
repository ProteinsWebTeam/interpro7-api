from webfront.models import Taxonomy
from webfront.serializers.taxonomy import TaxonomySerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.views.modifiers import (
    passing,
    add_extra_fields,
    filter_by_key_species,
    filter_by_entry,
    filter_by_entry_db,
    filter_by_domain_architectures,
)


class TaxonomyAccessionHandler(CustomView):
    level_description = "Taxonomy accession level"
    serializer_class = TaxonomySerializer
    queryset = Taxonomy.objects.all()
    many = False
    serializer_detail_filter = SerializerDetail.TAXONOMY_DETAIL

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
            "taxonomy", accession__iexact=endpoint_levels[level - 1]
        )
        general_handler.modifiers.register(
            "with_names", passing, serializer=SerializerDetail.TAXONOMY_DETAIL_NAMES
        )
        general_handler.modifiers.register(
            "filter_by_entry",
            filter_by_entry,
            serializer=SerializerDetail.TAXONOMY_PER_ENTRY,
            use_model_as_payload=True,
        )
        general_handler.modifiers.register(
            "filter_by_entry_db",
            filter_by_entry_db,
            serializer=SerializerDetail.TAXONOMY_PER_ENTRY_DB,
            use_model_as_payload=True,
        )

        return super(TaxonomyAccessionHandler, self).get(
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
            "taxonomy", accession__iexact=level_name
        )
        return queryset


class UniprotHandler(CustomView):
    level_description = "taxonomy db level"
    child_handlers = [(r"\d+", TaxonomyAccessionHandler)]
    queryset = Taxonomy.objects.all()
    serializer_class = TaxonomySerializer
    serializer_detail = SerializerDetail.TAXONOMY_HEADERS
    serializer_detail_filter = SerializerDetail.TAXONOMY_DB

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
        general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Taxonomy, "counters")
        )
        general_handler.modifiers.register("key_species", filter_by_key_species)
        general_handler.modifiers.register(
            "ida",
            filter_by_domain_architectures,
            use_model_as_payload=True,
            serializer=SerializerDetail.TAXONOMY_HEADERS,
            many=True,
        )

        return super(UniprotHandler, self).get(
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
        general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
        return queryset


class TaxonomyHandler(CustomView):
    level_description = "Taxonomy level"
    from_model = False
    child_handlers = [("uniprot", UniprotHandler)]
    many = False
    serializer_class = TaxonomySerializer
    serializer_detail = SerializerDetail.TAXONOMY_OVERVIEW
    serializer_detail_filter = SerializerDetail.TAXONOMY_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Taxonomy.objects.filter(accession__in=queryset)
        return {"taxa": {"uniprot": qs.count()}}

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
        general_handler.queryset_manager.reset_filters("taxonomy", endpoint_levels)

        return super(TaxonomyHandler, self).get(
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
        general_handler.queryset_manager.add_filter("taxonomy", accession__isnull=False)
        return queryset
