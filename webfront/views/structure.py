from webfront.models import DwEntryStructure
from webfront.serializers.pdb import StructureOverviewSerializer,StructureSerializer
from webfront.views import CustomView


class PDBAccessionHandler(CustomView):
    level = 3
    level_description = 'pdb accession level'
    queryset = DwEntryStructure.objects
    django_db = 'interpro_dw'

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = self.queryset.filter(xref_identifier=endpoint_levels[self.level-1].lower()
                                            )

        return super(PDBAccessionHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )

    serializer_class = StructureSerializer


class PDBHandler(CustomView):
    level = 2
    level_description = 'pdb level'
    child_handlers = {
        r'[1-9][A-Za-z0-9]{3}': PDBAccessionHandler,
    }
    django_db = 'interpro_dw'

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = DwEntryStructure.objects.using('interpro_dw').filter(dbcode='b')
        return super(PDBHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )

    serializer_class = StructureSerializer


class StructureHandler(CustomView):
    level = 1
    level_description = 'section level'
    from_model = False
    many = False
    child_handlers = {
        'pdb': PDBHandler,
    }
    django_db = 'interpro_dw'

    def get(self, request, endpoint_levels, *args, **kwargs):

        self.queryset = DwEntryStructure.objects.using('interpro_dw').filter(dbcode='b').distinct().count()
        return super(StructureHandler, self).get(
            request, endpoint_levels, *args, **kwargs
        )

    serializer_class = StructureOverviewSerializer


