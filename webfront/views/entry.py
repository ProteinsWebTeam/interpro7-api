from django.db.models import Count, QuerySet
from webfront.models import Entry, ProteinEntryFeature
from webfront.serializers.interpro import EntrySerializer
from .custom import CustomView, SerializerDetail

db_members = r'(pfam)|(smart)|(prosite_profiles)'


class MemberAccesionHandler(CustomView):
    level_description = 'DB member accession level'
    serializer_class = EntrySerializer
    many = False
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(accession__iexact=endpoint_levels[level-1])
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}"
                            .format(endpoint_levels[level-1], "/".join(endpoint_levels[:level-1])))
        return super(MemberAccesionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        return queryset.filter(entry=level_name)


class MemberHandler(CustomView):
    level_description = 'DB member level'
    child_handlers = [
        (r'PF\d{5}|SM\d{5}|PS\d{5}', MemberAccesionHandler),
        # 'clan':     ClanHandler,
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}

        if parent_queryset is not None and isinstance(parent_queryset, QuerySet):
            if endpoint_levels[level-2] == "unintegrated":
                self.queryset = parent_queryset.filter(integrated__isnull=True)
            else:
                self.queryset = Entry.objects.filter(integrated__in=parent_queryset)

        self.queryset = self.queryset.filter(source_database__iexact=endpoint_levels[level-1])

        return super(MemberHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        return ProteinEntryFeature.objects.filter(protein__in=queryset, entry__source_database__iexact=level_name)

class AccesionHandler(CustomView):
    level_description = 'interpro accession level'
    child_handlers = [
        (db_members, MemberHandler)
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_DETAIL
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN_DETAIL
    queryset = Entry.objects
    many = False

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(accession__iexact=endpoint_levels[level-1])
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}"
                            .format(endpoint_levels[level-1], endpoint_levels[level-2]))
        return super(AccesionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        return queryset.filter(entry=level_name)
        # TODO: Check this filter


class UnintegratedHandler(CustomView):
    level_description = 'interpro accession level'
    queryset = Entry.objects.all()\
        .exclude(source_database__iexact="interpro")\
        .filter(integrated__isnull=True)
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN
    child_handlers = [
        (db_members, MemberHandler)
    ]

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        qs = ProteinEntryFeature.objects \
            .filter(protein__in=queryset, entry__integrated__isnull=True) \
            .exclude(entry__source_database__iexact="interpro")
        if qs.count() == 0:
            raise ReferenceError("There are no entries of the type {} in this query".format(level_name))
        return qs


class InterproHandler(CustomView):
    level_description = 'interpro level'
    queryset = Entry.objects.filter(source_database__iexact="interpro")
    child_handlers = [
        (r'IPR\d{6}', AccesionHandler),
        (db_members, MemberHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        return ProteinEntryFeature.objects.filter(protein__in=queryset, entry__source_database__iexact="interpro")
#        return queryset.filter(entry__source_database__iexact="interpro")
    # TODO: Check this filter


class EntryHandler(CustomView):
    level_description = 'section level'
    from_model = False  # The object generated will be serialized as JSON, without checking the model
    child_handlers = [
        ('interpro', InterproHandler),
        ('unintegrated', UnintegratedHandler),
        (db_members, MemberHandler),
    ]
    serializer_detail_filter = SerializerDetail.ENTRY_OVERVIEW

    @staticmethod
    def get_database_contributions(queryset):
        entry_counter = queryset.values('source_database').annotate(total=Count('source_database'))
        output = {
            "interpro": 0,
            "unintegrated": 0,
            "member_databases": {}
        }
        for row in entry_counter:
            if row["source_database"].lower() == "interpro":
                output["interpro"] += row["total"]
            else:
                output["member_databases"][row["source_database"].lower()] = row["total"]

        output["unintegrated"] = queryset\
            .exclude(source_database__iexact="interpro")\
            .filter(integrated__isnull=True).count()
        return output

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        self.queryset = EntryHandler.get_database_contributions(Entry.objects.all())
        return super(EntryHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset, handler, general_handler, *args, **kwargs
        )
    # TODO: Check the filter option for endpoints combinations

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        general_handler.set_in_store(EntryHandler,
                                     "entry_count",
                                     EntryHandler.get_database_contributions(
                                         Entry.objects.filter(accession__in=queryset.values('proteinentryfeature__entry'))))
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj, list):
            obj["entries"] = general_handler.get_from_store(EntryHandler, "entry_count")
        return obj
