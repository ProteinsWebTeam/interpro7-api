import re
from django.conf import settings
from rest_framework.generics import GenericAPIView
from django.http import HttpResponse
import logging

from django.db.models import Q
from functools import reduce
from operator import or_

from webfront.exceptions import EmptyQuerysetError, BadURLParameterError
from webfront.response import Response
from webfront.constants import SerializerDetail
from webfront.models import Entry
from webfront.pagination import CustomPagination

logger = logging.getLogger("interpro.request")


def is_single_endpoint(general_handler):
    return general_handler.queryset_manager.is_single_endpoint()
    # main_ep = general_handler.queryset_manager.main_endpoint
    # filters = [
    #     f for f in general_handler.queryset_manager.filters
    #     if f != main_ep and f != "search" and general_handler.queryset_manager.filters[f] != {}
    # ]
    # return len(filters) == 0


class CustomView(GenericAPIView):
    # Parent class of all the view handlers on the API, including the GeneralHandler.

    # description of the level of the endpoint, for debug purposes
    level_description = "level"
    # List of tuples for the handlers for lower levels of the endpoint
    # the firt item of each tuple will be regex or string to which the endpoint will be matched
    # and the second item is the view handler that should proccess it.
    child_handlers = []
    # Default queryset of this view
    queryset = Entry.objects
    # custom pagination class
    pagination_class = CustomPagination
    # Each View will be serialized different if it contains many or a single item (List, Object)
    many = True
    # Some views Might not want to be serialized beyond its object  structure (i.e. from_model=False)
    from_model = True
    # A serializer can have different levels of details. e.g. we can use the same seializer for the list of proteins
    # and protein details showing only the accession in the first case
    serializer_detail = SerializerDetail.ALL
    serializer_detail_filter = SerializerDetail.ALL
    after_key = None
    before_key = None

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        drf_request=None,
        *args,
        **kwargs
    ):
        # if this is the last level
        if len(endpoint_levels) == level:
            searcher = general_handler.searcher
            has_payload = general_handler.modifiers.execute(drf_request)
            logger.debug(request.get_full_path())
            if has_payload or general_handler.modifiers.serializer is not None:
                self.serializer_detail = general_handler.modifiers.serializer
            if has_payload:
                self.queryset = general_handler.modifiers.payload
                if self.serializer_detail == SerializerDetail.ANNOTATION_BLOB:
                    # assuming queryset contains a list of one annotation object
                    if len(self.queryset) == 1:
                        annotation = self.queryset[0]
                        mime_type = annotation.mime_type
                        value = annotation.value
                        return HttpResponse(value, content_type=mime_type)
                general_handler.filter_serializers = []
                self.many = general_handler.modifiers.many
                self.search_size = general_handler.modifiers.search_size
                if self.many:
                    self.queryset = self.paginator.paginate_queryset(
                        self.get_queryset(),
                        drf_request,
                        view=self,
                        search_size=self.search_size,
                        # after_key=self.after_key,
                    )

            elif self.from_model:
                if (
                    is_single_endpoint(general_handler)
                    or not self.expected_response_is_list()
                ):
                    self.queryset = general_handler.queryset_manager.get_queryset(
                        only_main_endpoint=True
                    )
                    self.search_size = self.queryset.count()
                else:
                    self.update_queryset_from_search(searcher, general_handler)

                if self.queryset.count() == 0:
                    # if 0 == general_handler.queryset_manager.get_queryset(only_main_endpoint=True).count():
                    #     raise Exception("The URL requested didn't have any data related.\nList of endpoints: {}"
                    #                     .format(endpoint_levels))

                    raise EmptyQuerysetError(
                        "The URL requested didn't have any data related.\nList of endpoints: {}".format(
                            endpoint_levels
                        )
                    )
                if self.many:
                    self.queryset = self.paginator.paginate_queryset(
                        self.get_queryset(),
                        drf_request,
                        view=self,
                        search_size=self.search_size,
                        after_key=self.after_key,
                        before_key=self.before_key,
                    )
                else:
                    self.queryset = self.get_queryset().first()
            else:
                if endpoint_levels[0] != "utils":
                    # if it gets here it is a endpoint request checking for database contributions.
                    self.queryset = self.get_counter_response(general_handler, searcher)

            serialized = self.serializer_class(
                # passed to DRF's view
                self.queryset,
                many=self.many,
                # extracted out in the custom view
                content=request.GET.getlist("content"),
                context={"request": drf_request},
                searcher=searcher,
                serializer_detail=self.serializer_detail,
                serializer_detail_filters=general_handler.filter_serializers,
                queryset_manager=general_handler.queryset_manager,
            )

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
                    h
                    for h in handlers
                    if re.match(
                        r"(?i)^{}$".format(h[0]), level_name, flags=re.IGNORECASE
                    )
                )
            except StopIteration:
                # no handler has been found
                raise ValueError(
                    "the level '{}' is not a valid {}".format(
                        level_name, self.level_description
                    )
                )

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
                    # Which implies that another endpoint is to be procces and therefore is filtering time.
                    self.filter_entrypoint(
                        handler_name,
                        handler_class,
                        endpoint_levels,
                        endpoints,
                        general_handler,
                    )
                    return super(handler, self).get(
                        request,
                        endpoint_levels,
                        endpoints,
                        len(endpoint_levels),
                        parent_queryset,
                        handler,
                        general_handler,
                        drf_request,
                        *args,
                        **kwargs
                    )

            # delegate to the lower level handler
            return handler_class.as_view()(
                request,
                endpoint_levels,
                endpoints,
                level + 1,
                self.queryset,
                handler_class,
                general_handler,
                drf_request,
                *args,
                **kwargs
            )

    def filter_entrypoint(
        self, handler_name, handler_class, endpoint_levels, endpoints, general_handler
    ):
        for level in range(len(endpoint_levels)):
            self.queryset = handler_class.filter(
                self.queryset, endpoint_levels[level], general_handler
            )
            general_handler.register_filter_serializer(
                handler_class.serializer_detail_filter, endpoint_levels[level]
            )
            # general_handler.register_post_serializer(handler_class.post_serializer, endpoint_levels[level])
            handlers = endpoints + handler_class.child_handlers

            try:
                level_name = endpoint_levels[level + 1]
            except IndexError:
                return

            try:
                # get the corresponding handler name
                handler_name, handler_class = next(
                    h
                    for h in handlers
                    if re.match(
                        r"(?i)^{}$".format(h[0]), level_name, flags=re.IGNORECASE
                    )
                )
            except StopIteration:
                # no handler has been found
                raise ValueError(
                    "the level '{}' is not a valid {}".format(
                        level_name, self.level_description
                    )
                )
            try:
                index = [e[0] for e in endpoints].index(handler_name)
                endpoints.pop(index)
            except ValueError:
                pass

    def get_counter_response(self, general_handler, searcher):
        extra = [
            k
            for k, v in general_handler.filter_serializers.items()
            if v["filter_serializer"]
            in [
                SerializerDetail.PROTEIN_DB,
                SerializerDetail.ENTRY_DB,
                SerializerDetail.TAXONOMY_DB,
                SerializerDetail.PROTEOME_DB,
                SerializerDetail.SET_DB,
                SerializerDetail.STRUCTURE_DB,
            ]
        ]
        return searcher.get_counter_object(
            general_handler.queryset_manager.main_endpoint, extra_counters=extra
        )

    def get_database_contributions(self, queryset):
        return

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        return queryset

    def expected_response_is_list(self):
        return self.many

    search_size = None

    def update_queryset_from_search(self, searcher, general_handler):
        ep = general_handler.queryset_manager.main_endpoint
        s = general_handler.pagination["size"]
        after = general_handler.pagination["after"]
        before = general_handler.pagination["before"]
        if after is not None and before is not None:
            raise BadURLParameterError(
                "You can't use 'after' and 'before' together. Use only one of them."
            )
        qs = general_handler.queryset_manager.get_searcher_query(include_search=True)
        res, length, after_key, before_key = searcher.get_list_of_endpoint(
            ep, rows=s, query=qs, after=after, before=before
        )
        self.queryset = general_handler.queryset_manager.get_base_queryset(ep)

        self.queryset = filter_queryset_accession_in(self.queryset, res)

        self.search_size = length
        self.after_key = after_key
        self.before_key = before_key


def filter_queryset_accession_in(queryset, list):
    if len(list) > 0:
        or_filter = reduce(or_, (Q(**{"accession__iexact": acc}) for acc in list))
        return queryset.filter(or_filter)
    else:
        return queryset.filter(accession__in=[])
