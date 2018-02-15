from webfront.models import Entry, Protein, Structure, Taxonomy, Proteome, Set
from django.db.models import Q
from functools import reduce
from operator import or_
import re


def escape(text):
    return re.sub(r'([-+!(){}[\]^"~*?:\\\/])', r"\\\1", str(text))


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


class QuerysetManager:
    main_endpoint = None
    filters = {}
    exclusions = {}
    endpoints = []
    order_field =None;

    def reset_filters(self, endpoint, endpoint_levels=[]):
        self.main_endpoint = endpoint
        self.endpoints = endpoint_levels
        self.filters = {
            "search": {},
            "solr": {},
            "entry": {},
            "structure": {},
            "protein": {},
            "taxonomy": {},
            "proteome": {},
            "set": {},
        }
        self.exclusions = self.filters.copy()
        self.order_field = None

    def add_filter(self, endpoint,  **kwargs):
        self.filters[endpoint] = merge_two_dicts(self.filters[endpoint], kwargs)

    def add_exclusion(self, endpoint,  **kwargs):
        self.exclusions[endpoint] = merge_two_dicts(self.exclusions[endpoint], kwargs)

    def remove_filter(self, endpoint, f):
        tmp = self.filters[endpoint][f]
        del self.filters[endpoint][f]
        return tmp

    def order_by(self,field):
        self.order_field = field


    def get_searcher_query(self, include_search=False):
        q = ""
        for ep in self.filters:
            for k, v in self.filters[ep].items():
                if ep == "solr":
                    q += " && {}:{}".format(k, escape(v))
                elif include_search and ep == "search":
                    main_ep = self.main_endpoint
                    if main_ep == "taxonomy" or main_ep == "proteome":
                        main_ep = "organism"
                    q += " && text_{}:*{}*".format(main_ep, escape(v))
                elif k == "source_database__isnull":
                    q += " && {}{}_db:*".format("!" if v else "", ep)
                elif k == "accession" or k == "accession__iexact":
                    if ep == 'taxonomy':
                        q += " && lineage:{}".format(escape(v))
                    elif ep == 'proteome':
                        q += " && proteomes:{}".format(escape(v))
                    else:
                        q += " && {}_acc:{}".format(ep, escape(v))
                elif k == "accession__isnull":
                    # elasticsearch perform better if the "give me all" query runs over a
                    # low cardinality field such as the _db ones
                    if ep == 'structure':
                        q += " && {}{}_acc:*".format("!" if v else "", ep)
                    elif ep == 'taxonomy':
                        q += " && {}tax_id:[1 to *]".format("!" if v else "")
                    elif ep == 'proteome':
                        q += " && {}proteomes:*".format("!" if v else "")
                    else:
                        q += " && {}{}_db:*".format("!" if v else "", ep)
                elif k == "integrated" or k == "integrated__iexact" or k == "integrated__contains":
                    if ep == 'set':
                        if not v:
                            q += " && !_exists_:set_integrated"
                        else:
                            q += " && set_integrated:{}".format(escape(v))
                    else:
                        q += " && integrated:{}".format(escape(v))
                elif k == "integrated__isnull":
                    if ep == 'set':
                        q += " && {}set_integrated:*".format("!" if v else "")
                    else:
                        q += " && {}integrated:*".format("!entry_db:interpro && !" if v else "")
                elif k == "type" or k == "type__iexact":
                    q += " && {}_type:{}".format(ep, escape(v))
                elif k == "tax_id" or k == "tax_id__iexact" or k == "tax_id__contains":
                    q += " && tax_id:{}".format(escape(v))
                elif "lineage__contains" in k:
                    q += " && lineage:{}".format(escape(v).strip())
                elif "experiment_type__iexact" in k:
                    q += " && structure_evidence:{}".format(escape(v).strip())
                elif "__gt" in k:
                    q += " && {}:{}{} TO *]".format(
                        re.sub(r"__gte?", "", k),
                        "[" if "__gte" in k else "{",
                        escape(v)
                    )
                elif "__lt" in k:
                    q += " && {}:[* TO {}{}".format(
                        re.sub(r"__lte?", "", k),
                        escape(v),
                        "]" if "__lte" in k else "}"
                    )
                elif ep != "structure":
                    if k == "source_database" or k == "source_database__iexact":
                        q += " && {}_db:{}".format(ep, escape(v))

        q = q[4:].lower()
        if self.order_field is not None:
            q += "&sort="+self.order_field
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
        return queryset

    @staticmethod
    def get_current_filters(filters, endpoint, only_main_endpoint):
        current_filters = {}
        for ep in filters:
            if ep == "search" or ep == "solr":
                continue
            if ep == endpoint:
                current_filters = merge_two_dicts(
                    current_filters,
                    {k: v for k, v in filters[ep].items()}
                )
            elif not only_main_endpoint:
                current_filters = merge_two_dicts(
                    current_filters,
                    {ep+"__"+k: v for k, v in filters[ep].items()}
                )
        return current_filters

    def get_queryset(self, endpoint=None, only_main_endpoint=False):
        if endpoint is None:
            endpoint = self.main_endpoint
        queryset = self.get_base_queryset(endpoint)
        current_filters = self.get_current_filters(self.filters, endpoint, only_main_endpoint)
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
        if len(current_exclusions)>0:
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
                self.filters[endpoint]["integrated__iexact"] = f
                del self.filters[endpoint][k]
