import re
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
        general_handler.queryset_manager.add_filter("entry", accession__iexact=endpoint_levels[level - 1])
        return super(MemberAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset,
            handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("entry", accession__iexact=level_name)
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
            from webfront.views.protein import filter_protein_overview
            from webfront.views.structure import filter_structure_overview
            if "structures" in obj:
                obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "entry")
            if "proteins" in obj:
                obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "entry")
            return obj
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["entry"] == level_name or
                                    (isinstance(e["entry"], dict) and e["entry"]["accession"] == level_name)]
                    if len(o["entries"]) == 0:
                        remove_empty_structures = True
            if remove_empty_structures:
                arr = [a for a in arr if len(a["entries"]) > 0]
                if len(arr) == 0:
                    raise ReferenceError("The entry {} doesn't exist in the selected url".format(level_name))
        return obj


class MemberHandler(CustomView):
    level_description = 'DB member level'
    child_handlers = [
        (db_members_accessions, MemberAccessionHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_MATCH

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.add_filter("entry", source_database__iexact=endpoint_levels[level - 1])

        if endpoint_levels[level - 2] == "unintegrated":
            general_handler.queryset_manager.add_filter("entry", integrated__isnull=True)
        if endpoint_levels[level - 2] == "interpro":
            general_handler.queryset_manager.add_filter("entry", integrated__isnull=False)
        if level - 3 >= 0 and endpoint_levels[level - 3] == "interpro":
            general_handler.queryset_manager.add_filter("entry", integrated=endpoint_levels[level - 2])
            general_handler.queryset_manager.remove_filter("entry", "accession__iexact")

        return super(MemberHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset, handler,
            general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        try:
            is_unintegrated = general_handler.get_from_store(UnintegratedHandler, "unintegrated")
        except (IndexError, KeyError):
            is_unintegrated = False
        try:
            is_interpro = general_handler.get_from_store(InterproHandler, "interpro")
        except (IndexError, KeyError):
            is_interpro = False
        try:
            interpro_acc = general_handler.get_from_store(AccessionHandler, "accession")
        except (IndexError, KeyError):
            interpro_acc = None
        general_handler.set_in_store(MemberHandler, "database", level_name)

        if isinstance(queryset, dict):
            if "entries" in queryset:
                del queryset["entries"]
        else:
            if is_unintegrated:
                general_handler.queryset_manager.add_filter("entry", integrated__isnull=True)
            elif interpro_acc is not None:
                general_handler.queryset_manager.add_filter("entry", integrated=interpro_acc)
                general_handler.queryset_manager.remove_filter("entry", "accession__iexact")
            elif is_interpro:
                general_handler.queryset_manager.add_filter("entry", integrated__isnull=False)
            general_handler.queryset_manager.add_filter("entry", source_database__iexact=level_name)
            return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
            from webfront.views.protein import filter_protein_overview
            from webfront.views.structure import filter_structure_overview
            if "structures" in obj:
                obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "entry")
            if "proteins" in obj:
                obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "entry")
            return obj
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            entries = [x[0]
                       for x in general_handler.queryset_manager.get_queryset("entry")
                       .values_list("accession").distinct()]
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["source_database"].lower() == level_name and
                                    (entries is None or e["accession"] in entries)
                                    ]
                    if len(o["entries"]) == 0:
                        remove_empty_structures = True
            if remove_empty_structures:
                arr = [a for a in arr if len(a["entries"]) > 0]
                if len(arr) == 0:
                    raise ReferenceError("The entry {} doesn't exist in the selected url".format(level_name))
        return obj


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

        general_handler.queryset_manager.add_filter("entry", accession__iexact=endpoint_levels[level - 1])
        return super(AccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset,
            handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.set_in_store(AccessionHandler, "accession", level_name)
        general_handler.queryset_manager.add_filter("entry", accession__iexact=level_name)

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
            from webfront.views.protein import filter_protein_overview
            from webfront.views.structure import filter_structure_overview
            if "structures" in obj:
                obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "entry")
            if "proteins" in obj:
                obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "entry")
            return obj
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["entry"] == level_name or
                                    (isinstance(e["entry"], dict) and e["entry"]["accession"] == level_name)]
                    if len(o["entries"]) == 0:
                        remove_empty_structures = True
            if remove_empty_structures:
                arr = [a for a in arr if len(a["entries"]) > 0]
                if len(arr) == 0:
                    raise ReferenceError("The entry {} doesn't exist in the selected url".format(level_name))
        return obj


class UnintegratedHandler(CustomView):
    level_description = 'interpro accession level'
    queryset = Entry.objects.all() \
        .exclude(source_database__iexact="interpro") \
        .filter(integrated__isnull=True)
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_MATCH
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
        general_handler.set_in_store(UnintegratedHandler, "unintegrated", True)
        if isinstance(queryset, dict):
            del queryset["entries"]
        else:
            general_handler.queryset_manager.add_filter(
                "entry",
                integrated__isnull=True,
                source_database__iregex=db_members)
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
            from webfront.views.protein import filter_protein_overview
            from webfront.views.structure import filter_structure_overview
            if "structures" in obj:
                obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "entry")
            if "proteins" in obj:
                obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "entry")
            return obj
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            entries = [x[0]
                       for x in general_handler.queryset_manager.get_queryset("entry")
                       .values_list("accession").distinct()]
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if re.match(db_members, e["source_database"], flags=re.IGNORECASE) and
                                    "integrated" not in e and
                                    e["accession"] in entries]
                    if len(o["entries"]) == 0:
                        remove_empty_structures = True
            if remove_empty_structures:
                arr = [a for a in arr if len(a["entries"]) > 0]
                if len(arr) == 0:
                    raise ReferenceError("The entry {} doesn't exist in the selected url".format(level_name))
        return obj


class InterproHandler(CustomView):
    level_description = 'interpro level'
    queryset = Entry.objects.filter(source_database__iexact="interpro")
    child_handlers = [
        (r'IPR\d{6}', AccessionHandler),
        (db_members, MemberHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_MATCH

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
        general_handler.set_in_store(InterproHandler, "interpro", True)
        general_handler.queryset_manager.add_filter("entry", source_database__iexact=level_name)
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
            from webfront.views.protein import filter_protein_overview
            from webfront.views.structure import filter_structure_overview
            if "structures" in obj:
                obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "entry")
            if "proteins" in obj:
                obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "entry")
            return obj

        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"] if e["source_database"].lower() == "interpro"]
                    if len(o["entries"]) == 0:
                        remove_empty_structures = True
            if remove_empty_structures:
                arr = [a for a in arr if len(a["entries"]) > 0]
                if len(arr) == 0:
                    raise ReferenceError("The entry {} doesn't exist in the selected url".format(level_name))
        return obj


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
        return output

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
    def post_serializer(obj, level_name="", general_handler=None, queryset=None):
        if general_handler.queryset_manager.main_endpoint != "entry":
            if isinstance(obj, dict):
                qs = general_handler.queryset_manager.get_queryset("entry")
                obj["entries"] = EntryHandler.get_database_contributions(qs)
            elif isinstance(obj, list):
                pc = general_handler.queryset_manager.group_and_count("entry")
                for item in obj:
                    item["entries"] = pc[item["metadata"]["accession"]]
        else:
            obj = {"entries": obj}
        return obj

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
