
# class UniprotAccessionHandler(CustomView):
#     level_description = 'uniprot accession level'
#     queryset = DwEntryProteinsMatched.objects
#     django_db = 'interpro_dw'
#
#     def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, *args, **kwargs):
#
#         self.queryset = self.queryset.filter(protein_ac=endpoint_levels[level-1])
#
#         return super(UniprotAccessionHandler, self).get(
#             request, endpoint_levels, available_endpoint_handlers, level, *args, **kwargs
#         )
#
#     serializer_class = ProteinSerializer
#
#

from django.db.models import Count

from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.models import Protein

class UniprotAccessionHandler(CustomView):
    level_description = 'uniprot accession level'
    serializer_class = ProteinSerializer
    queryset = Protein.objects
    many = False

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, parent_queryset=None, *args, **kwargs):
        self.queryset = self.queryset.filter(accession=endpoint_levels[level-1])
        if self.queryset.count()==0:
            raise Exception("The ID '{}' has not been found in {}".format(endpoint_levels[level-1], endpoint_levels[level-2]))
        return super(UniprotAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, *args, **kwargs
        )

class IDAccessionHandler(CustomView):
    level_description = 'uniprot accession level'
    serializer_class = ProteinSerializer
    queryset = Protein.objects
    many = False

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, parent_queryset=None, *args, **kwargs):
        self.queryset = self.queryset.filter(identifier=endpoint_levels[level-1])
        if self.queryset.count()==0:
            raise Exception("The ID '{}' has not been found in {}".format(endpoint_levels[level-1], endpoint_levels[level-2]))
        return super(IDAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, *args, **kwargs
        )


class UniprotHandler(CustomView):
    level_description = 'uniprot level'
    child_handlers = [
        (r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}', UniprotAccessionHandler),
        (r'.+', IDAccessionHandler),
    ]
    queryset = Protein.objects.filter(source_database__iexact="uniprot")
    serializer_class = ProteinSerializer
    serializer_detail = SerializerDetail.HEADERS


class ProteinHandler(CustomView):
    level_description = 'section level'
    from_model = False
    child_handlers = [
        ('uniprot', UniprotHandler),
    ]

    def get(self, request, endpoint_levels, available_endpoint_handlers={}, level=0, parent_queryset=None, *args, **kwargs):
        protein_counter = Protein.objects.all().values('source_database').annotate(total=Count('source_database'))
        output = {}
        for row in protein_counter:
            output[row["source_database"]] = row["total"]

        self.queryset = output
        return super(ProteinHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level, *args, **kwargs
        )

