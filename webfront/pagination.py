from rest_framework.pagination import CursorPagination


class CustomPagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    ordering = '-accession'
