from django.db.models import Count

from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.models import Protein

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
        if protein_db != "uniprot":
            queryset = queryset.filter(proteinentryfeature__protein=level_name,
                                       proteinentryfeature__protein__source_database__iexact=protein_db)
        else:
            queryset = queryset.filter(proteinentryfeature__protein=level_name)
        if queryset.count() == 0:
            raise ReferenceError("The protein {} doesn't exist in the database {}".format(level_name, protein_db))
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj.serializer, ProteinSerializer):
            for p in obj["proteins"]:
                if p["accession"] != level_name:
                    obj["proteins"].remove(p)
        return obj


class IDAccessionHandler(UniprotAccessionHandler):
    level_description = 'uniprot id level'

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if available_endpoint_handlers is None:
            available_endpoint_handlers = {}
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(identifier=endpoint_levels[level - 1])
        if self.queryset.count() == 0:
            raise Exception("The ID '{}' has not been found in {}".format(
                endpoint_levels[level - 1], endpoint_levels[level - 2]))
        endpoint_levels[level - 1] = self.queryset.first().accession
        return super(IDAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, *args, **kwargs
        )
    # TODO: Check this filter


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
        if level_name != "uniprot":
            queryset = queryset.filter(proteinentryfeature__protein__source_database__iexact=level_name)
        return queryset

    @staticmethod
    def remove_proteins(obj, protein_source):
        for p in obj["proteins"]:
            if p["source_database"] != protein_source:
                obj["proteins"].remove(p)

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj.serializer, ProteinSerializer):
            if level_name != "uniprot":
                if isinstance(obj, list):
                    for o in obj:
                        UniprotHandler.remove_proteins(o, level_name)
                else:
                    UniprotHandler.remove_proteins(obj, level_name)
        return obj


class ProteinHandler(CustomView):
    level_description = 'section level'
    from_model = False
    child_handlers = [
        (db_members, UniprotHandler),
    ]
    to_add = None

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

    # TODO: Check the filter option for endpoints combinations
    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        # TODO: Support for the case /api/entry/pfam/protein/ were the QS can have thousands of entries
        general_handler.set_in_store(ProteinHandler,
                                     "protein_count",
                                     ProteinHandler.get_database_contributions(
                                         Protein.objects.filter(accession__in=queryset.values('proteins'))))
        return queryset

    @staticmethod
    def post_serializer(obj, level_name="", general_handler=None):
        if not isinstance(obj, list):
            obj["proteins"] = general_handler.get_from_store(ProteinHandler,
                                                             "protein_count")
        return obj
