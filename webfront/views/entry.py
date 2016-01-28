from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from .custom import CustomView
from webfront.active_sites import ActiveSites
from webfront.models import interpro, Clan, Pfama
from webfront.serializers.interpro import EntrySerializer
from webfront.serializers.pfam import ClanSerializer, PfamaSerializer


class PfamClanIDHandler(CustomView):
    level = 6
    level_description = 'Pfam clan ID level'
    serializer_class = ClanSerializer
    django_db = "pfam_ro"
    many = False

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = Clan.objects.all().filter(clan_acc=endpoint_levels[self.level-1])

        return super(PfamClanIDHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )


class ClanHandler(CustomView):
    level = 5
    level_description = 'Pfam clan level'
    child_handlers = {
        r'CL\d{4}': PfamClanIDHandler,
    }
    serializer_class = ClanSerializer
    django_db = "pfam_ro"

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = Clan.objects.all()

        return super(ClanHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )


class ActiveSitesHandler(CustomView):
    level = 6
    level_description = 'Pfam ID level',
    django_db = "pfam_ro"
    from_model = False
    many = False

    def get(self, request, endpoint_levels, *args, **kwargs):
        active_sites = ActiveSites(endpoint_levels[self.level-2])
        active_sites.load_from_db()
        active_sites.load_alignment()

        self.queryset = active_sites.proteins

        return Response(active_sites.proteins)
        # return super(ActiveSitesHandler, self).get(
        #     request, endpoint_levels, *args, **kwargs
        # )


class PfamIDHandler(CustomView):
    level = 5
    level_description = 'Pfam ID level',
    serializer_class = PfamaSerializer
    django_db = "pfam_ro"
    many = False
    child_handlers = {
        'active_sites': ActiveSitesHandler,
    }

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = Pfama.objects.all().filter(pfama_acc=endpoint_levels[self.level-1])

        return super(PfamIDHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )


class PfamHandler(CustomView):
    level = 4
    level_description = 'DB member level'
    child_handlers = {
        r'PF\d{5}': PfamIDHandler,
        'clan':     ClanHandler,
    }
    serializer_class = PfamaSerializer
    django_db = "pfam_ro"

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = Pfama.objects.all()

        return super(PfamHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )


class AccesionHandler(CustomView):
    level = 3
    level_description = 'interpro accession level'
    child_handlers = {
        'pfam': PfamHandler,
    }
    serializer_class = EntrySerializer

    def get(self, request, endpoint_levels, *args, **kwargs):
        # self.queryset = self.get_more(
        #     self.queryset.filter(entry_ac=endpoint_levels[self.level-1]),
        #     *request.GET.getlist('content')
        # )
        self.queryset = self.queryset.filter(entry_ac=endpoint_levels[self.level-1])

        return super(AccesionHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )


class AllHandler(CustomView):
    level = 3
    level_description = 'interpro accession level'
    child_handlers = {
        'pfam': PfamHandler,
    }


class UnintegratedHandler(CustomView):
    level = 3
    level_description = 'interpro accession level'
    child_handlers = {
        'pfam': PfamHandler,
    }


class InterproHandler(ListModelMixin, CustomView):
    level = 2
    level_description = 'interpro level'
    child_handlers = {
        r'IPR\d{6}':    AccesionHandler,
        'all':          AllHandler,
        'unintegrated': UnintegratedHandler,
    }
    serializer_class = EntrySerializer


class EntryHandler(CustomView):
    level = 1
    level_description = 'section level'
    child_handlers = {
        'interpro': InterproHandler,
    }
