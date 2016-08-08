import re
from django.db.models import Count, QuerySet

from webfront.constants import QuerysetType
from webfront.constants import get_queryset_type
from webfront.models import Entry, ProteinEntryFeature, EntryStructureFeature, Protein, Structure
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
    try:
        prev_queryset = general_handler.get_from_store(CustomView, "queryset_for_previous_count")
        qs_type = get_queryset_type(prev_queryset)
    except (IndexError, KeyError):
        qs_type = prev_queryset = None
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

    general_handler.set_in_store(CustomView, "queryset_for_previous_count", matches)

    entries = matches.values("entry")
    structs = matches.values("structure")
    if prev_queryset is not None:
        if qs_type == QuerysetType.STRUCTURE_PROTEIN:
            matches = matches.filter(structure__accession__in=prev_queryset.values("structure")) \
                .filter(entry__in=prev_queryset.values("protein__entry"))
            prev_queryset = prev_queryset.filter(structure__entrystructurefeature__in=matches)\
                .filter(protein__accession__in=matches.values("entry__protein"))

            structs = matches.values("structure")
            entries = matches.values("entry")
            prots = prev_queryset.values("protein")

            CustomView.set_counter_attributte(obj, "pdb", "proteins",
                                              prots.distinct().count())

    CustomView.set_counter_attributte(obj, "pdb", "structures",
                                      structs.distinct().count())
    CustomView.set_counter_attributte(obj, "pdb", "entries",
                                      entries.distinct().count())
    return obj


def filter_protein_overview(obj, general_handler, database=None, is_unintegrated=False, accession=None,
                            is_interpro=False, interpro_acc=None):
    try:
        prev_queryset = general_handler.get_from_store(CustomView, "queryset_for_previous_count")
        qs_type = get_queryset_type(prev_queryset)
    except (IndexError, KeyError):
        qs_type = prev_queryset = None
    matches = ProteinEntryFeature.objects.all()
    if is_unintegrated:
        matches = matches\
            .filter(entry__integrated__isnull=True)\
            .exclude(entry__source_database__iexact="interpro")
    if database is not None:
        matches = matches.filter(entry__source_database__iexact=database)
    if accession is not None:
        matches = matches.filter(entry=accession)
    if is_interpro :
        matches = matches.filter(entry__integrated__isnull=False)
    if interpro_acc is not None:
        matches = matches.filter(entry__integrated=interpro_acc)
    general_handler.set_in_store(CustomView, "queryset_for_previous_count", matches)

    for prot_db in obj:
        if prot_db != "uniprot":
            matches2 = matches.filter(protein__source_database__iexact=prot_db)
        else:
            matches2 = matches.all()
        prots = matches2.values("protein")
        entries = matches2.values("entry")
        if prev_queryset is not None:
            if qs_type == QuerysetType.STRUCTURE_PROTEIN:
                matches2 = matches2.filter(protein__in=prev_queryset.values('protein'))
                prots = matches2.values("protein")
                entries = Entry.objects \
                    .filter(accession__in=prev_queryset.values("protein__entry")) \
                    .filter(accession__in=matches2.values("entry"))
                structs = Structure.objects.filter(protein__in=prots, entry__in=entries)
                CustomView.set_counter_attributte(
                    obj, prot_db, "structures", structs.distinct().count())

        CustomView.set_counter_attributte(
            obj, prot_db, "proteins", prots.distinct().count())
        CustomView.set_counter_attributte(
            obj, prot_db, "entries", entries.distinct().count())
    return obj


class MemberAccesionHandler(CustomView):
    level_description = 'DB member accession level'
    serializer_class = EntrySerializer
    many = False
    serializer_detail_filter = SerializerDetail.ENTRY_DETAIL

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
            interpro_acc = general_handler.get_from_store(AccesionHandler, "accession")
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
        qs_type = get_queryset_type(queryset)
        if qs_type == QuerysetType.STRUCTURE:
            if is_unintegrated:
                queryset = queryset.filter(entry=level_name, entry__integrated__isnull=True)
            elif interpro_acc is not None:
                queryset = queryset.filter(entry=level_name, entry__integrated=interpro_acc)
            else:
                queryset = queryset.filter(entry=level_name, entrystructurefeature__chain__in=queryset.values('proteinstructurefeature__chain'),)
        if queryset.count() == 0:
            raise ReferenceError("There are no entries of the type {} in this query".format(level_name))
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if hasattr(obj, 'serializer'):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["entry"] == level_name or
                                    (isinstance(e["entry"], dict) and e["entry"]["accession"] == level_name)]
        return obj


class MemberHandler(CustomView):
    level_description = 'DB member level'
    child_handlers = [
        (db_members_accessions, MemberAccesionHandler),
        # 'clan':     ClanHandler,
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_MATCH

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
        try:
            is_unintegrated = general_handler.get_from_store(UnintegratedHandler, "unintegrated")
        except (IndexError, KeyError):
            is_unintegrated = False
        try:
            is_interpro = general_handler.get_from_store(InterproHandler, "interpro")
        except (IndexError, KeyError):
            is_interpro = False
        try:
            interpro_acc = general_handler.get_from_store(AccesionHandler, "accession")
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
            qs_type = get_queryset_type(queryset)
            qs = Entry.objects.all().filter(source_database__iexact=level_name)
            if is_unintegrated:
                qs = qs.filter(integrated__isnull=True)
            elif interpro_acc is not None:
                qs = qs.filter(integrated=interpro_acc)
            elif is_interpro:
                qs = qs.filter(integrated__isnull=False)

            general_handler.set_in_store(MemberHandler, "entries", [q["accession"] for q in qs.values("accession")])
            if qs_type == QuerysetType.PROTEIN:
                queryset = queryset.filter(entry__source_database__iexact=level_name,
                                           entry__in=qs).distinct()
            elif qs_type == QuerysetType.STRUCTURE:
                queryset = queryset.filter(
                    entrystructurefeature__chain__in=queryset.values('proteinstructurefeature__chain'),
                    entries__in=qs).distinct()

            if queryset.count() == 0:
                raise ReferenceError("There are no entries of the type {} in this query".format(level_name))
            return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if hasattr(obj, 'serializer'):
            try:
                entries = general_handler.get_from_store(MemberHandler, "entries")
            except IndexError:
                entries = Entry.objects.all()
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["source_database"] == level_name and e["accession"] in entries]
        return obj


class AccesionHandler(CustomView):
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
        general_handler.set_in_store(AccesionHandler, "accession", level_name)
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
        queryset = queryset.filter(entry=level_name)
        if queryset.count() == 0:
            raise ReferenceError("There are no entries of the type {} in this query".format(level_name))
        return queryset
    # TODO: Check this filter

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if hasattr(obj, 'serializer'):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if e["entry"] == level_name or
                                    (isinstance(e["entry"], dict) and e["entry"]["accession"] == level_name)]
        return obj


class UnintegratedHandler(CustomView):
    level_description = 'interpro accession level'
    queryset = Entry.objects.all()\
        .exclude(source_database__iexact="interpro")\
        .filter(integrated__isnull=True)
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_MATCH
    child_handlers = [
        (db_members, MemberHandler)
    ]

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
            qs_type = get_queryset_type(queryset)
            qs = queryset
            if qs_type == QuerysetType.PROTEIN:
                qs = queryset\
                    .filter(entry__integrated__isnull=True,
                            entry__source_database__iregex=db_members).distinct()
            elif qs_type == QuerysetType.STRUCTURE:
                qs = queryset \
                    .filter(entrystructurefeature__chain__in=queryset.values('proteinstructurefeature__chain'),
                            entries__integrated__isnull=True,
                            entries__source_database__iregex=db_members).distinct()
            if qs.count() == 0:
                raise ReferenceError("There are no entries of the type {} in this query".format(level_name))
            return qs

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if hasattr(obj, 'serializer'):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"]
                                    if re.match(db_members, e["source_database"]) and
                                    "integrated" not in e]
        return obj


class InterproHandler(CustomView):
    level_description = 'interpro level'
    queryset = Entry.objects.filter(source_database__iexact="interpro")
    child_handlers = [
        (r'IPR\d{6}', AccesionHandler),
        (db_members, MemberHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail = SerializerDetail.ENTRY_HEADERS
    serializer_detail_filter = SerializerDetail.ENTRY_MATCH

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.set_in_store(InterproHandler, "interpro", True)
        # TODO: Keep the filtered entries in the store.
        if isinstance(queryset, dict):
            del queryset["entries"]  # at this level (db) the counter is embedded in other endpoint.
            if "proteins" in queryset:
                queryset["proteins"] = filter_protein_overview(queryset["proteins"], general_handler, database="interpro")
            if "structures" in queryset:
                queryset["structures"] = filter_structure_overview(queryset["structures"], general_handler, "interpro")
            return queryset
        else:
            qs_type = get_queryset_type(queryset)
            qs = None
            if qs_type == QuerysetType.PROTEIN:
                qs = queryset.filter(
                    entry__source_database__iexact="interpro").distinct()
            elif qs_type == QuerysetType.STRUCTURE:
                qs = queryset.filter(
                    entrystructurefeature__chain__in=queryset.values('proteinstructurefeature__chain'),
                    entries__source_database__iexact="interpro").distinct()
            if qs is not None and qs.count() == 0:
                raise ReferenceError("There are no entries of the type {} in this query".format(level_name))
            return qs

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if hasattr(obj, 'serializer'):
            arr = [obj] if isinstance(obj, dict) else obj
            for o in arr:
                if "entries" in o:
                    o["entries"] = [e for e in o["entries"] if e["source_database"]=="interpro"]
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
        entry_counter = queryset.values(prefix+'source_database').annotate(total=Count(prefix+'source_database'))
        output = {
            "interpro": 0,
            "unintegrated": 0,
            "member_databases": {}
        }
        for row in entry_counter:
            if row[prefix+'source_database'].lower() == "interpro":
                output["interpro"] += row["total"]
            else:
                output["member_databases"][row[prefix+'source_database'].lower()] = row["total"]

        output["unintegrated"] = queryset\
            .exclude(**{prefix+'source_database__iexact': "interpro"}) \
            .filter(**{prefix+'integrated__isnull': True}).count()
        return output

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        self.queryset = {"entries": EntryHandler.get_database_contributions(Entry.objects.all())}
        return super(EntryHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers,
            level, self.queryset, handler, general_handler, *args, **kwargs
        )
    # TODO: Check the filter option for endpoints combinations

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        qs = Entry.objects.all()
        if isinstance(queryset, dict):
            queryset["entries"] = EntryHandler.get_database_contributions(qs)
        else:
            qs_type = get_queryset_type(queryset)
            if qs_type == QuerysetType.STRUCTURE:
                # TODO: Check on how to filter the chains.
                qs = Entry.objects.filter(accession__in=queryset.values('entrystructurefeature__entry'))
            elif qs_type == QuerysetType.PROTEIN:
                qs = Entry.objects.filter(accession__in=queryset.values('proteinentryfeature__entry'))

            general_handler.set_in_store(EntryHandler,
                                         "entry_count",
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
