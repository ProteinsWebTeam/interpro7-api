from interpro import settings
from webfront.constants import get_queryset_type
from webfront.models import Entry
from webfront.views.custom import CustomView
from webfront.views.entry import EntryHandler
from rest_framework import status
from webfront.views.protein import ProteinHandler
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
    http_method_names = ['get']
    level_description = 'home level'
    available_endpoint_handlers = [
        ('entry', EntryHandler),
        ('protein', ProteinHandler),
        ('structure', StructureHandler),
    ]
    child_handlers = []
    queryset = Entry.objects
    store = {}
    last_endpoint_level = None

    def get(self, request, url='', *args, **kwargs):
        self.store = {}
        self.post_serializers = {}
        self.filter_serializers = {}
        endpoint_levels = map_url_to_levels(url)

        self.set_in_store(GeneralHandler, "pagination", pagination_information(request))
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

    def set_in_store(self, handler_class, key, value):
        if handler_class not in self.store:
            self.store[handler_class] = {}
        self.store[handler_class][key] = value

    def get_from_store(self, handler_class, key):
        if handler_class not in self.store:
            raise IndexError("The general handler store doesn't have {} registered"
                             .format(handler_class))
        if key not in self.store[handler_class]:
            raise KeyError("The general handler store doesn't have the key {} registered under {}"
                           .format(key, handler_class))
        return self.store[handler_class][key]

    post_serializers = {}
    current_endpoint = None
    main_endpoint = None

    def register_post_serializer(self, post_serializer, value):
        if value in [e[0] for e in self.available_endpoint_handlers]:
            self.current_endpoint = value
            if len(self.post_serializers) == 0:
                self.main_endpoint = value
        if self.current_endpoint is not None:
            self.post_serializers[self.current_endpoint] = {
                "post_serializer": post_serializer,
                "value": value
            }

    def execute_post_serializers(self, data):
        for key in self.post_serializers:
            ps = self.post_serializers[key]
            data = ps["post_serializer"](data, ps["value"], self)
        return data

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
    def get_previous_queryset(self):
        try:
            prev_queryset = self.get_from_store(CustomView, "queryset_for_previous_count")
            qs_type = get_queryset_type(prev_queryset)
        except (IndexError, KeyError):
            qs_type = prev_queryset = None
        return prev_queryset, qs_type
