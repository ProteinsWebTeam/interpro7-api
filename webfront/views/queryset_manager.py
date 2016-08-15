from webfront.models import Entry, Protein, Structure


class QuerysetManager:
    main_endpoint = None
    filters = {
        "entry": {},
        "structure": {},
        "protein": {},
    }

    def reset_filters(self, endpoint):
        self.main_endpoint = endpoint
        self.filters = {
            "entry": {},
            "structure": {},
            "protein": {},
        }

    def add_filter(self, endpoint,  **kwargs):
        self.filters[endpoint] = {**self.filters[endpoint], **kwargs}

    def remove_filter(self, endpoint, f):
        del self.filters[endpoint][f]

    def get_queryset(self, endpoint=None, only_main_endpoint=False):
        if endpoint is None:
            endpoint = self.main_endpoint
        if endpoint == "entry":
            queryset = Entry.objects.all()
        elif endpoint == "structure":
            queryset = Structure.objects.all()
        elif endpoint == "protein":
            queryset = Protein.objects.all()
        current_filters = {}
        for ep in self.filters:
            if ep == endpoint:
                current_filters = {**current_filters, **self.filters[ep]}
            elif not only_main_endpoint:
                current_filters = {**current_filters, **{ep+"__"+k: v for k,v in self.filters[ep].items()}}

        return queryset.filter(**current_filters)
