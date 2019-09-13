from webfront.models.interpro_new import Release_Note, Protein

from webfront.response import Response
from rest_framework import status

from webfront.views.custom import CustomView
from webfront.exceptions import EmptyQuerysetError
from webfront.serializers.content_serializers import ModelContentSerializer

endpoints = [
    {"name": "entry", "db": "entry_db", "accession": "entry_acc"},
    {"name": "protein", "db": "protein_db", "accession": "protein_acc"},
    {"name": "structure", "db": "pdb", "accession": "structure_acc"},
    {"name": "taxonomy", "db": "uniprot", "accession": "tax_id"},
    {"name": "proteome", "db": "uniprot", "accession": "proteome_acc"},
    {"name": "set", "db": "set_db", "accession": "set_acc"},
]


class TimeoutHandler(CustomView):
    level_description = "Timeout level"
    from_model = False
    many = False
    serializer_class = ModelContentSerializer

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):
        print("TIMING out")
        content = {"detail": "This endpoint is always going to return a time-out"}
        response = Response(content, status=status.HTTP_408_REQUEST_TIMEOUT)
        return response


class TestEndpointHandler(CustomView):
    level_description = "Test level"
    from_model = False
    many = False
    serializer_class = ModelContentSerializer
    child_handlers = [(r".*", TimeoutHandler)]

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        self.queryset = {"testing endpoints": ["timeout"]}

        return super(TestEndpointHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )


class AccessionHandler(CustomView):
    level_description = "Accession level"
    from_model = False
    child_handlers = [(r".*",)]
    many = False
    serializer_class = ModelContentSerializer

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        acc = endpoint_levels[level - 1].lower()
        docs = general_handler.searcher.get_document_by_any_accession(acc)

        self.queryset = {}
        if len(docs["hits"]["hits"]) == 0:
            qs = Protein.objects.filter(identifier__iexact=acc)
            if qs.count() > 0:
                first = qs.first()
                self.queryset = {
                    "endpoint": "protein",
                    "source_database": first.source_database,
                    "accession": first.accession,
                }
        else:
            hit = docs["hits"]["hits"][0]["_source"]

            for ep in endpoints:
                if ep["accession"] in hit and hit[ep["accession"]] == acc:
                    db = ep["db"]
                    if ep["name"] in ["entry", "protein", "set"]:
                        db = hit[ep["db"]]
                    if not (db.lower() == "cdd" or db.lower() == "pdb"):
                        acc = acc.upper()
                    self.queryset = {
                        "endpoint": ep["name"],
                        "source_database": db,
                        "accession": acc,
                    }
        if self.queryset == {}:
            raise EmptyQuerysetError(
                "No accessions matching {} can be found in our data".format(acc)
            )

        return super(AccessionHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )


class AccessionEndpointHandler(CustomView):
    level_description = "Accession Endpoint level"
    from_model = False
    child_handlers = [(r".*", AccessionHandler)]
    many = False
    serializer_class = ModelContentSerializer

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        self.queryset = {
            "required": """This endpoint requires an accession in the next part of the URL. 
            e.g. /utils/accession/IPR00001"""
        }

        return super(AccessionEndpointHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )


class ReleaseVersionEndpointHandler(CustomView):
    level_description = "Release level"
    from_model = False
    many = False
    serializer_class = ModelContentSerializer

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        note_version = endpoint_levels[level - 1].lower()
        notes = Release_Note.objects.all()
        if note_version == "current":
            notes = notes.order_by("-release_date")
        else:
            notes = notes.filter(version=note_version)
        if notes.count() == 0:
            raise ReferenceError("Nothing found for version {}".format(note_version))

        note = notes.first()
        self.queryset = {
            "version": note.version,
            "release_date": note.release_date,
            "content": note.content,
        }

        return super(ReleaseVersionEndpointHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )


class ReleaseEndpointHandler(CustomView):
    level_description = "Release level"
    from_model = False
    child_handlers = [(r"current|(\d\d\.\d)", ReleaseVersionEndpointHandler)]
    many = False
    serializer_class = ModelContentSerializer

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        self.queryset = {
            note.version: note.release_date for note in Release_Note.objects.all()
        }

        return super(ReleaseEndpointHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )


class UtilsHandler(CustomView):
    level_description = "Utils level"
    from_model = False
    child_handlers = [
        ("accession", AccessionEndpointHandler),
        ("release", ReleaseEndpointHandler),
        ("test", TestEndpointHandler),
    ]
    many = False
    serializer_class = ModelContentSerializer

    def get(
        self,
        request,
        endpoint_levels,
        available_endpoint_handlers=None,
        level=0,
        parent_queryset=None,
        handler=None,
        general_handler=None,
        *args,
        **kwargs
    ):

        self.queryset = {"available": [ch[0] for ch in self.child_handlers]}

        return super(UtilsHandler, self).get(
            request._request,
            endpoint_levels,
            available_endpoint_handlers,
            level,
            self.queryset,
            handler,
            general_handler,
            request,
            *args,
            **kwargs
        )
