from webfront.models import interpro
from rest_framework.mixins import ListModelMixin

from webfront.serializers.interpro import EntrySerializer
from .custom import CustomView


class PfamClanIDHandler(CustomView):
    level = 6
    level_description = 'Pfam clan ID level'


class ClanHandler(CustomView):
    level = 5
    level_description = 'Pfam clan level'
    child_handlers = {
        r'CL\d{4}': PfamClanIDHandler,
    }


class PfamIDHandler(CustomView):
    level = 5
    level_description = 'Pfam ID level',


class PfamHandler(CustomView):
    level = 4
    level_description = 'DB member level'
    child_handlers = {
        r'PF\d{5}': PfamIDHandler,
        'clan':     ClanHandler,
    }


class AccesionHandler(CustomView):
    level = 3
    level_description = 'interpro accession level'
    child_handlers = {
        'pfam': PfamHandler,
    }
    multiple = False
    serializer_class = EntrySerializer

    def get(self, request, endpoint_levels, json_response, *args, **kwargs):
        # self.queryset = self.get_more(
        #     self.queryset.filter(entry_ac=endpoint_levels[self.level-1]),
        #     *request.GET.getlist('content')
        # )
        self.queryset = self.queryset.filter(entry_ac=endpoint_levels[self.level-1])


        return super(AccesionHandler, self).get(
            request, endpoint_levels, json_response, *args, **kwargs
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
