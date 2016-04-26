from enum import Enum

import re
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from webfront.models import Entry
from webfront.pagination import CustomPagination


class SerializerDetail(Enum):
    ALL = 1
    HEADERS = 2

    ENTRY_OVERVIEW = 101
    ENTRY_DETAIL = 102
    ENTRY_PROTEIN = 103
    ENTRY_PROTEIN_DETAIL = 104

    PROTEIN_OVERVIEW = 201
    PROTEIN_DETAIL = 202
    PROTEIN_ENTRY_DETAIL = 203

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
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        # if this is the last level
        if len(endpoint_levels) == level:
            if self.from_model:
                # self.queryset = self.queryset.using(self.django_db)
                if self.many:
                    self.queryset = self.paginate_queryset(self.get_queryset())
                else:
                    self.queryset = self.get_queryset().first()

                serialized = self.serializer_class(
                    # passed to DRF's view
                    self.queryset,
                    many=self.many,
                    # extracted out in the custom view
                    content=request.GET.getlist('content'),
                    context={"request": request},
                    serializer_detail=self.serializer_detail,
                )
                data_tmp= self.post_serializer(serialized.data, endpoint_levels[level-1])

                if self.many:
                    return self.get_paginated_response(data_tmp)
                else:
                    return Response(data_tmp)

            return Response(self.queryset)

        else:
            # combine the children handlers with the available endpoints
            endpoints = available_endpoint_handlers.copy()
            # handlers = {**self.child_handlers, **endpoints}
            handlers = endpoints + self.child_handlers

            # get next level name provided by the client
            level_name = endpoint_levels[level]
            try:
                # get the corresponding handler name
                handler_name, handler_class = next(
                    h for h in handlers
                    if re.match(r'(?i)^{}$'.format(h[0]), level_name)
                )
            except StopIteration:
                # no handler has been found
                raise ValueError('the level \'{}\' is not a valid {}'.format(
                    level_name, self.level_description
                ))

            # if the handler name is one of the endpoints this one should be removed of the available ones
            try:
                index = [e[0] for e in endpoints].index(handler_name)
                endpoints.pop(index)
                # removing the current
                endpoint_levels = endpoint_levels[level:]
                level = 0
                if handler is not None:
                    self.filter_entrypoint(handler_name, handler_class,endpoint_levels, endpoints)
                    return super(handler, self).get(
                        request, endpoint_levels, endpoints, len(endpoint_levels),
                        parent_queryset, handler,
                        *args, **kwargs
            )
            except ValueError:
                pass

            handler= handler_class

            # delegate to the lower level handler
            return handler_class.as_view()(
                request, endpoint_levels, endpoints, level+1,
                parent_queryset, handler,
                *args, **kwargs
            )

    def filter_entrypoint(self, handler_name, handler_class, endpoint_levels, endpoints):
        for level in range(len(endpoint_levels)):
            self.serializer_detail = handler_class.serializer_detail_filter
            self.queryset = handler_class.filter(self.queryset,endpoint_levels[level])
            self.post_serializer = handler_class.post_serializer

            # handlers = {**self.child_handlers, **endpoints}
            handlers = endpoints + handler_class.child_handlers

            try:
                level_name = endpoint_levels[level+1]
            except IndexError:
                return

            try:
                # get the corresponding handler name
                handler_name, handler_class = next(
                    h for h in handlers
                    if re.match(r'(?i)^{}$'.format(h[0]), level_name)
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

    @staticmethod
    def filter(queryset, level_name=""):
        return queryset

    @staticmethod
    def post_serializer(obj, level_name=""):
        return obj
