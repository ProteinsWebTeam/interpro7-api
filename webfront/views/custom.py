import re
from django.views.generic import View
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage

from webfront.models import interpro


class CustomView(GenericAPIView):
    level = 0
    level_description = 'level'
    child_handlers = {}
    queryset = interpro.Entry.objects
    django_db = 'interpro_ro'
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
                self.queryset,
                many=self.many,
                content=request.GET.getlist('content')
            )

            return Response(serialized.data)
            # if json_response:
            #     return self.get_json(endpoint_levels, request, *args, **kwargs)
            # else:
            #     return self.get_html(endpoint_levels, request, *args, **kwargs)
        # if this is not the last level
        else:
            # get next level name
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
