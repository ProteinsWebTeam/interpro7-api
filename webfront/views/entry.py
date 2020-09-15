from django.db.models import Count
from webfront.models.interpro_new import Release_Note

from webfront.exceptions import DeletedEntryError
from webfront.models import Entry
from webfront.serializers.interpro import EntrySerializer
from webfront.views.modifiers import (
    group_by,
    sort_by,
    filter_by_field,
    get_interpro_status_counter,
    filter_by_contains_field,
    get_domain_architectures,
    get_entry_annotation,
    get_entry_annotation_info,
    add_extra_fields,
    ida_search,
    filter_by_latest_entries,
    get_value_for_field,
)
from .custom import CustomView, SerializerDetail
from django.conf import settings

db_members = "|".join(settings.DB_MEMBERS)
db_members_accessions = r"^({})$".format(
    "|".join((db["accession"] for (_, db) in settings.DB_MEMBERS.items()))
)


class MemberAccessionHandler(CustomView):
    level_description = "DB member accession level"
    serializer_class = EntrySerializer
    many = False
    serializer_detail_filter = SerializerDetail.ENTRY_DETAIL

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
            "entry", accession__iexact=endpoint_levels[level - 1].lower()
        )

        general_handler.modifiers.register(
            "annotation",
            get_entry_annotation,
            use_model_as_payload=True,
            serializer=SerializerDetail.ANNOTATION_BLOB,
        )
        general_handler.modifiers.register(
            "annotation:info", get_entry_annotation_info, use_model_as_payload=True
        )
        general_handler.modifiers.register(
            "ida",
            get_domain_architectures,
            use_model_as_payload=True,
            serializer=SerializerDetail.IDA_LIST,
        )

        return super(MemberAccessionHandler, self).get(
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
            "entry", accession=level_name.lower()
        )
        return queryset


class MemberHandler(CustomView):
    level_description = "DB member level"
    child_handlers = [(db_members_accessions, MemberAccessionHandler)]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB

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
            "entry", source_database=endpoint_levels[level - 1].lower()
        )

        if endpoint_levels[level - 2] == "unintegrated":
            general_handler.queryset_manager.add_filter(
                "entry", integrated__isnull=True
            )
        if endpoint_levels[level - 2] == "interpro":
            general_handler.queryset_manager.add_filter(
                "entry", integrated__isnull=False
            )
        if level - 3 >= 0 and endpoint_levels[level - 3] == "interpro":
            general_handler.queryset_manager.add_filter(
                "entry",
                integrated__accession__iexact=endpoint_levels[level - 2].lower(),
            )
            general_handler.queryset_manager.remove_filter("entry", "accession__iexact")
        general_handler.modifiers.register(
            "group_by",
            group_by(
                Entry,
                {
                    "type": "entry_type",
                    "source_database": "entry_db",
                    "go_categories": "go_categories",
                    "go_terms": "go_terms",
                    "tax_id": "tax_id",
                },
            ),
            use_model_as_payload=True,
            # serializer=SerializerDetail.GROUP_BY_MEMBER_DATABASES
        )
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Entry, "counters")
        )

        general_handler.modifiers.register(
            "interpro_status", get_interpro_status_counter, use_model_as_payload=True
        )

        return super(MemberHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            parent_queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.update_integrated_filter("entry")
        general_handler.queryset_manager.add_filter(
            "entry", source_database=level_name.lower()
        )
        return queryset


class AccessionHandler(CustomView):
    level_description = "interpro accession level"
    child_handlers = [(db_members, MemberHandler)]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_DETAIL
    serializer_detail_filter = SerializerDetail.ENTRY_DETAIL
    queryset = Entry.objects
    many = False

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
        acc = endpoint_levels[level - 1].lower()
        general_handler.queryset_manager.add_filter("entry", accession__iexact=acc)

        # Checking if the entry has been marked as deleted
        general_handler.queryset_manager.add_filter("entry", is_alive=False)
        qs = general_handler.queryset_manager.get_queryset()
        if qs.count() > 0:
            first = qs.first()
            date = first.deletion_date
            history = first.history
            raise DeletedEntryError(
                acc,
                date,
                "The entry {} is not active. Removed: {}".format(acc, date),
                history,
            )
        general_handler.queryset_manager.add_filter("entry", is_alive=True)

        general_handler.modifiers.register(
            "ida",
            get_domain_architectures,
            use_model_as_payload=True,
            serializer=SerializerDetail.IDA_LIST,
        )
        general_handler.modifiers.register(
            "interactions",
            get_value_for_field("interactions"),
            use_model_as_payload=True,
        )
        general_handler.modifiers.register(
            "pathways", get_value_for_field("pathways"), use_model_as_payload=True
        )

        return super(AccessionHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            parent_queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter(
            "entry", accession=level_name.lower()
        )


class UnintegratedHandler(CustomView):
    level_description = "unintegrated level"
    queryset = (
        Entry.objects.all()
        .exclude(source_database="interpro")
        .filter(integrated__isnull=True)
    )
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB
    child_handlers = [(db_members, MemberHandler)]

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
            "entry", integrated__isnull=True, source_database__iregex=db_members
        )
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Entry, "counters")
        )
        return super(UnintegratedHandler, self).get(
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
            "entry", integrated__isnull=True, source_database__iregex=db_members
        )
        return queryset


class IntegratedHandler(CustomView):
    level_description = "integrated level"
    queryset = (
        Entry.objects.all()
        .exclude(source_database="interpro")
        .filter(integrated__isnull=False)
    )
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB
    child_handlers = [(db_members, MemberHandler)]

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
            "entry", integrated__isnull=False, source_database__iregex=db_members
        )
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Entry, "counters")
        )
        return super(IntegratedHandler, self).get(
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
            "entry", integrated__isnull=False, source_database__iregex=db_members
        )
        return queryset


class InterproHandler(CustomView):
    level_description = "interpro level"
    queryset = Entry.objects.filter(source_database="interpro")
    child_handlers = [(r"IPR\d{6}", AccessionHandler), (db_members, MemberHandler)]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB

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
            "entry", source_database=endpoint_levels[level - 1].lower()
        )

        general_handler.modifiers.register(
            "group_by",
            group_by(
                Entry,
                {
                    "type": "entry_type",
                    "tax_id": "tax_id",
                    "source_database": "entry_db",
                    "member_databases": "",
                    "go_categories": "go_categories",
                    "go_terms": "text",
                },
            ),
            use_model_as_payload=True,
            # serializer=SerializerDetail.GROUP_BY_MEMBER_DATABASES
        )
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Entry, "counters")
        )
        general_handler.modifiers.register(
            "signature_in",
            filter_by_contains_field("entry", "member_databases", '"{}"'),
            works_in_multiple_endpoint=False,
        )
        general_handler.modifiers.register("latest_entries", filter_by_latest_entries)
        return super(InterproHandler, self).get(
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
            "entry", source_database=level_name.lower()
        )
        return queryset


class AllHandler(CustomView):
    level_description = "all level"
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB
    child_handlers = [("interpro", InterproHandler), (db_members, MemberHandler)]

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
            "entry", source_database__isnull=False
        )
        general_handler.modifiers.register(
            "extra_fields", add_extra_fields(Entry, "counters")
        )
        return super(AllHandler, self).get(
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
            "entry", source_database__isnull=False
        )
        return queryset


class EntryHandler(CustomView):
    level_description = "Entry level"
    from_model = (
        False
    )  # The object generated will be serialized as JSON, without checking the model
    child_handlers = [
        ("all", AllHandler),
        ("interpro", InterproHandler),
        ("unintegrated", UnintegratedHandler),
        ("integrated", IntegratedHandler),
        (db_members, MemberHandler),
    ]
    many = False
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_OVERVIEW
    serializer_detail_filter = SerializerDetail.ENTRY_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Entry.objects.filter(accession__in=queryset)
        entry_counter = qs.values_list("source_database").annotate(
            total=Count("source_database")
        )
        output = {"interpro": 0, "unintegrated": 0, "member_databases": {}}
        for (source_database, total) in entry_counter:
            if source_database.lower() == "interpro":
                output["interpro"] += total
            else:
                output["member_databases"][source_database.lower()] = total

        output["unintegrated"] = (
            qs.exclude(**{"source_database": "interpro"})
            .filter(**{"integrated__isnull": True})
            .count()
        )
        output["all"] = qs.count()
        return {"entries": output}

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
        general_handler.queryset_manager.reset_filters("entry", endpoint_levels)
        general_handler.queryset_manager.add_filter("entry", accession__isnull=False)
        general_handler.queryset_manager.add_filter("entry", is_alive=True)
        general_handler.modifiers.register(
            "group_by",
            group_by(
                Entry,
                {
                    "type": "entry_type",
                    "source_database": "entry_db",
                    "tax_id": "tax_id",
                    "go_terms": "text",
                },
            ),
            use_model_as_payload=True,
            serializer=SerializerDetail.GROUP_BY,
        )
        general_handler.modifiers.register(
            "sort_by",
            sort_by(
                {"accession": "entry_acc", "integrated": "integrated", "name": None}
            ),
        )
        general_handler.modifiers.register("type", filter_by_field("entry", "type"))
        general_handler.modifiers.register(
            "integrated", filter_by_field("entry", "integrated__accession")
        )
        general_handler.modifiers.register(
            "go_category", filter_by_contains_field("entry", "go_terms", '"code": "{}"')
        )
        general_handler.modifiers.register(
            "go_term",
            filter_by_contains_field("entry", "go_terms", '"identifier": "{}"'),
        )
        general_handler.modifiers.register(
            "annotation",
            filter_by_contains_field("entry", "entryannotation__type"),
            use_model_as_payload=False,
        )
        general_handler.modifiers.register(
            "ida_search",
            ida_search,
            use_model_as_payload=True,
            serializer=SerializerDetail.IDA_LIST,
        )
        response = super(EntryHandler, self).get(
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
        return response

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("entry", accession__isnull=False)
        general_handler.queryset_manager.add_filter("entry", is_alive=True)
        return queryset
