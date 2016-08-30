from webfront.models import Entry, Protein, Structure
from django.db.models import Q
from functools import reduce
from operator import or_


class QuerysetManager:
    main_endpoint = None
    filters = {
        "search": {},
        "entry": {},
        "structure": {},
        "protein": {},
    }

    def reset_filters(self, endpoint):
        self.main_endpoint = endpoint
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

        current_filters = {}

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
                current_filters = {**current_filters, **self.filters[ep]}
            elif not only_main_endpoint:
                current_filters = {**current_filters, **{ep+"__"+k: v for k, v in self.filters[ep].items()}}

        if search_filters:
            return queryset.filter(or_filter, **current_filters)
        return queryset.filter(**current_filters)
