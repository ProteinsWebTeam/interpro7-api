import re
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from webfront.models import interpro
from webfront.pagination import CustomPagination


class CustomView(GenericAPIView):
    # description of the level of the endpoint, for debug purposes
    level_description = 'level'
    # dict of handlers for lower levels of the endpoint
    # the key will be regex or string to which the endpoint will be matched
    child_handlers = {}
    # dictionary with the high level endpoints that havent been used yet in the URL
    available_endpoint_handlers = {}
    # queryset upon which build new querysets
    queryset = interpro.Entry.objects
    # will be used for the 'using()' part of the queries
    django_db = 'interpro_ro'
    # custom pagination class
    pagination_class = CustomPagination
    # not used now
    many = True
    from_model = True

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, *args, **kwargs):
        # if this is the last level
        if (len(endpoint_levels) == level):
            if self.from_model:
                self.queryset = self.queryset.using(self.django_db)
                if self.many:
                    self.queryset = self.paginate_queryset(self.queryset)
                else:
                    self.queryset = self.queryset.first()

            serialized = self.serializer_class(
                # passed to DRF's view
                self.queryset,
                many=self.many,
                # extracted out in the custom view
                content=request.GET.getlist('content'),
                context={"request":request}
            )

            return Response(serialized.data)

        else:
            # combine the children handlers with the available endpoints
            endpoints = available_endpoint_handlers.copy()
            handlers = {**self.child_handlers, **endpoints}

            # get next level name provided by the client
            level_name = endpoint_levels[level]
            try:
                # get the corresponding handler name
                handler_name = next(
                    h for h in handlers
                    if re.match(r'(?i)^{}$'.format(h), level_name)
                )
            except StopIteration:
                # no handler has been found
                raise ValueError('the level \'{}\' is not a valid {}'.format(
                    level_name, self.level_description
                ))

            #if the handler name is one of the endpoints thisone should be removed of the available ones
            if handler_name in endpoints:
                endpoints.pop(handler_name)
                #removing the current
                endpoint_levels = endpoint_levels[level:]
                level=0

            # delegate to the lower level handler
            return handlers[handler_name].as_view()(
                request, endpoint_levels, endpoints, level+1,
                *args, **kwargs
            )
