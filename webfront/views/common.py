from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed

from webfront.views.custom import CustomView
from webfront.views.entry import EntryHandler
from webfront.models import interpro


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
    level = 0
    level_description = 'home level'
    child_handlers = {
        'entry': EntryHandler,
    }
    queryset = interpro.Entry.objects

    def get(self, request, url='', *args, **kwargs):

        endpoint_levels = map_url_to_levels(url)
        pagination = pagination_information(request)

        return super(GeneralHandler, self).get(
            request, endpoint_levels,
            pagination=pagination, *args, **kwargs
        )
