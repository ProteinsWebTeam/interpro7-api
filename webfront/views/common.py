from interpro import settings
from webfront.models import Entry
from webfront.views.custom import CustomView
from webfront.views.entry import EntryHandler
from rest_framework import status
from webfront.views.protein import ProteinHandler
from webfront.views.queryset_manager import QuerysetManager
from webfront.views.structure import StructureHandler
from rest_framework.response import Response
import re


def map_url_to_levels(url):
    parts = [x.strip("/") for x in re.compile("(entry|protein|structure)").split(url)]

    new_url = parts[:3]
    for i in range(4, len(parts), 2):
        if parts[i] == "":
            new_url = new_url[:3] + parts[i-1:i+1] + new_url[3:]
        else:
            new_url += parts[i-1:i+1]

    return "/".join(filter(lambda a: len(a) != 0, new_url)).split("/")


def pagination_information(request):

    return {
        'index': int(request.GET.get('page', 1)),
        'size':  int(request.GET.get('page_size', 10)),
    }


class GeneralHandler(CustomView):
    # High level view for the API... all th request in the API start by instantiating this Handler
    # The URL gets evaluated blobk by block in the path (e.g. [block1]/[block2/...])
    # All the block handlers inherit from CustomView.
    # A recursion chain gets started at the get method of the GeneralHandler.
    #
    # The instance of this class is the only shared object among the view handlers that take
    # part on building the response, and therefore common functionality has been overloaded in it,
    # so it is accessible arounf the request procesing. (e.g. queryset management,

    http_method_names = ['get']
    level_description = 'home level'
    available_endpoint_handlers = [
        ('entry', EntryHandler),
        ('protein', ProteinHandler),
        ('structure', StructureHandler),
    ]
    plurals = {
        "entry": "entries",
        "protein": "proteins",
        "structure": "structures",
    }
    child_handlers = []
    queryset = Entry.objects
    last_endpoint_level = None
    queryset_manager = QuerysetManager()
    endpoint_levels = []
    pagination = None

    def get(self, request, url='', *args, **kwargs):
        # self.post_serializers = {}
        self.filter_serializers = {}
        self.endpoint_levels = endpoint_levels = map_url_to_levels(url)
        self.pagination = pagination_information(request)

        try:
            return super(GeneralHandler, self).get(
                request, endpoint_levels,
                available_endpoint_handlers=self.available_endpoint_handlers,
                level=0,
                parent_queryset=self.queryset,
                general_handler=self,
                *args, **kwargs
            )
        except ReferenceError as e:
            if settings.DEBUG:
                raise
            content = {'Error': e.args[0]}
            return Response(content, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            if settings.DEBUG:
                raise
            content = {'Error': e.args[0]}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    # post_serializers = {}
    # current_endpoint = None
    # main_endpoint = None
    #
    # def register_post_serializer(self, post_serializer, value):
    #     if value in [e[0] for e in self.available_endpoint_handlers]:
    #         self.current_endpoint = value
    #         if len(self.post_serializers) == 0:
    #             self.main_endpoint = value
    #     if self.current_endpoint is not None:
    #         self.post_serializers[self.current_endpoint] = {
    #             "post_serializer": post_serializer,
    #             "value": value
    #         }
    #
    # def execute_post_serializers(self, data):
    #     pss = list(self.post_serializers.items())
    #     pss.sort(key=lambda e: self.endpoint_levels.index(e[0]))
    #     for key, ps in pss:
    #         data = ps["post_serializer"](data, ps["value"], self)
    #     return data

    filter_serializers = {}
    current_filter_endpoint = None

    def register_filter_serializer(self, filter_serializer, value):
        if value in [e[0] for e in self.available_endpoint_handlers]:
            self.current_filter_endpoint = value
        if self.current_filter_endpoint is not None:
            self.filter_serializers[self.current_filter_endpoint] = {
                "filter_serializer": filter_serializer,
                "value": value
            }
