from urllib.error import URLError
from webfront.views.custom import is_single_endpoint

from django.db.models import Count
from webfront.models import Entry


def group_by_member_databases(general_handler):
    if is_single_endpoint(general_handler):
        holder = general_handler.queryset_manager.remove_filter('entry', 'source_database__iexact')
        dbs = Entry.objects.get_queryset().values('source_database').distinct()
        qs = {db['source_database']:
                  general_handler.queryset_manager.get_queryset()
                      .filter(member_databases__contains=db['source_database'])
                      .count()
              for db in dbs
              }

        general_handler.queryset_manager.add_filter('entry', source_database__iexact=holder)
        return qs


def group_by_go_terms(general_handler):
    if is_single_endpoint(general_handler):
        categories = {"P": "Biological Process", "C": "Cellular Component", "F": "Molecular Function"}
        qs = {categories[cat]:
                  general_handler.queryset_manager.get_queryset()
                      .filter(go_terms__contains='"category": "{}"'.format(cat))
                      .count()
              for cat in categories
              }
        return qs


def group_by_organism(general_handler,endpoint_queryset):
        queryset = general_handler.queryset_manager.get_queryset().distinct()
        qs = endpoint_queryset.objects.filter(accession__in=queryset)
        return qs.values_list("tax_id").annotate(total=Count("tax_id")).order_by('-total').distinct()[:30]



def group_by(endpoint_queryset, fields):
    def inner(field, general_handler):
        if field not in fields:
            raise URLError("{} is not a valid field to group entries by. Allowed fields : {}".format(
                field, ", ".join(fields.keys())
            ))
        if "member_databases" == field:
            return group_by_member_databases(general_handler)
        if "go_terms" == field:
            return group_by_go_terms(general_handler)
        if is_single_endpoint(general_handler):
            if "tax_id" == field:
                return group_by_organism(general_handler, endpoint_queryset)
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

        if field not in fields and field[1:] not in fields:
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


def filter_by_contains_field(endpoint, field, value_template='{}'):
    def x(value, general_handler):
        general_handler.queryset_manager.add_filter(
            endpoint,
            **{"{}__contains".format(field): value_template.format(value)}
        )
    return x

def filter_by_field_range(endpoint, field, value_template='{}'):
    def x(value, general_handler):
        pos = value.split('-')
        general_handler.queryset_manager.add_filter(
            endpoint,
            **{
                "{}__gte".format(field): value_template.format(pos[0]),
                "{}__lte".format(field): value_template.format(pos[1]),
            }
        )
    return x

def get_single_value(field):
    def x(value, general_handler):
        queryset = general_handler.queryset_manager.get_queryset()
        first = queryset.first()
        return first.__getattribute__(field)
    return x


def get_interpro_status_counter(field, general_handler):
    queryset = general_handler.queryset_manager.get_queryset().distinct()
    total = queryset.count()
    unintegrated = queryset.filter(integrated__isnull=True).count()
    return {
        "integrated": total - unintegrated,
        "unintegrated": unintegrated,
    }


def get_domain_architectures(field, general_handler):
    searcher = general_handler.searcher
    rows = general_handler.pagination["size"] if "size" in general_handler.pagination else 10
    index = general_handler.pagination["index"] if "index" in general_handler.pagination else 1
    if field is None or field.strip() == "":
        return searcher.get_group_obj_of_field_by_query(
            None, "IDA_FK", rows=rows, start=index*rows-rows,
            inner_field_to_count="protein_acc")
    else:
        query = general_handler.queryset_manager.get_searcher_query() + " && IDA_FK:" + field
        res, length = searcher.get_list_of_endpoint("protein", query, rows, index*rows-rows)
        return general_handler.queryset_manager\
            .get_base_queryset("protein")\
            .filter(accession__in=res)