from enum import Enum

import re
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from webfront.models import Entry
from webfront.pagination import CustomPagination


class SerializerDetail(Enum):
    ALL = 1
    HEADERS = 2


class CustomView(GenericAPIView):
    # description of the level of the endpoint, for debug purposes
    level_description = 'level'
    # dict of handlers for lower levels of the endpoint
    # the key will be regex or string to which the endpoint will be matched
    child_handlers = {}
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

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, *args, **kwargs):
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
                    serializer_detail=self.serializer_detail
                )
                return Response(serialized.data)
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
                handler_name, handler = next(
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
            except: pass

            # delegate to the lower level handler
            return handler.as_view()(
                request, endpoint_levels, endpoints, level+1,
                parent_queryset,
                *args, **kwargs
            )
