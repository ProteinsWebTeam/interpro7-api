import re
import os
import logging

from rest_framework import status

from webfront.exceptions import DeletedEntryError, EmptyQuerysetError
from webfront.response import Response

from django.conf import settings
from django.http import HttpRequest
from rest_framework.request import Request
from webfront.views.custom import CustomView
from webfront.views.modifier_manager import ModifierManager
from webfront.views.queryset_manager import QuerysetManager
from webfront.searcher.elastic_controller import ElasticsearchController
from webfront.views.entry import EntryHandler
from webfront.views.protein import ProteinHandler
from webfront.views.structure import StructureHandler
from webfront.views.taxonomy import TaxonomyHandler
from webfront.views.proteome import ProteomeHandler
from webfront.views.set import SetHandler
from webfront.views.utils import UtilsHandler
from webfront.views.cache import InterProCache

from webfront.models import Database
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from time import sleep

QUERY_TIMEOUT = settings.INTERPRO_CONFIG.get('query_timeout', 90)
CACHE_TIMEOUT = settings.INTERPRO_CONFIG.get('cache_volatile_key_ttl', 1800)
logger = logging.getLogger(__name__)


def map_url_to_levels(url):
    parts = [x.strip("/") for x in re.compile("(entry|protein|structure|taxonomy|proteome|set)").split(url)]

    new_url = parts[:3]
    for i in range(4, len(parts), 2):
        if parts[i] == "":
            new_url = new_url[:3] + parts[i - 1:i + 1] + new_url[3:]
        else:
            new_url += parts[i - 1:i + 1]

    return "/".join(filter(lambda a: len(a) != 0, new_url)).split("/")


def pagination_information(request):
    # Extracts the pagination parameters out of the URL and returns a dictionary.
    return {
        "index": int(request.GET.get("page", 1)),
        "size": int(request.GET.get(
            "page_size",
            settings.INTERPRO_CONFIG.get('default_page_size', 20)
        )),
    }


def getDataForRoot(handlers):
    return {
        "endpoints": [x[0] for x in handlers],
        "databases": {
            db["name"].lower(): {
                "canonical": db["name"],
                "name": db["name_long"],
                "description": db["description"],
                "version": db["version"],
                "releaseDate": db["release_date"],
                "type": db["type"],
            } for db in Database.objects.order_by("type")
            .values("name", "name_long", "description", "version", "release_date", "type")
        },
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

    # Human readable description for logging purposes
    level_description = 'home level'

    # A valid URL on the API can only use an endpoint of this list *once*.
    # This list contains the endpoint that haven't been used yet in this request.
    # Been this view the root handler, all the endpoints are available.
    available_endpoint_handlers = [
        ('entry', EntryHandler),
        ('protein', ProteinHandler),
        ('structure', StructureHandler),
        ('taxonomy', TaxonomyHandler),
        ('proteome', ProteomeHandler),
        ('set', SetHandler),
        ('utils', UtilsHandler),
    ]
    # The queryset manager for the current request.
    queryset_manager = QuerysetManager()
    # Pagination information from the URL
    pagination = None
    # The modifier manager for the current request
    modifiers = ModifierManager()
    searcher = None
    filter_serializers = {}
    current_filter_endpoint = None

    cache = InterProCache()

    def get(self, request, url='', *args, **kwargs):
        clean_url = url.strip()
        if clean_url == '' or clean_url == '/':
            return Response(getDataForRoot(self.available_endpoint_handlers))
        full_path = request.get_full_path()
        response = None
        caching_allowed = settings.INTERPRO_CONFIG.get('enable_caching', False)
        if caching_allowed:
            try:
                response = self.cache.get(full_path)
            except Exception as e:
                if "TRAVIS" not in os.environ:
                    logger.error('Failed getting {} from cache: {}'.format(full_path, e))
        if response:
            return response

        self.filter_serializers = {}
        self.pagination = pagination_information(request)
        endpoint_levels = map_url_to_levels(url)
        self.modifiers = ModifierManager(self)
        self.modifiers.register("search", self.search_modifier)
        self.queryset_manager = QuerysetManager()
        self.searcher = self.get_search_controller(self.queryset_manager)
        try:
            def query(args):
                self, request, endpoint_levels, full_path, drf_request, caching_allowed = args
                response = super(GeneralHandler, self, ).get(
                    request, endpoint_levels,
                    available_endpoint_handlers=self.available_endpoint_handlers,
                    level=0,
                    parent_queryset=self.queryset,
                    general_handler=self,
                    drf_request=drf_request,
                )
                self._set_in_cache(caching_allowed, full_path, response)
                return response

            def timer(caching_allowed):
                sleep(QUERY_TIMEOUT)
                content = {'detail': 'Query timed out'}
                response = Response(content, status=status.HTTP_408_REQUEST_TIMEOUT)
                return response

            drf_request = request
            if caching_allowed:
                pool = ThreadPoolExecutor(2)
                futures = [
                    pool.submit(query,
                                (self, request._request, endpoint_levels, full_path, drf_request, caching_allowed)),
                    pool.submit(timer, caching_allowed),
                ]
                result = wait(futures, return_when=FIRST_COMPLETED)
                response = result.done.pop().result()
                if response.status_code == status.HTTP_408_REQUEST_TIMEOUT:
                    self._set_in_cache(caching_allowed, full_path, response, timeout=CACHE_TIMEOUT)

            else:
                response = query((self, request._request, endpoint_levels, full_path, drf_request, caching_allowed))
        except DeletedEntryError as e:
            if settings.DEBUG:
                raise
            content = {'detail': e.args[2], 'accession': e.args[0], 'date': e.args[1]}
            response = Response(content, status=status.HTTP_410_GONE)
        except EmptyQuerysetError as e:
            if settings.DEBUG:
                raise
            content = {'detail': e.args[0]}
            response = Response(content, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            if settings.DEBUG:
                raise
            content = {'Error': e.args[0]}
            response = Response(content, status=status.HTTP_404_NOT_FOUND)
        return response

    def _set_in_cache(self, caching_allowed, full_path, response, timeout=None):
        if caching_allowed:
            try:
                self.cache.set(full_path, response, timeout)
            except Exception as e:
                if "TRAVIS" not in os.environ:
                    logger.error('Failed setting {} into cache: {}'.format(full_path, e))

    def register_filter_serializer(self, filter_serializer, value):
        if value in [e[0] for e in self.available_endpoint_handlers]:
            self.current_filter_endpoint = value
        if self.current_filter_endpoint is not None:
            self.filter_serializers[self.current_filter_endpoint] = {
                "filter_serializer": filter_serializer,
                "value": value
            }

    def search_modifier(self, search, general_handler):
        if search.strip() == "":
            return
        if general_handler.queryset_manager.main_endpoint == "taxonomy":
            self.queryset_manager.add_filter(
                "search",
                accession__icontains=search,
                full_name__icontains=search
            )
        else:
            self.queryset_manager.add_filter(
                "search",
                accession__icontains=search,
                name__icontains=search
            )

    @staticmethod
    def get_search_controller(queryset_manager=None):
        return ElasticsearchController(queryset_manager)
