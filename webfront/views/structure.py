from django.db.models import Count
from webfront.constants import get_queryset_type, QuerysetType
from webfront.models import Structure, ProteinStructureFeature, Protein, EntryStructureFeature
from webfront.serializers.pdb import StructureSerializer
from webfront.views.custom import CustomView, SerializerDetail



def filter_protein_overview(obj, accession=None):
    for prot_db in obj:
        matches = ProteinStructureFeature.objects.all()
        if accession is not None:
            matches = matches.filter(structure=accession)
        if prot_db != "uniprot":
            matches = matches.filter(protein__source_database__iexact=prot_db)
        obj[prot_db] = {
            "proteins": matches.values("protein").distinct().count(),
            "structures": matches.values("structure").distinct().count()
        }

def filter_entry_overview(obj, accession=None):
    for entry_db in obj:
        matches = EntryStructureFeature.objects.all()
        if accession is not None:
            matches = matches.filter(structure=accession)
        if entry_db == "member_databases":
            for member_db in obj[entry_db]:
                matches2 = matches.filter(entry__source_database__iexact=member_db)
                obj[entry_db][member_db] = {
                    "structures": matches2.values("structure").distinct().count(),
                    "entries": matches2.values("entry").distinct().count()
                }
        else:
            if entry_db == "interpro":
                matches = matches.filter(entry__source_database__iexact=entry_db)
            elif entry_db == "unintegrated":
                matches = matches \
                    .filter(entry__integrated__isnull=True) \
                    .exclude(entry__source_database__iexact="interpro")
            obj[entry_db] = {
                "structures": matches.values("structure").distinct().count(),
                "entries": matches.values("entry").distinct().count()
            }


class ChainPDBAccessionHandler(CustomView):
    level_description = 'pdb accession level'
    serializer_class = StructureSerializer
    queryset = Structure.objects
    many = False
    serializer_detail = SerializerDetail.STRUCTURE_CHAIN
    serializer_detail_filter = SerializerDetail.STRUCTURE_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        if parent_queryset is not None:
            self.queryset = parent_queryset
        # self.queryset = self.queryset.filter(chains__contains=endpoint_levels[level - 1])
        self.queryset = self.queryset\
            .filter(proteinstructurefeature__chain=endpoint_levels[level - 1])

        # ProteinStructureFeature.objects\
        #     .filter(structure__in=self.queryset)\
        #     .filter(chain=endpoint_levels[level - 1])
        # self.queryset.filter(proteins__set__chain=endpoint_levels[level - 1])
        if self.queryset.count() == 0:
            raise Exception("The Chain '{}' has not been found in the structure {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2].upper()))
        return super(ChainPDBAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        qs_type = get_queryset_type(queryset)
        if not isinstance(queryset, dict):
            if qs_type == QuerysetType.PROTEIN:
                queryset = queryset.filter(proteinstructurefeature__protein__in=queryset,
                                           proteinstructurefeature__chain=level_name)
            if queryset.count() == 0:
                raise ReferenceError("The protein {} doesn't exist in the database {}".format(level_name, "pdb"))
            return queryset
        # if "interpro" in queryset:
        #     matches = EntryStructureFeature.objects.filter(structure=level_name)
        #     from webfront.views.entry import EntryHandler
        #     return EntryHandler.get_database_contributions(matches, 'entry__')
        # if "uniprot" in queryset:
        #     matches = ProteinStructureFeature.objects.filter(structure=level_name)
        #     from webfront.views.protein import ProteinHandler
        #     return ProteinHandler.get_database_contributions(matches, 'protein__')

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if type(obj) != dict:
                pdb = general_handler.get_from_store(PDBAccessionHandler, "pdb_accession")
                arr = obj
                if isinstance(obj, dict):
                    arr = [obj]
                for o in arr:
                    if "structures" in o:
                        o["structures"] = \
                            [p for p in o["structures"] if
                             ("chain" in p and
                              p["chain"] == level_name and
                              p["structure"]["accession"] == pdb) or
                             ("structure" in p and
                              "chain" in p["structure"] and
                              p["structure"]["chain"] == level_name and
                              p["structure"]["accession"] == pdb)
                             ]
                    if "entries" in o and isinstance(o["entries"], list):
                        o["entries"] = \
                            [p for p in o["entries"] if
                             ("chain" in p and
                              p["chain"] == level_name) or
                             ("structure" in p and
                              "chain" in p["structure"] and
                              p["entry"]["chain"] == level_name)
                             ]
                    if "metadata"in o and "chains" in o["metadata"] and isinstance(o["metadata"]["chains"], dict):
                        o["metadata"]["chains"] = \
                            {p:o["metadata"]["chains"][p] for p in o["metadata"]["chains"] if
                             (level_name in p)
                             }
        return obj


class PDBAccessionHandler(CustomView):
    level_description = 'pdb accession level'
    serializer_class = StructureSerializer
    queryset = Structure.objects
    many = False
    child_handlers = [
        (r'[a-z]|[A-Z]', ChainPDBAccessionHandler),
    ]
    serializer_detail_filter = SerializerDetail.STRUCTURE_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(accession__iexact=endpoint_levels[level - 1])
        general_handler.set_in_store(PDBAccessionHandler, "pdb_accession", endpoint_levels[level - 1])
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2]))
        return super(PDBAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        qs_type = get_queryset_type(queryset)
        general_handler.set_in_store(PDBAccessionHandler, "pdb_accession", level_name)
        if not isinstance(queryset, dict):
            if qs_type == QuerysetType.PROTEIN or qs_type == QuerysetType.ENTRY:
                queryset = queryset.filter(structures=level_name).distinct()
            elif qs_type == QuerysetType.STRUCTURE:
                queryset = queryset.filter(protein=level_name)
            else:
                queryset = queryset.filter(proteinentryfeature__protein=level_name)

            if queryset.count() == 0:
                raise ReferenceError("The chain {} doesn't exist in the structure {}".format(level_name, "pdb"))
            return queryset
        if "entries" in queryset:
            filter_entry_overview(queryset["entries"], level_name)
        if "proteins" in queryset:
            filter_protein_overview(queryset["proteins"], level_name)

        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if type(obj) != dict:
            if not isinstance(obj.serializer, StructureSerializer):
                arr = obj
                if isinstance(obj, dict):
                    arr = [obj]
                for o in arr:
                    if "structures" in o:
                        o["structures"] = \
                            [p for p in o["structures"] if
                             ("accession" in p and
                              p["accession"] == level_name) or
                             ("structure" in p and
                              "accession" in p["structure"] and
                              p["structure"]["accession"] == level_name)
                             ]
        return obj


class PDBHandler(CustomView):
    level_description = 'pdb level'
    child_handlers = [
        (r'([a-z]|[A-Z]|\d){4}', PDBAccessionHandler),
        # (r'.+', IDAccessionHandler),
    ]
    queryset = Structure.objects.all()
    serializer_class = StructureSerializer
    serializer_detail = SerializerDetail.STRUCTURE_HEADERS
    serializer_detail_filter = SerializerDetail.STRUCTURE_OVERVIEW

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        ds = endpoint_levels[level - 1].lower()
        self.queryset = self.queryset.filter(source_database__iexact=ds)

        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2]))
        return super(PDBHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        if not isinstance(queryset, dict):
            qs_type = get_queryset_type(queryset)
            if qs_type == QuerysetType.PROTEIN:
                general_handler.set_in_store(PDBHandler, "structure_queryset",
                                             queryset.values("structures").exclude(structures=None).distinct())
        else:
            if "entries" in queryset:
                filter_entry_overview(queryset["entries"])
            if "proteins" in queryset:
                filter_protein_overview(queryset["proteins"])

        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):

        try:
            if "structures" not in obj:
                obj["structures"] = general_handler.get_from_store(PDBHandler,
                                                                   "structure_queryset").count()
        finally:
            return obj


class StructureHandler(CustomView):
    level_description = 'section level'
    from_model = False
    child_handlers = [
        ("pdb", PDBHandler),
    ]
    to_add = None
    serializer_detail_filter = SerializerDetail.STRUCTURE_HEADERS

    @staticmethod
    def get_database_contributions(queryset, prefix=""):
        protein_counter = queryset.values(prefix+'source_database').annotate(total=Count(prefix+'source_database'))
        output = {}
        for row in protein_counter:
            output[row[prefix+"source_database"]] = row["total"]
        # output["uniprot"] = sum(output.values())
        return output

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}

        self.queryset = {"structures": StructureHandler.get_database_contributions(Structure.objects.all())}

        return super(StructureHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        qs = Structure.objects.all()
        if not isinstance(queryset, dict):
            qs_type = get_queryset_type(queryset)
            if qs_type == QuerysetType.PROTEIN:
                qs = Structure.objects.filter(accession__in=queryset.values('structures'))
            elif qs_type == QuerysetType.ENTRY:
                qs = Structure.objects.filter(accession__in=queryset.values('structures'))
        #     elif qs_type == QuerysetType.STRUCTURE_PROTEIN:
        #         qs = Protein.objects.filter(accession__in=queryset.values('protein'))
        general_handler.set_in_store(StructureHandler,
                                     "structure_count",
                                     StructureHandler.get_database_contributions(qs))
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj, list):
            try:
                obj["structures"] = general_handler.get_from_store(StructureHandler, "structure_count")
            finally:
                return obj
        return obj
