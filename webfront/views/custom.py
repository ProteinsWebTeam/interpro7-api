import re
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from webfront.models import interpro
from webfront.pagination import CustomPagination


class CustomView(GenericAPIView):
    # level of the view, to be able to extract the value from the URL
    level = 0
    # description of the level of the endpoint, for debug purposes
    level_description = 'level'
    # dict of handlers for lower levels of the endpoint
    # the key will be regex or string to which the endpoint will be matched
    child_handlers = {}
    # queryset upon which build new querysets
    queryset = interpro.Entry.objects
    # will be used for the 'using()' part of the queries
    django_db = 'interpro_ro'
    # custom pagination class
    pagination_class = CustomPagination
    # not used now
    many = True

    # # TODO: check if we can avoid instantiating at every request
    # def __init__(self, *args, **kwargs):
    #     print('instantiating {}'.format(self))

    # def query_to_page(self, query, pagination = {}, *args, **kwargs):
    #     paginator = Paginator(query, pagination['size'])
    #     paginator = self.pagination_class
    #     try:
    #         subset = paginator.page(pagination['index'])
    #     except EmptyPage:
    #         subset = paginator.page(paginator.num_pages)
    #     return subset.object_list.values()
    #
    # def get_more(self, queryset, *details):
    #     return queryset.prefetch_related(*details)
    #
    # def get_json(self, endpoint_levels, request, *args, **kwargs):
    #     response = {'endpoint_levels': endpoint_levels}
    #     if (self.multiple):
    #         response = {
    #             **response,
    #             'query': list(map(lambda a: a, self.query_to_page(
    #                 self.queryset.using(self.django_db), *args, **kwargs
    #             ))),
    #         }
    #     else:
    #         response = {
    #             **response,
    #             # 'query': self.queryset.using(self.django_db).first(),
    #             'query': self.queryset.using(self.django_db).values()[0],
    #         }
    #     return Response(response)
    #
    # def get_html(self, endpoint_levels, request, *args, **kwargs):
    #     return Response(self.queryset.using(self.django_db).values())
    #     return HttpResponse(
    #         'http response: {}'.format('→'.join(['Home', *endpoint_levels]))
    #     )

    def get(
        self, request, endpoint_levels, *args, **kwargs
    ):
        # if this is the last level
        if (len(endpoint_levels) == self.level):
            self.queryset = self.queryset.using(self.django_db)
            if not self.many:
                self.queryset = self.queryset.first()
            serialized = self.serializer_class(
                # passed to DRF's view
                self.paginate_queryset(self.queryset),
                many=self.many,
                # extracted out in the custom view
                content=request.GET.getlist('content')
            )

            return Response(serialized.data)

        else:
            # get next level name provided by the client
            level_name = endpoint_levels[self.level]
            try:
                # get the corresponding handler name
                handler_name = next(
                    h for h in self.child_handlers
                    if re.match(r'(?i)^{}$'.format(h), level_name)
                )
            except StopIteration:
                # no handler has been found
                raise ValueError('the level \'{}\' is not a valid {}'.format(
                    level_name, self.level_description
                ))
            # delegate to the lower level handler
            return self.child_handlers[handler_name].as_view()(
                request, endpoint_levels, *args, **kwargs
            )
