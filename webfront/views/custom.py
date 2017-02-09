import re
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from webfront.constants import SerializerDetail
from webfront.models import Entry
from webfront.pagination import CustomPagination
from webfront.solr_controller import SolrController
from webfront.search_controller import ElasticsearchController
from django.conf import settings


class CustomView(GenericAPIView):
    # description of the level of the endpoint, for debug purposes
    level_description = 'level'
    # dict of handlers for lower levels of the endpoint
    # the key will be regex or string to which the endpoint will be matched
    child_handlers = []
    # dictionary with the high level endpoints that havent been used yet in the URL
    available_endpoint_handlers = {}
    # queryset upon which build new querysets
    queryset = Entry.objects
    # will be used for the 'using()' part of the queries
    # django_db = 'interpro_ro'
    # custom pagination class
    pagination_class = CustomPagination
    # not used now
    many = True
    from_model = True
    # A serializer can have different levels of details. e.g. we can use the same seializer for the list of proteins
    # and protein details showing only the accession in the first case
    serializer_detail = SerializerDetail.ALL
    serializer_detail_filter = SerializerDetail.ALL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        # if this is the last level
        if len(endpoint_levels) == level:
            searcher = self.get_search_controller(general_handler.queryset_manager)
            if self.from_model:
                # search filter, from request parameters
                search = request.query_params.get("search")
                if search:
                    general_handler.queryset_manager.add_filter(
                        "search",
                        accession__icontains=search,
                        name__icontains=search
                    )
                if self.is_single_endpoint(general_handler) or not self.expected_response_is_list():
                    self.queryset = general_handler.queryset_manager.get_queryset(only_main_endpoint=True)
                else:
                    self.update_queryset_from_search(searcher, general_handler)

                if self.queryset.count() == 0:
                    if 0 == general_handler.queryset_manager.get_queryset(only_main_endpoint=True).count():
                        raise Exception("The URL requested didn't have any data related.\nList of endpoints: {}"
                                        .format(endpoint_levels))

                    raise ReferenceError("The URL requested didn't have any data related.\nList of endpoints: {}"
                                         .format(endpoint_levels))
                if self.many:
                    self.queryset = self.paginate_queryset(self.get_queryset())
                else:
                    self.queryset = self.get_queryset().first()
            else:
                # if it gets here it is a endpoint request checking for database contributions.
                self.queryset = self.get_counter_response(general_handler, searcher)

            serialized = self.serializer_class(
                # passed to DRF's view
                self.queryset,
                many=self.many,
                # extracted out in the custom view
                content=request.GET.getlist('content'),
                context={"request": request},
                serializer_detail=self.serializer_detail,
                serializer_detail_filters=general_handler.filter_serializers,
                queryset_manager=general_handler.queryset_manager,
            )
            # data_tmp = general_handler.execute_post_serializers(serialized.data)

            if self.many:
                return self.get_paginated_response(serialized.data)
            else:
                return Response(serialized.data)

        else:
            # combine the children handlers with the available endpoints
            endpoints = available_endpoint_handlers.copy()
            handlers = endpoints + self.child_handlers

            # get next level name provided by the client
            level_name = endpoint_levels[level]
            try:
                # get the corresponding handler name
                handler_name, handler_class = next(
                    h for h in handlers
                    if re.match(r'(?i)^{}$'.format(h[0]), level_name, flags=re.IGNORECASE)
                )
            except StopIteration:
                # no handler has been found
                raise ValueError('the level \'{}\' is not a valid {}'.format(
                    level_name, self.level_description
                ))

            # if the handler name is one of the endpoints this one should be removed of the available ones
            index = -1
            try:
                index = [e[0] for e in endpoints].index(handler_name)
            except ValueError:
                pass

            if index != -1:
                endpoints.pop(index)
                # removing the current
                endpoint_levels = endpoint_levels[level:]
                level = 0
                if handler is not None:
                    self.filter_entrypoint(handler_name, handler_class, endpoint_levels, endpoints, general_handler)
                    return super(handler, self).get(
                        request, endpoint_levels, endpoints, len(endpoint_levels),
                        parent_queryset, handler, general_handler,
                        *args, **kwargs
                    )

            general_handler.register_post_serializer(handler_class.post_serializer, level_name)

            # delegate to the lower level handler
            return handler_class.as_view()(
                request, endpoint_levels, endpoints, level + 1,
                self.queryset, handler_class, general_handler,
                *args, **kwargs
            )

    def filter_entrypoint(self, handler_name, handler_class, endpoint_levels, endpoints, general_handler):
        for level in range(len(endpoint_levels)):
            self.queryset = handler_class.filter(self.queryset, endpoint_levels[level], general_handler)
            general_handler.register_filter_serializer(handler_class.serializer_detail_filter, endpoint_levels[level])
            general_handler.register_post_serializer(handler_class.post_serializer, endpoint_levels[level])
            handlers = endpoints + handler_class.child_handlers

            try:
                level_name = endpoint_levels[level + 1]
            except IndexError:
                return

            try:
                # get the corresponding handler name
                handler_name, handler_class = next(
                    h for h in handlers
                    if re.match(r'(?i)^{}$'.format(h[0]), level_name, flags=re.IGNORECASE)
                )
            except StopIteration:
                # no handler has been found
                raise ValueError('the level \'{}\' is not a valid {}'.format(
                    level_name, self.level_description
                ))
            try:
                index = [e[0] for e in endpoints].index(handler_name)
                endpoints.pop(index)
            except ValueError:
                pass

    def get_counter_response(self, general_handler, solr):
        if self.is_single_endpoint(general_handler):
            self.queryset = general_handler.queryset_manager.get_queryset().distinct()
            obj = self.get_database_contributions(self.queryset)
            data_tmp = general_handler.execute_post_serializers(obj)
            return data_tmp
        else:
            extra = [k
                     for k, v in general_handler.filter_serializers.items()
                     if v["filter_serializer"] in [SerializerDetail.PROTEIN_DB,
                                                   SerializerDetail.ENTRY_DB,
                                                   SerializerDetail.STRUCTURE_DB]
                     ]
            return solr.get_counter_object(general_handler.queryset_manager.main_endpoint, extra_counters=extra)

    def get_database_contributions(self, prefix=""):
        return

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        return obj

    def expected_response_is_list(self):
        return self.many

    def is_single_endpoint(self, general_handler):
        return general_handler.filter_serializers == {}

    def update_queryset_from_search(self, searcher, general_handler):
        ep = general_handler.queryset_manager.main_endpoint
        res = searcher.get_list_of_endpoint(ep)
        self.queryset = general_handler.queryset_manager\
            .get_base_queryset(ep)\
            .filter(accession__in=res)

    @staticmethod
    def get_search_controller(queryset_manager=None):
        if "solr" in settings.HAYSTACK_CONNECTIONS['default']['URL']:
            return SolrController(queryset_manager)
        else:
            return ElasticsearchController(queryset_manager)
