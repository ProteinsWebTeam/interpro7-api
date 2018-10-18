from django.shortcuts import redirect

from webfront.models.interpro_new import Release_Note

from webfront.views.custom import CustomView
from webfront.serializers.content_serializers import ModelContentSerializer

endpoints = [
    {"name": "entry", "db": "entry_db", "accession": "entry_acc"},
    {"name": "protein", "db": "protein_db", "accession": "protein_acc"},
    {"name": "structure", "db": "pdb", "accession": "structure_acc"},
    {"name": "taxonomy", "db": "uniprot", "accession": "tax_id"},
    {"name": "proteome", "db": "uniprot", "accession": "proteome_acc"},
    {"name": "set", "db": "set_db", "accession": "set_acc"},
]
class AccessionHandler(CustomView):
    level_description = 'Accession level'
    from_model = False
    child_handlers = [
        (r'.*', )
    ]
    many = False
    serializer_class = ModelContentSerializer

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        acc = endpoint_levels[level - 1].lower()
        docs = general_handler.searcher.get_document_by_any_accession(acc)

        if len(docs["hits"]["hits"]) == 0:
            raise ReferenceError("No accessions matching {} can be found in our data"
                                 .format(acc))

        hit = docs["hits"]["hits"][0]["_source"]

        self.queryset = {}
        for ep in endpoints:
            if hit[ep["accession"]] == acc:
                db = ep["db"]
                if ep["name"] in ["entry", "protein", "set"]:
                    db = hit[ep["db"]]
                self.queryset = {
                    "endpoint": ep["name"],
                    "source_database": db,
                    "accession": acc
                }

        return super(AccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )


class AccessionEndpointHandler(CustomView):
    level_description = 'Accession Endpoint level'
    from_model = False
    child_handlers = [
        (r'.*', AccessionHandler),
    ]
    many = False
    serializer_class = ModelContentSerializer

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        self.queryset = {
            "required": """This endpoint requires an accession in the next part of the URL. 
            e.g. /utils/accession/IPR00001"""
        }

        return super(AccessionEndpointHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )


class ReleaseVersionEndpointHandler(CustomView):
    level_description = 'Release level'
    from_model = False
    many = False
    serializer_class = ModelContentSerializer

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        note_version = endpoint_levels[level - 1].lower()
        notes = Release_Note.objects.all()
        if note_version == "current":
            notes = notes.order_by('-release_date')
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
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

class ReleaseEndpointHandler(CustomView):
    level_description = 'Release level'
    from_model = False
    child_handlers = [
        (r'current|(\d\d\.\d)', ReleaseVersionEndpointHandler),
    ]
    many = False
    serializer_class = ModelContentSerializer

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        self.queryset = {
            note.version: note.release_date
            for note in Release_Note.objects.all()
        }

        return super(ReleaseEndpointHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )


class UtilsHandler(CustomView):
    level_description = 'Utils level'
    from_model = False
    child_handlers = [
        ("accession", AccessionEndpointHandler),
        ("release", ReleaseEndpointHandler),
    ]
    many = False
    serializer_class = ModelContentSerializer

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        self.queryset = {"available": [ch[0] for ch in self.child_handlers]}

        return super(UtilsHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

