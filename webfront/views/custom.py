import re

from rest_framework.generics import GenericAPIView
from django.http import HttpResponse, HttpResponseRedirect
import logging

from django.db.models import Q
from functools import reduce
from operator import or_

from webfront.exceptions import EmptyQuerysetError
from webfront.response import Response
from webfront.constants import SerializerDetail
from webfront.models import (
    Entry,
    TaxonomyPerEntry,
    TaxonomyPerEntryDB,
    ProteomePerEntry,
    ProteomePerEntryDB,
)
from webfront.pagination import CustomPagination
from webfront.views.queryset_manager import (
    can_use_taxonomy_per_entry,
    can_use_taxonomy_per_db,
    can_use_proteome_per_entry,
    can_use_proteome_per_db,
)

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
    # the first item of each tuple will be regex or string to which the endpoint will be matched
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
    elastic_result = None
    http_method_names = ["get", "head"]

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
            # Executes all the modifiers, some add filters to the query set but others might replace it.
            has_payload = general_handler.modifiers.execute(drf_request)
            logger.debug(request.get_full_path())
            # If there is a payload from the modifiers, it has its own serializer
            if has_payload or general_handler.modifiers.serializer is not None:
                self.serializer_detail = general_handler.modifiers.serializer
            if general_handler.modifiers.many is not None:
                self.many = general_handler.modifiers.many
            # When there is a payload from the modifiers. It should build the response with it
            if has_payload:
                if general_handler.modifiers.payload is None:
                    raise EmptyQuerysetError(
                        "There is no data associated with the requested URL+modifier.\nList of endpoints: {}".format(
                            endpoint_levels
                        )
                    )

                self.queryset = general_handler.modifiers.payload
                if self.serializer_detail == SerializerDetail.ANNOTATION_BLOB:
                    # assuming queryset contains a list of one annotation object
                    if len(self.queryset) == 1:
                        annotation = self.queryset[0]
                        mime_type = annotation.mime_type
                        anno_type = annotation.type
                        anno_value = annotation.value
                        response = HttpResponse(
                            content=anno_value, content_type=mime_type
                        )

                        if anno_type.startswith("alignment:"):
                            if "download" in request.GET:
                                response["Content-Type"] = "application/gzip"
                            else:
                                response["Content-Encoding"] = "gzip"
                                if "gzip" in mime_type:
                                    response["Content-Type"] = "text/plain"

                        return response

                general_handler.filter_serializers = []
                self.search_size = general_handler.modifiers.search_size
                if self.many:
                    self.queryset = self.paginator.paginate_queryset(
                        self.get_queryset(),
                        drf_request,
                        view=self,
                        search_size=self.search_size,
                        after_key=general_handler.modifiers.after_key,
                        before_key=general_handler.modifiers.before_key,
                    )

            elif self.from_model:
                # Single endpoints don't require Elasticsearch, so they can be resolved
                # by normal Django means(i.e. just the MySQL model)
                if (
                    is_single_endpoint(general_handler)
                    or not self.expected_response_is_list()
                ):
                    self.queryset = general_handler.queryset_manager.get_queryset(
                        only_main_endpoint=True
                    )
                    self.search_size = self.queryset.count()
                else:
                    # The  queryset needs to be updated to query other sources
                    self.update_queryset(searcher, general_handler)

                if self.queryset.count() == 0:
                    raise EmptyQuerysetError(
                        "There is no data associated with the requested URL.\nList of endpoints: {}".format(
                            endpoint_levels
                        )
                    )
                if self.many:
                    self.queryset = self.paginator.paginate_queryset(
                        self.get_queryset(),
                        drf_request,
                        view=self,
                        # passing data of the elastic result to the pagination instance
                        search_size=self.search_size,
                        after_key=self.after_key,
                        before_key=self.before_key,
                        elastic_result=self.elastic_result,
                        ordering=general_handler.queryset_manager.order_field,
                    )
                else:
                    self.queryset = self.get_queryset().first()
            else:
                if endpoint_levels[0] != "utils":
                    # if it gets here it is an endpoint request checking for database contributions.
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

            payload = {"data": serialized.data}
            extensions = general_handler.modifiers.execute_extenders(
                drf_request, serialized.data
            )
            if extensions != {}:
                payload["extensions"] = extensions

            if self.many:
                return self.get_paginated_response(payload)
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
                    filter = self.filter_entrypoint(
                        handler_name,
                        handler_class,
                        endpoint_levels,
                        endpoints,
                        general_handler,
                    )
                    if isinstance(filter, HttpResponseRedirect):
                        return filter

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
            if isinstance(self.queryset, HttpResponseRedirect):
                return self.queryset
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

    def update_queryset(self, searcher, general_handler):
        if (
            # it uses the taxonomy endpoint filtered by an entry accession
            general_handler.queryset_manager.main_endpoint == "taxonomy"
            and can_use_taxonomy_per_entry(general_handler.queryset_manager.filters)
        ):
            self.update_queryset_from_taxonomy_per_entry(general_handler)
        elif (
            # it uses the taxonomy endpoint filtered by an entry database
            general_handler.queryset_manager.main_endpoint == "taxonomy"
            and can_use_taxonomy_per_db(general_handler.queryset_manager.filters)
        ):
            self.update_queryset_from_taxonomy_per_entry_db(general_handler)
        elif (
            # it uses the proteome endpoint filtered by an entry accession
            general_handler.queryset_manager.main_endpoint == "proteome"
            and can_use_proteome_per_entry(general_handler.queryset_manager.filters)
        ):
            self.update_queryset_from_proteome_per_entry(general_handler)
        elif (
            # it uses the proteome endpoint filtered by an entry database
            general_handler.queryset_manager.main_endpoint == "proteome"
            and can_use_proteome_per_db(general_handler.queryset_manager.filters)
        ):
            self.update_queryset_from_proteome_per_entry_db(general_handler)
        else:
            # It uses multiple endpoints, so we need to use the elastic index
            self.update_queryset_from_search(searcher, general_handler)

    # Queries the elastic searcher core to get a list of accessions of the main endpoint,
    # then builds a queryset matching those accessions.
    # This is the main connection point between elastic and MySQL
    def update_queryset_from_search(self, searcher, general_handler):
        ep = general_handler.queryset_manager.main_endpoint
        s = general_handler.pagination["size"]
        cursor = general_handler.pagination["cursor"]

        qs = general_handler.queryset_manager.get_searcher_query(include_search=True)
        elastic_result, length, after_key, before_key, should_keep_elastic_order = (
            searcher.get_list_of_endpoint(ep, rows=s, query=qs, cursor=cursor)
        )

        self.queryset = general_handler.queryset_manager.get_base_queryset(ep)
        self.queryset = filter_queryset_accession_in(self.queryset, elastic_result)

        # This values get store in the instance attributes, so they can be recovered on the pagination stage.
        self.search_size = length
        self.after_key = after_key
        self.before_key = before_key
        self.elastic_result = elastic_result if should_keep_elastic_order else None

    def update_queryset_from_taxonomy_per_entry(self, general_handler):
        entry_acc = general_handler.queryset_manager.filters["entry"]["accession"]
        self.queryset = TaxonomyPerEntry.objects.filter(
            entry_acc=entry_acc.upper()
        ).order_by("num_proteins")
        self.search_size = len(self.queryset)

    def update_queryset_from_taxonomy_per_entry_db(self, general_handler):
        entry_db = general_handler.queryset_manager.filters["entry"]["source_database"]
        self.queryset = TaxonomyPerEntryDB.objects.filter(
            source_database=entry_db
        ).order_by("num_proteins")
        self.search_size = len(self.queryset)

    def update_queryset_from_proteome_per_entry(self, general_handler):
        entry_acc = general_handler.queryset_manager.filters["entry"]["accession"]
        self.queryset = ProteomePerEntry.objects.filter(
            entry_acc=entry_acc.upper()
        ).order_by("num_proteins")
        self.search_size = len(self.queryset)

    def update_queryset_from_proteome_per_entry_db(self, general_handler):
        entry_db = general_handler.queryset_manager.filters["entry"]["source_database"]
        self.queryset = ProteomePerEntryDB.objects.filter(
            source_database=entry_db
        ).order_by("num_proteins")
        if "is_reference" in general_handler.queryset_manager.filters["proteome"]:
            self.queryset.filter(
                proteome__is_reference=general_handler.queryset_manager.filters[
                    "proteome"
                ]["is_reference"]
            )

        self.search_size = len(self.queryset)


def filter_queryset_accession_in(queryset, list_of_accessions):
    if len(list_of_accessions) > 0:
        or_filter = reduce(
            or_, (Q(**{"accession__iexact": acc}) for acc in list_of_accessions)
        )
        return queryset.filter(or_filter)
    else:
        return queryset.filter(accession__in=[])
