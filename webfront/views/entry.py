from django.db.models import Count

from webfront.models import Entry
from webfront.serializers.interpro import EntrySerializer
from .custom import CustomView, SerializerDetail
from django.conf import settings

db_members = '|'.join(settings.DB_MEMBERS)
db_members_accessions = (
    r'^({})$'.format('|'.join((db['accession'] for (_, db) in settings.DB_MEMBERS.items())))
)


def filter_entry_overview(obj, general_handler, endpoint):
    obj = EntryHandler.flat_counter_object(obj)

    for entry_db in obj:
        qm = general_handler.queryset_manager.clone()
        if entry_db == "unintegrated":
            qm.add_filter("entry",
                          integrated__isnull=True,
                          source_database__iregex=db_members)
        else:
            qm.add_filter("entry", source_database__iexact=entry_db)

        if not isinstance(obj[entry_db], dict):
            obj[entry_db] = {"entries": obj[entry_db]}
        obj[entry_db][general_handler.plurals[endpoint]] = qm.get_queryset(endpoint)\
            .values("accession")\
            .distinct().count()
    return EntryHandler.unflat_counter_object(obj)


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
    level_description = 'interpro accession level'
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
    level_description = 'section level'
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

    @staticmethod
    def get_database_contributions(queryset):
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
        return super(EntryHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers,
            level, self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        general_handler.queryset_manager.add_filter("entry", accession__isnull=False)

        return queryset

    @staticmethod
    def flat_counter_object(obj):
        obj = {**obj, **obj["member_databases"]}
        del obj["member_databases"]
        return obj

    @staticmethod
    def unflat_counter_object(obj):
        new_obj = {"member_databases": {}}
        for key, value in obj.items():
            if key == "interpro" or key == "unintegrated":
                new_obj[key] = value
            else:
                new_obj["member_databases"][key] = value
        obj = new_obj
        return obj
