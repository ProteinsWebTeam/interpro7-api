from webfront.models import Entry, Protein, Structure, Taxonomy, Proteome, Set, Alignment
from django.db.models import Q
from functools import reduce
from operator import or_
import re


def escape(text):
    return re.sub(r'([-+!(){}[\]^"~*?:\\\/])', r"\\\1", str(text))


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def uses_wildcards(query):
    return re.match(r'[-+!(){}[\]^"~*?:\\\/]', query) is not None


class QuerysetManager:
    main_endpoint = None
    filters = {}
    exclusions = {}
    endpoints = []
    order_field = None
    other_fields = None

    def reset_filters(self, endpoint, endpoint_levels=[]):
        self.main_endpoint = endpoint
        self.endpoints = endpoint_levels
        self.filters = {
            "search": {},
            "searcher": {},
            "entry": {},
            "structure": {},
            "protein": {},
            "taxonomy": {},
            "proteome": {},
            "set": {},
            "set_alignment": {},
        }
        self.exclusions = self.filters.copy()
        self.order_field = None

    def set_main_endpoint(self, endpoint):
        self.main_endpoint = endpoint

    def add_filter(self, endpoint, **kwargs):
        self.filters[endpoint] = merge_two_dicts(self.filters[endpoint], kwargs)

    def add_exclusion(self, endpoint, **kwargs):
        self.exclusions[endpoint] = merge_two_dicts(self.exclusions[endpoint], kwargs)

    def remove_filter(self, endpoint, f):
        tmp = self.filters[endpoint][f]
        del self.filters[endpoint][f]
        return tmp

    def order_by(self, field):
        self.order_field = field

    def get_searcher_query(self, include_search=False):
        blocks = []
        for ep in self.filters:
            for k, v in self.filters[ep].items():
                if ep == "searcher":
                    blocks.append("{}:{}".format(k, escape(v)))
                elif ep == "proteome" and k == "is_reference":
                    blocks.append("proteome_is_reference:{}".format(escape(v).strip()))
                elif include_search and ep == "search":
                    main_ep = self.main_endpoint
                    if uses_wildcards(v):
                        blocks.append("text_{}:{}".format(main_ep, v.replace(' ', '%20')))
                    else:
                        for token in v.split():
                            blocks.append("text_{}:{}~0".format(main_ep, token))
                elif k == "source_database__isnull":
                    blocks.append("{}_exists_:{}_db".format("!" if v else "", ep))
                elif k == "accession" or k == "accession__iexact":
                    if ep == 'taxonomy':
                        blocks.append("tax_lineage:{}".format(escape(v)))
                    else:
                        blocks.append("{}_acc:{}".format(ep, escape(v)))
                elif k == "accession__isnull":
                    if ep == 'structure':
                        blocks.append("{}_exists_:{}_acc".format("!" if v else "", ep))
                    elif ep == 'taxonomy':
                        blocks.append("{}_exists_:tax_id".format("!" if v else ""))
                    elif ep == 'proteome':
                        blocks.append("{}_exists_:proteome_acc".format("!" if v else ""))
                    else:
                        blocks.append("{}_exists_:{}_db".format("!" if v else "", ep))

                elif k == 'accession__in' and ep == 'taxonomy' and isinstance(v, list) and len(v) > 0:
                    blocks.append("({})".format(
                        " || ".join(["tax_id:{}".format(value) for value in v])
                    ))
                elif k == "integrated" or k == "integrated__accession__iexact" or k == "integrated__iexact" or k == "integrated__contains":
                    if ep == 'set':
                        if not v:
                            blocks.append("!_exists_:set_integrated")
                        else:
                            blocks.append("set_integrated:{}".format(escape(v)))
                    else:
                        blocks.append("entry_integrated:{}".format(escape(v)))
                elif k == "integrated__isnull":
                    if ep == 'set':
                        blocks.append("{}_exists_:set_integrated".format("!" if v else ""))
                    else:
                        blocks.append("{}_exists_:entry_integrated".format("!entry_db:interpro && !" if v else ""))
                elif k == "type" or k == "type__iexact" or k == "type__exact":
                    blocks.append("{}_type:{}".format(ep, escape(v)))
                elif k == "tax_id" or k == "tax_id__iexact" or k == "tax_id__contains":
                    blocks.append("tax_id:{}".format(escape(v)))
                elif "tax_lineage__contains" in k:
                    blocks.append("tax_lineage:{}".format(escape(v).strip()))
                elif "experiment_type__" in k:
                    blocks.append("structure_evidence:{}".format(escape(v).strip()))
                elif ep == "protein" and "size__" in k:
                    blocks.append("protein_size:{}".format(escape(v).strip()))
                elif "__gt" in k:
                    filter_k = "protein_" + k if k.startswith("length_") else k
                    blocks.append("{}:{}{} TO *]".format(
                        re.sub(r"__gte?", "", filter_k),
                        "[" if "__gte" in filter_k else "{",
                        escape(v)
                    ))
                elif "__lt" in k:
                    filter_k = "protein_" + k if k.startswith("length_") else k
                    blocks.append("{}:[* TO {}{}".format(
                        re.sub(r"__lte?", "", filter_k),
                        escape(v),
                        "]" if "__lte" in filter_k else "}"
                    ))
                elif ep != "structure":
                    if k == "source_database" or k == "source_database__iexact":
                        blocks.append("{}_db:{}".format(ep, escape(v)))

        blocks = list(set(blocks))
        blocks.sort()
        q = " && ".join(blocks).lower()
        if self.order_field is not None:
            q += "&sort=" + self.order_field
        return q

    def get_base_queryset(self, endpoint):
        queryset = Entry.objects.all()
        if endpoint == "entry":
            queryset = Entry.objects.all()
        elif endpoint == "structure":
            queryset = Structure.objects.all()
        elif endpoint == "protein":
            queryset = Protein.objects.all()
        elif endpoint == "proteome":
            queryset = Proteome.objects.all()
        elif endpoint == "taxonomy":
            queryset = Taxonomy.objects.all()
        elif endpoint == "set":
            queryset = Set.objects.all()
        elif endpoint == "set_alignment":
            queryset = Alignment.objects.all()
        return queryset

    @staticmethod
    def get_current_filters(filters, endpoint, only_main_endpoint):
        current_filters = {}
        for ep in filters:
            if ep == "search" or ep == "searcher":
                continue
            if ep == endpoint:
                current_filters = merge_two_dicts(
                    current_filters,
                    {k: v for k, v in filters[ep].items()}
                )
            elif not only_main_endpoint:
                current_filters = merge_two_dicts(
                    current_filters,
                    {ep + "__" + k: v for k, v in filters[ep].items()}
                )
        return current_filters

    def get_queryset(self, endpoint=None, only_main_endpoint=False):
        if endpoint is None:
            endpoint = self.main_endpoint
        queryset = self.get_base_queryset(endpoint)
        current_filters = self.get_current_filters(self.filters, endpoint, only_main_endpoint)
        if "accession__isnull" in current_filters:
            del current_filters["accession__isnull"]
        current_exclusions = self.get_current_filters(self.exclusions, endpoint, only_main_endpoint)

        # creates an `OR` filter for the search fields
        search_filters = self.filters.get("search")
        if search_filters:
            or_filter = reduce(
                or_,
                (Q(**{f[0]: f[1]}) for f in search_filters.items()),
            )
            queryset = queryset.filter(or_filter, **current_filters)
        queryset = queryset.filter(**current_filters)
        if len(current_exclusions) > 0:
            queryset = queryset.exclude(**current_exclusions)
        if self.order_field is not None:
            queryset = queryset.order_by(self.order_field)
        return queryset

    def update_integrated_filter(self, endpoint):
        c = self.filters[endpoint].copy()
        for k, f in c.items():
            if k == "source_database" or k == "source_database__iexact":
                if endpoint == "set" and "integrated" in c:
                    del self.filters[endpoint]["integrated"]
                else:
                    self.filters[endpoint]["integrated__isnull"] = False
                    del self.filters[endpoint][k]
            elif k == "accession" or k == "accession__iexact":
                self.filters[endpoint]["integrated__accession__iexact"] = f.lower()
                del self.filters[endpoint][k]

    def is_single_endpoint(self):
        main_ep = self.main_endpoint
        filters = [
            f for f in self.filters
            if f != main_ep and f != "search" and self.filters[f] != {}
        ]
        return len(filters) == 0
