from urllib.error import URLError
from webfront.views.custom import is_single_endpoint

from django.db.models import Count


def group_by(endpoint_queryset, fields):
    def inner(field, general_handler):
        if field not in fields:
            raise URLError("{} is not a valid field to group entries by. Allowed fields : {}".format(
                field, ", ".join(fields.keys())
            ))
        if is_single_endpoint(general_handler):
            queryset = general_handler.queryset_manager.get_queryset().distinct()
            qs = endpoint_queryset.objects.filter(accession__in=queryset)
            return qs.values_list(field).annotate(total=Count(field))
        else:
            searcher = general_handler.searcher
            result = searcher.get_grouped_object(
                general_handler.queryset_manager.main_endpoint, fields[field]
            )
            return result
    return inner


def sort_by(fields):
    def x(field, general_handler):
        if not is_single_endpoint(general_handler):
            # wl = {k: v for k, v in wl.items() if v is not None}
            raise URLError("Sorting is not currently supported for multi-domains queries")

        if field not in fields:
            raise URLError("This query can't be be sorted by {}. The supported fields are {}".format(
                field, ", ".join(fields.keys())
            ))
        general_handler.queryset_manager.order_by(field)
    return x


def filter_by_field(endpoint, field):
    def x(value, general_handler):
        general_handler.queryset_manager.add_filter(
            endpoint,
            **{"{}__iexact".format(field): value}
        )
    return x
