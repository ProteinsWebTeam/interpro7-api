import re
from django.db.models import Count

from webfront.constants import QuerysetType
from webfront.constants import get_queryset_type
from webfront.models import Entry, ProteinEntryFeature, EntryStructureFeature
from webfront.serializers.interpro import EntrySerializer
from .custom import CustomView, SerializerDetail
from django.conf import settings

members = settings.DB_MEMBERS
db_members = '|'.join(members)
db_members_accessions = (
    r'^({})$'.format('|'.join((db['accession'] for (_, db) in members.items())))
)


def filter_structure_overview(obj, general_handler, database=None, is_unintegrated=False, accession=None,
                              is_interpro=False, interpro_acc=None):
    prev_queryset, qs_type = general_handler.get_previous_queryset()
    matches = EntryStructureFeature.objects.all()
    if is_unintegrated:
        matches = matches \
            .filter(entry__integrated__isnull=True) \
            .exclude(entry__source_database__iexact="interpro")
    if database is not None:
        matches = matches.filter(entry__source_database__iexact=database)
    if accession is not None:
        matches = matches.filter(entry=accession)
    if is_interpro:
        matches = matches.filter(entry__integrated__isnull=False)
    if interpro_acc is not None:
        matches = matches.filter(entry__integrated=interpro_acc)

    entries = matches.values("entry")
    structs = matches.values("structure")
    include_prots = False
    if prev_queryset is not None:
        if qs_type == QuerysetType.STRUCTURE_PROTEIN:
            matches = matches.filter(structure__accession__in=prev_queryset.values("structure")) \
                .filter(entry__in=prev_queryset.values("protein__entry"))
            include_prots = True
        elif qs_type == QuerysetType.ENTRY_STRUCTURE:
            matches = matches.all() & prev_queryset.all()
            include_prots = True
        structs = matches.values("structure")
        entries = matches.values("entry")
        if include_prots:
            prots = set(matches.values_list("entry__protein__accession")) \
                .intersection(matches.values_list("structure__protein__accession"))
            CustomView.set_counter_attributte(obj, "pdb", "proteins", len(prots))

    general_handler.set_in_store(CustomView, "queryset_for_previous_count", matches)

    CustomView.set_counter_attributte(obj, "pdb", "structures",
                                      structs.distinct().count())
    CustomView.set_counter_attributte(obj, "pdb", "entries",
                                      entries.distinct().count())
    return obj


def filter_protein_overview(obj, general_handler, database=None, is_unintegrated=False, accession=None,
                            is_interpro=False, interpro_acc=None):
    prev_queryset, qs_type = general_handler.get_previous_queryset()
    matches = ProteinEntryFeature.objects.all()
    if is_unintegrated:
        matches = matches \
            .filter(entry__integrated__isnull=True) \
            .exclude(entry__source_database__iexact="interpro")
    if database is not None:
        matches = matches.filter(entry__source_database__iexact=database)
    if accession is not None:
        matches = matches.filter(entry=accession)
    if is_interpro:
        matches = matches.filter(entry__integrated__isnull=False)
    if interpro_acc is not None:
        matches = matches.filter(entry__integrated=interpro_acc)

    if prev_queryset is not None:
        if qs_type == QuerysetType.STRUCTURE_PROTEIN:
            matches = matches.filter(protein__proteinstructurefeature__in=prev_queryset) \
                .filter(entry__accession__in=prev_queryset.values("structure__entry"))
        elif qs_type == QuerysetType.ENTRY_PROTEIN:
            matches = matches.all() & prev_queryset.all()

    general_handler.set_in_store(CustomView, "queryset_for_previous_count", matches)

    for prot_db in obj:
        matches2 = matches.all()
        if prot_db != "uniprot":
            matches2 = matches.filter(protein__source_database__iexact=prot_db)
        prots = matches2.values("protein")
        entries = matches2.values("entry")

        if prev_queryset is not None and (qs_type == QuerysetType.STRUCTURE_PROTEIN or
                                          qs_type == QuerysetType.ENTRY_PROTEIN):
            structs = set(matches2.values_list("entry__structure__accession")) \
                .intersection(matches2.values_list("protein__structure__accession"))
            CustomView.set_counter_attributte(obj, prot_db, "structures", len(structs))

        CustomView.set_counter_attributte(obj, prot_db, "proteins", prots.distinct().count())
        CustomView.set_counter_attributte(obj, prot_db, "entries", entries.distinct().count())
    return obj


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
        try:
            is_unintegrated = general_handler.get_from_store(UnintegratedHandler, "unintegrated")
        except (IndexError, KeyError):
            is_unintegrated = False
        try:
            is_interpro = general_handler.get_from_store(InterproHandler, "interpro")
        except (IndexError, KeyError):
            is_interpro = False
        try:
            database = general_handler.get_from_store(MemberHandler, "database")
        except (IndexError, KeyError):
            database = None
        try:
            interpro_acc = general_handler.get_from_store(AccessionHandler, "accession")
        except (IndexError, KeyError):
            interpro_acc = None
        if isinstance(queryset, dict):
            if "proteins" in queryset:
                queryset["proteins"] = filter_protein_overview(
                    queryset["proteins"], general_handler,
                    database=database,
                    accession=level_name,
                    is_unintegrated=is_unintegrated,
                    interpro_acc=interpro_acc,
                    is_interpro=is_interpro)
            if "structures" in queryset:
                queryset["structures"] = filter_structure_overview(
                    queryset["structures"], general_handler,
                    database=database,
                    accession=level_name,
                    is_unintegrated=is_unintegrated,
                    interpro_acc=interpro_acc,
                    is_interpro=is_interpro)
            return queryset
        general_handler.queryset_manager.add_filter("entry", accession__iexact=level_name)
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
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

        # if parent_queryset is not None and isinstance(parent_queryset, QuerySet):
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

            if "proteins" in queryset:
                queryset["proteins"] = filter_protein_overview(queryset["proteins"], general_handler,
                                                               database=level_name,
                                                               is_unintegrated=is_unintegrated,
                                                               interpro_acc=interpro_acc,
                                                               is_interpro=is_interpro)
            if "structures" in queryset:
                queryset["structures"] = filter_structure_overview(queryset["structures"], general_handler,
                                                                   database=level_name,
                                                                   is_unintegrated=is_unintegrated,
                                                                   interpro_acc=interpro_acc,
                                                                   is_interpro=is_interpro)
            return queryset
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
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            entries = [x[0]
                       for x in general_handler.queryset_manager.get_queryset("entry")
                       .values_list("accession").distinct()]
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["source_database"] == level_name and
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
        if isinstance(queryset, dict):
            if "proteins" in queryset:
                queryset["proteins"] = filter_protein_overview(queryset["proteins"], general_handler,
                                                               database="interpro",
                                                               accession=level_name)
            if "structures" in queryset:
                queryset["structures"] = filter_structure_overview(queryset["structures"], general_handler,
                                                                   database="interpro",
                                                                   accession=level_name)
            return queryset
        general_handler.queryset_manager.add_filter("entry", accession__iexact=level_name)

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
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
            if "proteins" in queryset:
                queryset["proteins"] = filter_protein_overview(queryset["proteins"], general_handler,
                                                               is_unintegrated=True)
            if "structures" in queryset:
                queryset["structures"] = filter_structure_overview(queryset["structures"], general_handler,
                                                                   is_unintegrated=True)
            return queryset
        else:
            general_handler.queryset_manager.add_filter(
                "entry",
                integrated__isnull=True,
                source_database__iregex=db_members)
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            entries = [x[0]
                       for x in general_handler.queryset_manager.get_queryset("entry")
                       .values_list("accession").distinct()]
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if re.match(db_members, e["source_database"]) and
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
        if isinstance(queryset, dict):
            del queryset["entries"]  # at this level (db) the counter is embedded in other endpoint.
            if "proteins" in queryset:
                queryset["proteins"] = filter_protein_overview(queryset["proteins"], general_handler,
                                                               database="interpro")
            if "structures" in queryset:
                queryset["structures"] = filter_structure_overview(queryset["structures"], general_handler,
                                                                   "interpro")
            return queryset
        else:
            general_handler.queryset_manager.add_filter("entry",
                                                        source_database__iexact=level_name)
            return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        remove_empty_structures = False
        if hasattr(obj, 'serializer') or isinstance(obj, list):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"] if e["source_database"] == "interpro"]
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
    def get_database_contributions(queryset, prefix=""):
        entry_counter = queryset.values(prefix + 'source_database').annotate(total=Count(prefix + 'source_database'))
        output = {
            "interpro": 0,
            "unintegrated": 0,
            "member_databases": {}
        }
        for row in entry_counter:
            if row[prefix + 'source_database'].lower() == "interpro":
                output["interpro"] += row["total"]
            else:
                output["member_databases"][row[prefix + 'source_database'].lower()] = row["total"]

        output["unintegrated"] = queryset \
            .exclude(**{prefix + 'source_database__iexact': "interpro"}) \
            .filter(**{prefix + 'integrated__isnull': True}).count()
        return output

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.reset_filters("entry")
        self.queryset = {"entries": EntryHandler.get_database_contributions(Entry.objects.all())}
        return super(EntryHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers,
            level, self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        queryset_tmp = general_handler.queryset_manager.get_queryset()
        qs = Entry.objects.all()
        if isinstance(queryset, dict):
            queryset["entries"] = EntryHandler.get_database_contributions(qs)
        else:
            qs_type = get_queryset_type(queryset_tmp)
            if qs_type == QuerysetType.STRUCTURE:
                # TODO: Check on how to filter the chains.
                qs = Entry.objects.filter(accession__in=queryset_tmp.values('entrystructurefeature__entry'))
            elif qs_type == QuerysetType.PROTEIN:
                qs = Entry.objects.filter(accession__in=queryset_tmp.values('proteinentryfeature__entry'))

            general_handler.set_in_store(EntryHandler, "entry_count",
                                         EntryHandler.get_database_contributions(qs))

        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj, list):
            try:
                obj["entries"] = general_handler.get_from_store(EntryHandler, "entry_count")
            finally:
                return obj
        return obj
