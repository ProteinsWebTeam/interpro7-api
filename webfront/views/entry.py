from urllib.error import URLError

from django.db.models import Count

from webfront.models import Entry
from webfront.serializers.interpro import EntrySerializer
from .custom import CustomView, SerializerDetail, is_single_endpoint
from django.conf import settings

db_members = '|'.join(settings.DB_MEMBERS)
db_members_accessions = (
    r'^({})$'.format('|'.join((db['accession'] for (_, db) in settings.DB_MEMBERS.items())))
)


class MemberAccessionHandler(CustomView):
    level_description = 'DB member accession level'
    serializer_class = EntrySerializer
    many = False
    serializer_detail_filter = SerializerDetail.ENTRY_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("entry", accession=endpoint_levels[level - 1].upper())
        return super(MemberAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset,
            handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("entry", accession=level_name.upper())
        return queryset


class MemberHandler(CustomView):
    level_description = 'DB member level'
    child_handlers = [
        (db_members_accessions, MemberAccessionHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("entry", source_database__iexact=endpoint_levels[level - 1])

        if endpoint_levels[level - 2] == "unintegrated":
            general_handler.queryset_manager.add_filter("entry", integrated__isnull=True)
        if endpoint_levels[level - 2] == "interpro":
            general_handler.queryset_manager.add_filter("entry", integrated__isnull=False)
        if level - 3 >= 0 and endpoint_levels[level - 3] == "interpro":
            general_handler.queryset_manager.add_filter("entry", integrated=endpoint_levels[level - 2])
            general_handler.queryset_manager.remove_filter("entry", "accession")

        return super(MemberHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset, handler,
            general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
            general_handler.queryset_manager.update_interpro_filter()
            general_handler.queryset_manager.add_filter("entry", source_database__iexact=level_name)
            return queryset


class AccessionHandler(CustomView):
    level_description = 'interpro accession level'
    child_handlers = [
        (db_members, MemberHandler)
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_DETAIL
    serializer_detail_filter = SerializerDetail.ENTRY_DETAIL
    queryset = Entry.objects
    many = False

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("entry", accession=endpoint_levels[level - 1].upper())
        return super(AccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset,
            handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("entry", accession=level_name.upper())


class UnintegratedHandler(CustomView):
    level_description = 'unintegrated level'
    queryset = Entry.objects.all() \
        .exclude(source_database__iexact="interpro") \
        .filter(integrated__isnull=True)
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB
    child_handlers = [
        (db_members, MemberHandler)
    ]

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("entry",
                                                    integrated__isnull=True,
                                                    source_database__iregex=db_members)
        return super(UnintegratedHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter(
            "entry",
            integrated__isnull=True,
            source_database__iregex=db_members)
        return queryset


class InterproHandler(CustomView):
    level_description = 'interpro level'
    queryset = Entry.objects.filter(source_database__iexact="interpro")
    child_handlers = [
        (r'IPR\d{6}', AccessionHandler),
        (db_members, MemberHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("entry",
                                                    source_database__iexact=endpoint_levels[level - 1])

        return super(InterproHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("entry", source_database__iexact=level_name)
        return queryset


class EntryHandler(CustomView):
    level_description = 'Entry level'
    from_model = False  # The object generated will be serialized as JSON, without checking the model
    child_handlers = [
        ('interpro', InterproHandler),
        ('unintegrated', UnintegratedHandler),
        (db_members, MemberHandler),
    ]
    many = False
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_OVERVIEW
    serializer_detail_filter = SerializerDetail.ENTRY_OVERVIEW

    def get_database_contributions(self, queryset):
        qs = Entry.objects.filter(accession__in=queryset)
        entry_counter = qs.values_list('source_database').annotate(total=Count('source_database'))
        output = {
            "interpro": 0,
            "unintegrated": 0,
            "member_databases": {}
        }
        for (source_database, total) in entry_counter:
            if source_database.lower() == "interpro":
                output["interpro"] += total
            else:
                output["member_databases"][source_database.lower()] = total

        output["unintegrated"] = qs \
            .exclude(**{'source_database__iexact': "interpro"}) \
            .filter(**{'integrated__isnull': True}).count()
        return {"entries": output}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.reset_filters("entry", endpoint_levels)
        general_handler.queryset_manager.add_filter("entry", accession__isnull=False)
        general_handler.modifiers.register("group_by", self.group_by,
                                           use_model_as_payload=True,
                                           serializer=SerializerDetail.GROUP_BY
                                           )
        general_handler.modifiers.register("type", self.filter_by_type)
        return super(EntryHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers,
            level, self.queryset, handler, general_handler, *args, **kwargs
        )

    def group_by(self, field, general_handler):
        wl = {
            "type": "entry_type",
            "integrated": "integrated",
            "source_database": "entry_db"
        }
        if field not in wl:
            raise URLError("{} is not a valid field to group entries by. Allowed fields : {}".format(
                field, ", ".join(wl.keys())
            ))
        if is_single_endpoint(general_handler):
            queryset = general_handler.queryset_manager.get_queryset().distinct()
            qs = Entry.objects.filter(accession__in=queryset)
            return qs.values_list(field).annotate(total=Count(field))
        else:
            searcher = CustomView.get_search_controller(general_handler.queryset_manager)
            result = searcher.get_grouped_object(
                general_handler.queryset_manager.main_endpoint, wl[field]
            )
            return result

    def filter_by_type(self, field, general_handler):
        general_handler.queryset_manager.add_filter(
            "entry",
            type__iexact=field
        )


    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        general_handler.queryset_manager.add_filter("entry", accession__isnull=False)

        return queryset
