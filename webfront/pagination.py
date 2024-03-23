from collections import OrderedDict
from django.core.paginator import Paginator as DjangoPaginator

from webfront.response import Response
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.utils.urls import replace_query_param, remove_query_param
from django.conf import settings

from django.http import QueryDict


def replace_url_host(url):
    host = settings.INTERPRO_CONFIG.get("api_url", "http://localhost:8007/api/")
    divider = "/wwwapi/" if "/wwwapi/" in url else "/api/"
    return host + url.split(divider)[1]


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
    elastic_result = None

    def get_paginated_response(self, data):
        base = [
            ("count", self.current_size),
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            ("results", self._sortBasedOnElastic(data["data"])),
        ]
        if "extensions" in data and len(data["extensions"]) > 0:
            for ext in data["extensions"]:
                base.append((ext, data["extensions"][ext]))
        return Response(OrderedDict(base))

    # If there is data in elastic_result, implies that the wueryset was created by querying elastic first.
    # This method uses the list of accession retrieved via elastic to order the results.
    def _sortBasedOnElastic(self, data):
        if self.elastic_result is None:
            return data
        ordered_data = []
        for acc in self.elastic_result:
            obj = next(
                filter(
                    lambda item: item.get("metadata", {}).get("accession", "").lower()
                    == acc.lower(),
                    data,
                ),
                None,
            )
            if obj is not None:
                ordered_data.append(obj)
        return ordered_data

    def _get_position_from_instance(self, instance, ordering):
        if type(instance) == tuple:
            return instance[0]
        return super(CustomPagination, self)._get_position_from_instance(
            instance, ordering
        )

    # Extract some values passed as kwargs before invoking the implementation in the super class
    def paginate_queryset(self, queryset, request, **kwargs):
        self.current_size = None
        self.after_key = None
        self.elastic_result = None
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
        if "elastic_result" in kwargs and kwargs["elastic_result"] is not None:
            self.elastic_result = kwargs["elastic_result"]
        if "ordering" in kwargs and kwargs["ordering"] is not None:
            self.ordering = kwargs["ordering"]
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
        self.base_url = replace_url_host(self.base_url)
        if self.after_key is None:
            return super(CustomPagination, self).get_next_link()
        return replace_query_param(self.base_url, "cursor", self.after_key)

    def get_previous_link(self):
        if not self.has_prev_page():
            return None
        self.base_url = replace_url_host(self.base_url)
        if self.before_key is None:
            return super(CustomPagination, self).get_previous_link()
        return replace_query_param(
            self.base_url, "cursor", "-{}".format(self.before_key)
        )
