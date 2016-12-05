from django.db.models import Count
from django.shortcuts import redirect

from webfront.serializers.uniprot import ProteinSerializer
from webfront.views.custom import CustomView, SerializerDetail
from webfront.models import Protein
from django.conf import settings


entry_db_members = '|'.join(settings.DB_MEMBERS)

db_members = r'(uniprot)|(trembl)|(swissprot)'


def filter_protein_overview(obj, general_handler, endpoint):
    for prot_db in obj:
        qm = general_handler.queryset_manager.clone()
        if prot_db != "uniprot":
            qm.add_filter("protein", source_database__iexact=prot_db)
        if not isinstance(obj[prot_db], dict):
            obj[prot_db] = {"proteins": obj[prot_db]}
        obj[prot_db][general_handler.plurals[endpoint]] = qm.get_queryset(endpoint).values("accession").distinct().count()
    return obj


class UniprotAccessionHandler(CustomView):
    level_description = 'uniprot accession level'
    serializer_class = ProteinSerializer
    queryset = Protein.objects
    many = False
    serializer_detail_filter = SerializerDetail.PROTEIN_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("protein", accession=endpoint_levels[level - 1])
        return super(UniprotAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    # @staticmethod
    # def filter(queryset, level_name="", general_handler=None):
    #     if not isinstance(queryset, dict):
    #         general_handler.queryset_manager.add_filter("protein", accession=level_name)
    #         return queryset
    #     return queryset
    #
    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
    #         from webfront.views.entry import filter_entry_overview
    #         from webfront.views.structure import filter_structure_overview
    #         if "entries" in obj:
    #             obj["entries"] = filter_entry_overview(obj["entries"], general_handler, "protein")
    #         if "structures" in obj:
    #             obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "protein")
    #     else:
    #         if not isinstance(obj.serializer, ProteinSerializer):
    #             prots = [x[0]
    #                      for x in general_handler.queryset_manager.get_queryset("protein")
    #                      .values_list("accession").distinct()]
    #             remove_empty_structures = False
    #             arr = [obj] if isinstance(obj, dict) else obj
    #             for o in arr:
    #                 if "proteins" in o:
    #                     o["proteins"] = [p for p in o["proteins"]
    #                                      if level_name in prots and(
    #                                          (("accession" in p and p["accession"] == level_name) or
    #                                           ("protein" in p and p["protein"]["accession"] == level_name)))]
    #                     if len(o["proteins"]) == 0:
    #                         remove_empty_structures = True
    #             if remove_empty_structures:
    #                 arr = [a for a in arr if len(a["proteins"]) > 0]
    #                 if len(arr) == 0:
    #                     raise ReferenceError("The entry {} doesn't exist in the selected url".format(level_name))
    #     return obj


class IDAccessionHandler(UniprotAccessionHandler):
    level_description = 'uniprot id level'

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, *args, **kwargs):
        if parent_queryset is not None:
            self.queryset = parent_queryset
        self.queryset = self.queryset.filter(identifier=endpoint_levels[level - 1])
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
    serializer_detail_filter = SerializerDetail.PROTEIN_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        ds = endpoint_levels[level - 1].lower()
        if ds != "uniprot":
            general_handler.queryset_manager.add_filter("protein", source_database__iexact=ds)
        return super(UniprotHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        if level_name != "uniprot":
            general_handler.queryset_manager.add_filter("protein", source_database__iexact=level_name)
        else:
            general_handler.queryset_manager.add_filter("protein", source_database__isnull=False)
        return queryset

    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
    #         from webfront.views.entry import filter_entry_overview
    #         from webfront.views.structure import filter_structure_overview
    #         if "entries" in obj:
    #             obj["entries"] = filter_entry_overview(obj["entries"], general_handler, "protein")
    #         if "structures" in obj:
    #             obj["structures"] = filter_structure_overview(obj["structures"], general_handler, "protein")
    #         return obj
    #     prots = [x[0]
    #              for x in general_handler.queryset_manager.get_queryset("protein")
    #              .values_list("accession").distinct()]
    #     if hasattr(obj, 'serializer') and not isinstance(obj.serializer, ProteinSerializer):
    #         remove_empty_structures = False
    #         arr = obj if isinstance(obj, list) else [obj]
    #         for o in arr:
    #             if "proteins" in o:
    #                 o["proteins"] = [p
    #                                  for p in o["proteins"]
    #                                  if (level_name == "uniprot" or
    #                                      ("source_database"in p and p["source_database"] == level_name)) and
    #                                  (prots is None or p["accession"] in prots)]
    #                 if len(o["proteins"]) == 0:
    #                     remove_empty_structures = True
    #         if remove_empty_structures:
    #             arr = [a for a in arr if len(a["proteins"]) > 0]
    #             if len(arr) == 0:
    #                 raise ReferenceError("There are not proteins fo the database {} with the selected filters"
    #                                      .format(level_name))
    #     return obj


class ProteinHandler(CustomView):
    serializer_class = ProteinSerializer
    many = False
    serializer_detail = SerializerDetail.PROTEIN_OVERVIEW
    level_description = 'section level'
    from_model = False
    child_handlers = [
        (db_members, UniprotHandler),
    ]
    to_add = None
    serializer_detail_filter = SerializerDetail.PROTEIN_OVERVIEW

    @staticmethod
    def get_database_contributions(queryset):
        qs = Protein.objects.filter(accession__in=queryset)
        protein_counter = qs.values_list('source_database').annotate(total=Count('source_database'))
        output = {}
        for (source_database, total) in protein_counter:
            output[source_database] = total

        output["uniprot"] = sum(output.values())
        return {"proteins": output}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):

        general_handler.queryset_manager.reset_filters("protein", endpoint_levels)
        general_handler.queryset_manager.add_filter("protein", accession__isnull=False)

        return super(ProteinHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("protein", accession__isnull=False)
        return queryset

    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     endpoint = general_handler.queryset_manager.main_endpoint
    #     if endpoint != "protein":
    #         if isinstance(obj, dict):
    #             qs = general_handler.queryset_manager.get_queryset("protein")
    #             obj["proteins"] = ProteinHandler.get_database_contributions(qs)
    #         elif isinstance(obj, list):
    #             pc = general_handler.queryset_manager.group_and_count("protein")
    #             for item in obj:
    #                 item["proteins"] = pc[item["metadata"]["accession"]]
    #     else:
    #         obj = {"proteins": obj}
    #     return obj
