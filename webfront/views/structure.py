from django.db.models import Count
from webfront.models import Structure
from webfront.serializers.pdb import StructureSerializer
from webfront.views.custom import CustomView, SerializerDetail
from django.db.models import F


def filter_structure_overview(obj, general_handler, endpoint):
    for str_db in obj:
        qm = general_handler.queryset_manager.clone()
        qm.add_filter("structure", source_database__iexact=str_db)
        if not isinstance(obj[str_db], dict):
            obj[str_db] = {"structures": obj[str_db]}
        obj[str_db][general_handler.plurals[endpoint]] = qm.get_queryset(endpoint)\
            .values("accession").distinct().count()
    return obj


class ChainPDBAccessionHandler(CustomView):
    level_description = 'structure chain level'
    serializer_class = StructureSerializer
    queryset = Structure.objects
    many = False
    serializer_detail = SerializerDetail.STRUCTURE_CHAIN
    serializer_detail_filter = SerializerDetail.STRUCTURE_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("solr",
                                                    chain=endpoint_levels[level - 1])
        return super(ChainPDBAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    # @staticmethod
    # def filter(queryset, level_name="", general_handler=None):
    #     if not isinstance(queryset, dict):
    #         general_handler.queryset_manager.add_filter("structure",
    #                                                     proteinstructurefeature__chain=level_name,
    #                                                     entrystructurefeature__chain=level_name,
    #                                                     proteinstructurefeature__protein_id=F('protein__accession'))
    #     return queryset
    #
    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
    #         from webfront.views.entry import filter_entry_overview
    #         from webfront.views.protein import filter_protein_overview
    #         if "entries" in obj:
    #             obj["entries"] = filter_entry_overview(obj["entries"], general_handler, "structure")
    #         if "proteins" in obj:
    #             obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "structure")
    #     else:
    #             pdb = general_handler.get_from_store(PDBAccessionHandler, "pdb_accession")
    #             arr = obj
    #             remove_empty_structures = False
    #             if isinstance(obj, dict):
    #                 arr = [obj]
    #             for o in arr:
    #                 if "structures" in o:
    #                     o["structures"] = \
    #                         [p for p in o["structures"] if
    #                          ("chain" in p and
    #                           p["chain"] == level_name and
    #                           p["structure"]["accession"] == pdb) or
    #                          ("structure" in p and
    #                           "chain" in p["structure"] and
    #                           p["structure"]["chain"] == level_name and
    #                           p["structure"]["accession"] == pdb)
    #                          ]
    #                     if len(o["structures"]) == 0:
    #                         remove_empty_structures = True
    #
    #                 if "entries" in o and isinstance(o["entries"], list) and \
    #                         len(o["entries"]) > 0 and "chain" in o["entries"][0]:
    #                     o["entries"] = \
    #                         [p for p in o["entries"] if
    #                          ("chain" in p and
    #                           p["chain"] == level_name) or
    #                          ("structure" in p and
    #                           "chain" in p["structure"] and
    #                           p["entry"]["chain"] == level_name)
    #                          ]
    #                     if len(o["entries"]) == 0:
    #                         raise ReferenceError("The chain {} doesn't exist in the selected structure"
    #                                              .format(level_name))
    #                 if "proteins" in o and isinstance(o["proteins"], list) and \
    #                         len(o["proteins"]) > 0 and "chain" in o["proteins"][0]:
    #                     o["proteins"] = \
    #                         [p for p in o["proteins"] if
    #                          ("chain" in p and
    #                           p["chain"] == level_name) or
    #                          ("structure" in p and
    #                           "chain" in p["structure"] and
    #                           p["entry"]["chain"] == level_name)
    #                          ]
    #                     if len(o["proteins"]) == 0:
    #                         raise ReferenceError("The chain {} doesn't exist in the selected structure"
    #                                              .format(level_name))
    #                 if "metadata"in o and "chains" in o["metadata"] and isinstance(o["metadata"]["chains"], dict):
    #                     o["metadata"]["chains"] = \
    #                         {p: o["metadata"]["chains"][p] for p in o["metadata"]["chains"] if
    #                          (level_name in p)
    #                          }
    #             if remove_empty_structures:
    #                 arr = [a for a in arr if len(a["structures"]) > 0]
    #                 if len(arr) == 0:
    #                     raise ReferenceError("The chain {} doesn't exist in the selected structure".format(level_name))
    #                 return arr
    #     return obj


class PDBAccessionHandler(CustomView):
    level_description = 'pdb accession level'
    serializer_class = StructureSerializer
    queryset = Structure.objects
    many = False
    child_handlers = [
        (r'[a-zA-Z\d]{1,4}', ChainPDBAccessionHandler),
    ]
    serializer_detail_filter = SerializerDetail.STRUCTURE_DETAIL

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.add_filter("structure", accession__iexact=endpoint_levels[level - 1])
        general_handler.set_in_store(PDBAccessionHandler, "pdb_accession", endpoint_levels[level - 1])
        return super(PDBAccessionHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    # @staticmethod
    # def filter(queryset, level_name="", general_handler=None):
    #     general_handler.set_in_store(PDBAccessionHandler, "pdb_accession", level_name)
    #     if not isinstance(queryset, dict):
    #         general_handler.queryset_manager.add_filter("structure", accession__iexact=level_name)
    #     return queryset
    #
    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
    #         from webfront.views.entry import filter_entry_overview
    #         from webfront.views.protein import filter_protein_overview
    #         if "entries" in obj:
    #             obj["entries"] = filter_entry_overview(obj["entries"], general_handler, "structure")
    #         if "proteins" in obj:
    #             obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "structure")
    #     else:
    #         if not isinstance(obj.serializer, StructureSerializer):
    #             arr = obj
    #             if isinstance(obj, dict):
    #                 arr = [obj]
    #             for o in arr:
    #                 if "structures" in o:
    #                     o["structures"] = \
    #                         [p for p in o["structures"] if
    #                          ("accession" in p and
    #                           p["accession"] == level_name) or
    #                          ("structure" in p and
    #                           "accession" in p["structure"] and
    #                           p["structure"]["accession"] == level_name)
    #                          ]
    #     return obj


class PDBHandler(CustomView):
    level_description = 'pdb level'
    child_handlers = [
        (r'[a-zA-Z\d]{4}', PDBAccessionHandler),
        # (r'.+', IDAccessionHandler),
    ]
    queryset = Structure.objects.all()
    serializer_class = StructureSerializer
    serializer_detail = SerializerDetail.STRUCTURE_HEADERS
    serializer_detail_filter = SerializerDetail.STRUCTURE_DB

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        ds = endpoint_levels[level - 1].lower()
        general_handler.queryset_manager.add_filter("structure", source_database__iexact=ds)
        return super(PDBHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("structure", source_database__iexact=level_name)
        return queryset
    #
    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     if isinstance(obj, dict) and not hasattr(obj, 'serializer'):
    #         from webfront.views.entry import filter_entry_overview
    #         from webfront.views.protein import filter_protein_overview
    #         if "entries" in obj:
    #             obj["entries"] = filter_entry_overview(obj["entries"], general_handler, "structure")
    #         if "proteins" in obj:
    #             obj["proteins"] = filter_protein_overview(obj["proteins"], general_handler, "structure")
    #         return obj
    #
    #     try:
    #         structures = [x[0]
    #                       for x in general_handler.queryset_manager.get_queryset("structure")
    #                       .values_list("accession").distinct()]
    #
    #         arr = [obj] if isinstance(obj, dict) else obj
    #         for result in arr:
    #             result["structures"] = [x for x in result["structures"] if x["accession"] in structures]
    #     finally:
    #         return obj


class StructureHandler(CustomView):
    level_description = 'section level'
    from_model = False
    child_handlers = [
        ("pdb", PDBHandler),
    ]
    to_add = None
    many = False
    serializer_class = StructureSerializer
    serializer_detail = SerializerDetail.STRUCTURE_OVERVIEW
    serializer_detail_filter = SerializerDetail.STRUCTURE_OVERVIEW

    @staticmethod
    def get_database_contributions(queryset):
        qs = Structure.objects.filter(accession__in=queryset)
        protein_counter = qs.values_list('source_database').annotate(total=Count('source_database'))
        output = {"pdb": 0}
        for (source_database, total) in protein_counter:
            output[source_database] = total
        return {"structures": output}

    def get(self, request, endpoint_levels, available_endpoint_handlers=None, level=0,
            parent_queryset=None, handler=None, general_handler=None, *args, **kwargs):
        general_handler.queryset_manager.reset_filters("structure", endpoint_levels)
        general_handler.queryset_manager.add_filter("structure", accession__isnull=False)
        return super(StructureHandler, self).get(
            request, endpoint_levels, available_endpoint_handlers, level,
            self.queryset, handler, general_handler, *args, **kwargs
        )

    @staticmethod
    def filter(queryset, level_name="", general_handler=None):
        general_handler.queryset_manager.add_filter("structure", accession__isnull=False)
        return queryset
    #
    # @staticmethod
    # def post_serializer(obj, level_name="", general_handler=None):
    #     if general_handler.queryset_manager.main_endpoint != "structure":
    #         if isinstance(obj, dict):
    #             qs = general_handler.queryset_manager.get_queryset("structure")
    #             obj["structures"] = StructureHandler.get_database_contributions(qs)
    #         elif isinstance(obj, list):
    #             pc = general_handler.queryset_manager.group_and_count("structure")
    #             for item in obj:
    #                 item["structures"] = pc[item["metadata"]["accession"]]
    #     else:
    #         obj = {"structures": obj}
    #     return obj
