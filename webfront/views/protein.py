from webfront.models import Protein
from webfront.serializers.uniprot import ProteinSerializer, ProteinOverviewSerializer
from webfront.views import CustomView


class UniprotAccessionHandler(CustomView):
    level = 3
    level_description = 'uniprot accession level'
    queryset = Protein.objects

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = self.queryset.filter(protein_ac=endpoint_levels[self.level-1])

        return super(UniprotAccessionHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )

    serializer_class = ProteinSerializer


class UniprotHandler(CustomView):
    level = 2
    level_description = 'uniprot level'
    child_handlers = {
        r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}': UniprotAccessionHandler,
    }
    queryset = Protein.objects
    serializer_class = ProteinSerializer


class ProteinHandler(CustomView):
    level = 1
    level_description = 'section level'
    from_model = False
    many = False
    child_handlers = {
        'uniprot': UniprotHandler,
    }
    def get(self, request, endpoint_levels, *args, **kwargs):


        self.queryset = Protein.objects.using('interpro_ro').all().count()
        return super(ProteinHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )

    serializer_class = ProteinOverviewSerializer

