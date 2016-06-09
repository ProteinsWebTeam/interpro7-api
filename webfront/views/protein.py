from django.db.models import Count
from django.shortcuts import redirect

from webfront.constants import get_queryset_type, QuerysetType
from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.models import Protein, Entry, ProteinEntryFeature, ProteinStructureFeature
from webfront.views.entry import EntryHandler
from webfront.views.structure import StructureHandler

db_members = r'(uniprot)|(trembl)|(swissprot)'


class UniprotAccessionHandler(CustomView):
    level_description = 'uniprot accession level'
    serializer_class = ProteinSerializer
    queryset = Protein.objects
    many = False
    serializer_detail_filter = SerializerDetail.PROTEIN_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(accession=endpoint_levels[level - 1])
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2]))
        return super(UniprotAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        protein_db = general_handler.get_from_store(UniprotHandler, "protein_db")
        qs_type = get_queryset_type(queryset)
        if not isinstance(queryset, dict):
            if protein_db != "uniprot":
                if qs_type == QuerysetType.STRUCTURE_PROTEIN:
                    queryset = queryset.filter(protein=level_name, protein__source_database__iexact=protein_db)
                elif qs_type == QuerysetType.STRUCTURE:
                    queryset = queryset.filter(proteins=level_name, proteins__source_database__iexact=protein_db)
                else:
                    queryset = queryset.filter(proteinentryfeature__protein=level_name,
                                               proteinentryfeature__protein__source_database__iexact=protein_db)
            else:
                if qs_type == QuerysetType.STRUCTURE_PROTEIN:
                    queryset = queryset.filter(protein=level_name)
                elif qs_type == QuerysetType.STRUCTURE:
                    queryset = queryset.filter(proteins=level_name)
                else:
                    queryset = queryset.filter(proteinentryfeature__protein=level_name)
            if queryset.count() == 0:
                raise ReferenceError("The protein {} doesn't exist in the database {}".format(level_name, protein_db))
            return queryset
        elif "interpro" in queryset:
            matches = ProteinEntryFeature.objects.filter(protein=level_name)
            return EntryHandler.get_database_contributions(matches, 'entry__')
        elif "pdb" in queryset:
            matches = ProteinStructureFeature.objects.filter(protein=level_name)
            return StructureHandler.get_database_contributions(matches, 'structure__')

        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if type(obj) != dict:
            if not isinstance(obj.serializer, ProteinSerializer):
                arr = obj
                if isinstance(obj, dict):
                    arr = [obj]
                for o in arr:
                    if "proteins" in o:
                        for p in o["proteins"]:
                            if "accession" in p and p["accession"] != level_name:
                                o["proteins"].remove(p)
                            elif "protein" in p and p["protein"]["accession"] != level_name:
                                o["proteins"].remove(p)
        return obj


class IDAccessionHandler(UniprotAccessionHandler):
    level_description = 'uniprot id level'

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(identifier=endpoint_levels[level - 1])
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2]))
        new_url = request.get_full_path().replace(endpoint_levels[level - 1], self.queryset.first().accession)
        return redirect(new_url)


class UniprotHandler(CustomView):
    level_description = 'uniprot level'
    child_handlers = [
        (r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}', UniprotAccessionHandler),
        (r'.+', IDAccessionHandler),
    ]
    queryset = Protein.objects.all()
    serializer_class = ProteinSerializer
    serializer_detail = SerializerDetail.PROTEIN_HEADERS
    serializer_detail_filter = SerializerDetail.PROTEIN_OVERVIEW

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        ds = endpoint_levels[level - 1].lower()
        if ds != "uniprot":

            self.queryset = self.queryset.filter(source_database__iexact=ds)
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2]))
        return super(UniprotHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.set_in_store(UniprotHandler, "protein_db", level_name)
        if not isinstance(queryset, dict):
            qs_type = get_queryset_type(queryset)
            if level_name != "uniprot":
                if qs_type == QuerysetType.PROTEIN:
                    queryset = queryset.filter(proteinentryfeature__protein__source_database__iexact=level_name)
                elif qs_type == QuerysetType.STRUCTURE:
                    queryset = queryset.filter(proteins__source_database__iexact=level_name).distinct()
            if qs_type == QuerysetType.STRUCTURE_PROTEIN:
                general_handler.set_in_store(UniprotHandler,
                                             "protein_queryset",
                                             queryset.values("protein").all())
            else:
                general_handler.set_in_store(UniprotHandler,
                                             "protein_queryset",
                                             queryset.values("proteins").exclude(proteins=None).distinct())
        else:
            qs = Entry.objects.all()
            if level_name != "uniprot":
                qs = qs.filter(proteinentryfeature__protein__source_database__iexact=level_name)
            general_handler.set_in_store(UniprotHandler,
                                         "protein_queryset",
                                         qs.values("proteins").exclude(proteins=None).distinct())
        return queryset

    @staticmethod
    def remove_proteins(obj, protein_source):
        if "proteins" in obj:
            for p in obj["proteins"]:
                if "source_database"in p and p["source_database"] != protein_source:
                    obj["proteins"].remove(p)

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if hasattr(obj, 'serializer') and not isinstance(obj.serializer, ProteinSerializer):
            if level_name != "uniprot":
                if isinstance(obj, list):
                    for o in obj:
                        UniprotHandler.remove_proteins(o, level_name)
                else:
                    UniprotHandler.remove_proteins(obj, level_name)
        try:
            if "proteins" not in obj:
                obj["proteins"] = general_handler.get_from_store(UniprotHandler,
                                                                 "protein_queryset").count()
        finally:
            return obj


class ProteinHandler(CustomView):
    level_description = 'section level'
    from_model = False
    child_handlers = [
        (db_members, UniprotHandler),
    ]
    to_add = None
    serializer_detail_filter = SerializerDetail.ENTRY_PROTEIN_HEADERS

    @staticmethod
    def get_database_contributions(queryset):
        protein_counter = queryset.values('source_database').annotate(total=Count('source_database'))
        output = {}
        for row in protein_counter:
            output[row["source_database"]] = row["total"]

        output["uniprot"] = sum(output.values())
        return output

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}

        self.queryset = ProteinHandler.get_database_contributions(Protein.objects.all())

        return super(ProteinHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        qs = Protein.objects.all()
        if not isinstance(queryset, dict):
            qs_type = get_queryset_type(queryset)
            if qs_type == QuerysetType.ENTRY:
                qs = Protein.objects.filter(accession__in=queryset.values('proteins'))
            elif qs_type == QuerysetType.STRUCTURE:
                qs = Protein.objects.filter(accession__in=queryset.values('proteins'))
            elif qs_type == QuerysetType.STRUCTURE_PROTEIN:
                qs = Protein.objects.filter(accession__in=queryset.values('protein'))
        general_handler.set_in_store(ProteinHandler,
                                     "protein_count",
                                     ProteinHandler.get_database_contributions(qs))
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj, list):
            try:
                obj["proteins"] = general_handler.get_from_store(ProteinHandler, "protein_count")
            finally:
                return obj
        return obj
