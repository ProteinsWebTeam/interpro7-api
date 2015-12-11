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

def wants_json(request):
    if 'json' in request.META.get('HTTP_ACCEPT', 'html').lower():
        return True
    if request.GET.get('format', 'html').lower() == 'json':
        return True
    return False


class GeneralHandler(CustomView):
    http_method_names = ['get']
    level = 0
    level_description = 'home level'
    child_handlers = {
        'entry': EntryHandler,
    }
    queryset = interpro.Entry.objects

    def get(self, request, url = '', *args, **kwargs):

        endpoint_levels = map_url_to_levels(url)
        json_response = wants_json(request)
        pagination = pagination_information(request)

        return super(GeneralHandler, self).get(
            request, endpoint_levels, json_response,
            pagination=pagination, *args, **kwargs
        )

        # if (len(endpoint_levels) == level):
        #     if (json_response):
        #         return self.get_json(endpoint_levels)
        #     else:
        #         return self.get_html(endpoint_levels)
        # else:
        #     section = endpoint_levels[0]
        #     if (section not in self.child_handlers):
        #         raise ValueError(
        #             '{} is not a valid section'.format(section)
        #         )
        #
        #     response = self.child_handlers[section].as_view()(
        #         request, endpoint_levels, json_response,
        #         section=section, *args, **kwargs
        #     )
        #     return response;

# def page_handler(request, *args):
#     print(request)
#     print(dir(request))
#     print(request.META.get('HTTP_ACCEPT'))
#     if (request.method != 'GET'):
#         print('not allowed')
#         return HttpResponseNotAllowed(['GET'])
#     if len(args) == 0:
#         return render(request, 'home.html')
#     else:
#         kwargs = map_args_to_kwargs(args)
#         print(kwargs)
#         return render(request, 'home.html')
