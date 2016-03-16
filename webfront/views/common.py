from unifam import settings
from webfront.models import Entry
from webfront.views.custom import CustomView
from webfront.views.entry import EntryHandler
from rest_framework import status
from webfront.views.protein import ProteinHandler
# from webfront.models import interpro
# from webfront.views.structure import StructureHandler
from rest_framework.response import Response

def map_url_to_levels(url):
    return list(
        filter(lambda a: len(a) != 0, url.split('/'))
    )


def pagination_information(request):

    return {
        'index': int(request.GET.get('page', 1)),
        'size':  int(request.GET.get('page_size', 10)),
    }


class GeneralHandler(CustomView):
    http_method_names = ['get']
    level_description = 'home level'
    available_endpoint_handlers = [
        ('entry', EntryHandler),
        ('protein', ProteinHandler),
        # 'structure': StructureHandler,
    ]
    child_handlers = []
    queryset = Entry.objects

    def get(self, request, url='', *args, **kwargs):

        endpoint_levels = map_url_to_levels(url)
        pagination = pagination_information(request)

        try:
            return super(GeneralHandler, self).get(
                request, endpoint_levels,
                pagination=pagination,
                available_endpoint_handlers=self.available_endpoint_handlers,
                level=0,
                parent_queryset = self.queryset,
                *args, **kwargs
            )
        except Exception as e:
            if settings.DEBUG:
                raise
            content = {'Error': e.args[0]}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
