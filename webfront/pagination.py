from collections import OrderedDict
from django.core.paginator import Paginator as DjangoPaginator

from webfront.response import Response
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.utils.urls import replace_query_param, remove_query_param
from django.conf import settings

from django.http import QueryDict


def replace_url_host(url):
    host = settings.INTERPRO_CONFIG.get("api_url", "http://localhost:8007/api/")
    return host + url.split("/api/")[1]


class CustomPaginator(DjangoPaginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        if not object_list.ordered:
            object_list = object_list.order_by("accession")
        super(CustomPaginator, self).__init__(
            object_list, per_page, orphans, allow_empty_first_page
        )


class CustomPagination(CursorPagination):
    page_size = settings.INTERPRO_CONFIG.get("default_page_size", 20)
    page_size_query_param = "page_size"
    ordering = "accession"
    current_size = None
    after_key = None
    before_key = None

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.current_size),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def paginate_queryset(self, queryset, request, **kwargs):
        self.current_size = None
        self.after_key = None
        if (
            hasattr(queryset, "model")
            and queryset.model._meta.ordering != []
            and queryset.model._meta.ordering != ""
            and queryset.model._meta.ordering is not None
        ):
            self.ordering = queryset.model._meta.ordering
        if "search_size" in kwargs and kwargs["search_size"] is not None:
            if not queryset.ordered:
                queryset = queryset.order_by("accession")
            self.current_size = kwargs["search_size"]
        if "after_key" in kwargs and kwargs["after_key"] is not None:
            self.after_key = kwargs["after_key"]
        if "before_key" in kwargs and kwargs["before_key"] is not None:
            self.before_key = kwargs["before_key"]
        return super(CustomPagination, self).paginate_queryset(
            queryset, request, kwargs["view"]
        )

    def decode_cursor(self, request):
        if self.after_key is not None or self.before_key is not None:
            return None
        return super(CustomPagination, self).decode_cursor(request)

    def has_next_page(self):
        if self.after_key is None:
            return self.has_next
        return True

    def has_prev_page(self):
        if self.before_key is None:
            return self.has_previous
        return True

    def get_next_link(self):
        if not self.has_next_page():
            return None
        if self.after_key is None:
            return super(CustomPagination, self).get_next_link()
        url = replace_url_host(self.base_url)
        return replace_query_param(url, "cursor", self.after_key)

    def get_previous_link(self):
        if not self.has_prev_page():
            return None
        if self.before_key is None:
            return super(CustomPagination, self).get_previous_link()
        url = replace_url_host(self.base_url)
        return replace_query_param(url, "cursor", "-" + self.before_key)


class CustomPaginationOld(PageNumberPagination):
    page_size = settings.INTERPRO_CONFIG.get("default_page_size", 20)
    page_size_query_param = "page_size"
    max_page_size = 200
    ordering = "-accession"
    django_paginator_class = CustomPaginator
    current_size = None

    def get_paginated_response(self, data):
        self.current_size = (
            self.page.paginator.count
            if self.current_size is None
            else self.current_size
        )
        return Response(
            OrderedDict(
                [
                    ("count", self.current_size),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def paginate_queryset(self, queryset, request, **kwargs):
        self.current_size = None
        if "search_size" in kwargs and kwargs["search_size"] is not None:
            if not queryset.ordered:
                queryset = queryset.order_by("accession")
            self.current_size = kwargs["search_size"]

        return super(CustomPagination, self).paginate_queryset(
            queryset, request, kwargs["view"]
        )

    def get_next_link(self):
        if not self.has_next():
            return None
        url = replace_url_host(self.request.build_absolute_uri())
        page_number = self.page.number + 1
        return replace_query_param(url, self.page_query_param, page_number)

    def has_next(self):
        if self.current_size is None:
            return False
        return self.page.number * self.page.paginator.per_page < self.current_size

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = replace_url_host(self.request.build_absolute_uri())
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
