from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.urls import replace_query_param

from django.core.paginator import Paginator as DjangoPaginator

class CustomPaginator(DjangoPaginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        if not object_list.ordered:
            object_list = object_list.order_by('accession')
        super(CustomPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)
        if hasattr(object_list, "_count"):
            self._count = object_list._count

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 200
    ordering = '-accession'
    django_paginator_class = CustomPaginator

    # def get_paginated_response(self, data):
    #     return Response(OrderedDict([
    #         ('count', self.page.paginator.count if self.search_size == 0 else self.search_size),
    #         ('next', self.get_next_link()),
    #         ('previous', self.get_previous_link()),
    #         ('results', data)
    #     ]))

    def paginate_queryset(self, queryset, request, **kwargs):
        if "search_size" in kwargs and kwargs["search_size"] is not None:
            queryset._count = kwargs["search_size"]
        return super(CustomPagination, self).paginate_queryset(queryset, request, kwargs["view"])
    #
    # def get_next_link(self):
    #     if self.search_size == 0:
    #         return super(CustomPagination, self).get_next_link()
    #     url = self.request.build_absolute_uri()
    #     page_number = self.page.next_page_number()
    #     return replace_query_param(url, self.page_query_param, page_number)

