from django.db.models import Count
from webfront.models import Entry, ProteinEntryFeature
from webfront.serializers.interpro import EntrySerializer
from .custom import CustomView, SerializerDetail


# from webfront.active_sites import ActiveSites
# from webfront.models import Clan, Pfama, DwEntrySignature,DwEntry
#from webfront.serializers.interpro import EntryOverviewSerializer, EntryDWSerializer
#from webfront.serializers.pfam import ClanSerializer, PfamaSerializer

#
# class PfamClanIDHandler(CustomView):
#     level_description = 'Pfam clan ID level'
#     serializer_class = ClanSerializer
#     django_db = "pfam_ro"
#     many = False
#
#     def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, *args, **kwargs):
#         self.queryset = Clan.objects.all().filter(clan_acc=endpoint_levels[level-1])
#
#         return super(PfamClanIDHandler, self).get(
#             request, endpoint_levels, available_endpoint_handlers, level, *args, **kwargs
#         )
#
#
# class ClanHandler(CustomView):
#     level_description = 'Pfam clan level'
#     child_handlers = {
#         r'CL\d{4}': PfamClanIDHandler,
#     }
#     serializer_class = ClanSerializer
#     django_db = "pfam_ro"
#
#     def get(self, request, endpoint_levels, *args, **kwargs):
#
#         self.queryset = Clan.objects.all()
#
#         return super(ClanHandler, self).get(
#             request, endpoint_levels, *args, **kwargs
#         )
#
#
# class ActiveSitesHandler(CustomView):
#     level_description = 'Pfam ID level',
#     django_db = "pfam_ro"
#     from_model = False
#     many = False
#
#     def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, *args, **kwargs):
#         active_sites = ActiveSites(endpoint_levels[level-2])
#         active_sites.load_from_db()
#         active_sites.load_alignment()
#
#         self.queryset = active_sites.proteins
#
#         return Response(active_sites.proteins)
#         # return super(ActiveSitesHandler, self).get(
#         #     request, endpoint_levels, *args, **kwargs
#         # )
#
#
#     level_description = 'Pfam ID level'
#     serializer_class = EntrySerializer
#     many = False
#     # child_handlers = {
#     #     'active_sites': ActiveSitesHandler,
#     # }
#
#     def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, *args, **kwargs):
#
#         self.queryset = Pfama.objects.all().filter(pfama_acc=endpoint_levels[level-1])
#
#         return super(PfamIDHandler, self).get(
#             request, endpoint_levels, available_endpoint_handlers, level, *args, **kwargs
#         )
#
class MemberAccesionHandler(CustomView):
    level_description = 'DB member accession level'
    serializer_class = EntrySerializer
    many = False

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(accession__iexact=endpoint_levels[level-1])
        if self.queryset.count()==0:
            raise Exception("The ID '{}' has not been found in {}".format(endpoint_levels[level-1], "/".join(endpoint_levels[:level-1])))
        return super(MemberAccesionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset, handler, *args, **kwargs
        )


db_members = r'(pfam)|(smart)|(prosite_profiles)'

class MemberHandler(CustomView):
    level_description = 'DB member level'
    child_handlers = [
        (r'PF\d{5}|SM\d{5}|PS\d{5}', MemberAccesionHandler),
        # 'clan':     ClanHandler,
    ]
    serializer_class = EntrySerializer

    def get_queryset(self, endpoint_levels=None, level=None):
        if level is None or endpoint_levels is None:
            return super(MemberHandler, self).get_queryset()

        self.queryset = self.queryset.filter(source_database__iexact=endpoint_levels[level-1])
        if level == 3:
            if endpoint_levels[level-2] == "interpro":
                self.queryset = self.queryset.filter(integrated__isnull=False)
            elif endpoint_levels[level-2] == "unintegrated":
                self.queryset = self.queryset.filter(integrated__isnull=True)
        elif level == 4:
            self.queryset = self.queryset.filter(integrated=endpoint_levels[level-2])
        return self.queryset

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        parent_queryset = self.get_queryset(endpoint_levels,level)

        return super(MemberHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, parent_queryset, handler, *args, **kwargs
        )


class AccesionHandler(CustomView):
    level_description = 'interpro accession level'
    child_handlers = [
        (db_members, MemberHandler)
    ]
    serializer_class = EntrySerializer
    queryset = Entry.objects
    many = False

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        self.queryset = self.queryset.filter(accession=endpoint_levels[level-1])
        if self.queryset.count()==0:
            raise Exception("The ID '{}' has not been found in {}".format(endpoint_levels[level-1], endpoint_levels[level-2]))
        return super(AccesionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset, handler, *args, **kwargs
        )


class UnintegratedHandler(CustomView):
    level_description = 'interpro accession level'
    queryset = Entry.objects.all()\
        .exclude(source_database__iexact="interpro")\
        .filter(integrated__isnull=True)
    serializer_class = EntrySerializer
    child_handlers = [
        (db_members, MemberHandler)
    ]


class InterproHandler(CustomView):
    level_description = 'interpro level'
    queryset = Entry.objects.filter(source_database__iexact="interpro")
    child_handlers = [
        (r'IPR\d{6}',    AccesionHandler),
        (db_members, MemberHandler),
    ]
    serializer_class = EntrySerializer
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN_DETAIL

    @staticmethod
    def filter(queryset, level_name=""):
#        return queryset.filter(entry__source_database__iexact="interpro")
        return ProteinEntryFeature.objects.filter(protein__in=queryset, entry__source_database__iexact="interpro")
        # TOOO: what if the model has a


class EntryHandler(CustomView):
    level_description = 'section level'
    from_model = False
    child_handlers = [
        ('interpro', InterproHandler),
        ('unintegrated', UnintegratedHandler),
        (db_members, MemberHandler),
    ]
    serializer_detail_filter = SerializerDetail.ENTRY_OVERVIEW

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}

        entry_counter = Entry.objects.all()\
            .values('source_database')\
            .annotate(total=Count('source_database'))
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

        output["unintegrated"] = Entry.objects.all()\
            .exclude(source_database__iexact="interpro")\
            .filter(integrated__isnull=True).count()
        self.queryset = output
        return super(EntryHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, self.queryset, handler, *args, **kwargs
        )
