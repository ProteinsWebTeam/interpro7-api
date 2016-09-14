from webfront.models import Entry, Protein, Structure
from django.db.models import Q
from functools import reduce
from operator import or_
from django.db.models import F
from django.db.models import Count


class QuerysetManager:
    main_endpoint = None
    filters = {
        "search": {},
        "entry": {},
        "structure": {},
        "protein": {},
    }
    endpoints = []

    def reset_filters(self, endpoint, endpoint_levels=[]):
        self.main_endpoint = endpoint
        self.endpoints = endpoint_levels
        self.filters = {
            "search": {},
            "entry": {},
            "structure": {},
            "protein": {},
        }

    def add_filter(self, endpoint,  **kwargs):
        self.filters[endpoint] = {**self.filters[endpoint], **kwargs}

    def remove_filter(self, endpoint, f):
        del self.filters[endpoint][f]

    def get_join_filters(self, endpoint):
        join_filters = {}
        if "entry" == endpoint:
            if "structure" in self.endpoints:
                join_filters["entrystructurefeature__structure_id"] = F('structure__accession')
                # join_filters["entrystructurefeature__entry_id"] = F('accession')
                if "protein" in self.endpoints:
                    join_filters["structure__proteinstructurefeature__protein_id"] = F('structure__protein__accession')
                    join_filters["protein__proteinstructurefeature__structure_id"] = F('protein__structure__accession')
                    # join_filters["proteinentryfeature__entry_id"] = F('entrystructurefeature__entry_id')
                    join_filters["structure__proteinstructurefeature__protein_id"] = F('protein__accession')
                    # join_filters["proteinstructurefeature__structure_id"] = F('entrystructurefeature__structure_id')
                    # join_filters["proteinstructurefeature__structure_id"] = F('proteinstructurefeature__structure_id')
                    # join_filters["structure__proteinstructurefeature__structure_id"] = F('structure__accession')
            if "protein" in self.endpoints:
                join_filters["proteinentryfeature__protein_id"] = F('protein__accession')
                # join_filters["proteinentryfeature__entry_id"] = F('accession')

        elif "protein" == endpoint:
            if "structure" in self.endpoints:
                join_filters["proteinstructurefeature__structure_id"] = F('structure__accession')
                # join_filters["proteinstructurefeature__protein_id"] = F('accession')
                if "entry" in self.endpoints:
                    # join_filters["structure__entrystructurefeature__entry_id"] = F('structure__entry__accession')
                    join_filters["entry__entrystructurefeature__structure_id"] = F('structure__accession')
                    join_filters["entry__structure__accession"] = F('structure__accession')
                    join_filters["structure__entrystructurefeature__entry_id"] = F('entry__accession')
                    join_filters["structure__entry__accession"] = F('entry__accession')
            if "entry" in self.endpoints:
                join_filters["proteinentryfeature__entry_id"] = F('entry__accession')
                # join_filters["proteinentryfeature__protein_id"] = F('accession')

        if "structure" == endpoint:
            if "entry" in self.endpoints:
                join_filters["entrystructurefeature__entry_id"] = F('entry__accession')
                # join_filters["entrystructurefeature__structure_id"] = F('accession')
                if "protein" in self.endpoints:
                    join_filters["entry__proteinentryfeature__protein_id"] = F('entry__protein__accession')
                    join_filters["protein__proteinentryfeature__entry_id"] = F('protein__entry__accession')
                    join_filters["entry__proteinentryfeature__protein_id"] = F('protein__accession')
                    # join_filters["entry__proteinentryfeature__entry_id"] = F('entry__accession')
            if "protein" in self.endpoints:
                join_filters["proteinstructurefeature__protein_id"] = F('protein__accession')
                # join_filters["proteinstructurefeature__structure_id"] = F('accession')
        return join_filters

    def get_queryset(self, endpoint=None, only_main_endpoint=False):
        queryset = Entry.objects.all()
        if endpoint is None:
            endpoint = self.main_endpoint
        if endpoint == "entry":
            queryset = Entry.objects.all()
        elif endpoint == "structure":
            queryset = Structure.objects.all()
        elif endpoint == "protein":
            queryset = Protein.objects.all()

        current_filters = {} if only_main_endpoint else self.get_join_filters(endpoint)

        # creates an `OR` filter for the search fields
        search_filters = self.filters.get("search")
        if search_filters:
            or_filter = reduce(
                or_,
                (Q(**{f[0]: f[1]}) for f in search_filters.items()),
            )

        for ep in self.filters:
            if ep == "search":
                continue
            if ep == endpoint:
                current_filters = {**current_filters, **{k: self.check_for_f(v, endpoint)
                                                         for k, v in self.filters[ep].items()}
                                   }
            elif not only_main_endpoint:
                current_filters = {**current_filters, **{ep+"__"+k: self.check_for_f(v, endpoint)
                                                         for k, v in self.filters[ep].items()}
                                   }

        if search_filters:
            return queryset.filter(or_filter, **current_filters)
        return queryset.filter(**current_filters)

    def check_for_f(self, value, endpoint):
        if isinstance(value, F):
            if value.name.startswith(endpoint+"__"):
                return F(value.name[len(endpoint+"__"):])
        return value

    def clone(self):
        c = QuerysetManager()
        c.main_endpoint = self.main_endpoint
        c.filters = self.filters.copy()
        c.endpoints = self.endpoints
        return c

    def group_and_count(self, endpoint_to_count):
        me = self.main_endpoint
        qs = self.get_queryset(endpoint_to_count)
        counter = qs.values("accession", me + '__accession').distinct() \
            .annotate(total=Count(me + '__accession'))
        pc = {}
        for row in counter:
            if row[me + '__accession'] not in pc:
                pc[row[me + '__accession']] = 0
            pc[row[me + '__accession']] += 1
        return pc
