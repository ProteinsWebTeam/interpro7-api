from django.conf import settings
from webfront.models import Entry, EntryAnnotation
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
import webfront.serializers.uniprot
import webfront.serializers.pdb
import webfront.serializers.taxonomy
import webfront.serializers.collection
from webfront.views.queryset_manager import escape


class EntrySerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
        if self.queryset_manager.other_fields is not None:
            def counter_function():
                return EntrySerializer.get_counters(
                    instance,
                    self.searcher,
                    self.queryset_manager.get_searcher_query()
                )
            representation = self.add_other_fields(
                representation,
                instance,
                self.queryset_manager.other_fields,
                {"counters": counter_function}
            )
        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL or detail == SerializerDetail.ENTRY_DETAIL:
            sq = self.queryset_manager.get_searcher_query()
            representation["metadata"] = self.to_metadata_representation(instance, self.searcher, sq)
        elif detail == SerializerDetail.ENTRY_OVERVIEW:
            representation = self.to_counter_representation(instance, self.detail_filters)
        elif detail == SerializerDetail.ENTRY_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.GROUP_BY:
            representation = self.to_group_representation(instance)
        elif detail == SerializerDetail.IDA_LIST:
            representation = self.to_ida_list_representation(instance)
        else:
            representation = instance
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        if SerializerDetail.TAXONOMY_OVERVIEW in detail_filters:
            representation["taxa"] = self.to_taxonomy_count_representation(instance)
        if SerializerDetail.PROTEOME_OVERVIEW in detail_filters:
            representation["proteomes"] = self.to_proteome_count_representation(instance)
        if SerializerDetail.SET_OVERVIEW in detail_filters:
            representation["sets"] = self.to_set_count_representation(instance)

        if detail != SerializerDetail.ENTRY_OVERVIEW:
            sq = self.queryset_manager.get_searcher_query()
            if SerializerDetail.PROTEIN_DB in detail_filters or \
                    SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = EntrySerializer.to_proteins_detail_representation(
                    instance, self.searcher, "entry_acc:" + escape(instance.accession.lower()),
                    for_entry=True,
                    base_query=sq
                )
            if SerializerDetail.STRUCTURE_DB in detail_filters or \
                    SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = self.to_structures_detail_representation(
                    instance, self.searcher, "entry_acc:" + escape(instance.accession.lower()),
                    include_structure=SerializerDetail.STRUCTURE_DETAIL not in detail_filters,
                    base_query=sq
                )
            if SerializerDetail.TAXONOMY_DB in detail_filters or \
                    SerializerDetail.TAXONOMY_DETAIL in detail_filters:
                representation["taxa"] = self.to_taxonomy_detail_representation(
                    instance,
                    self.searcher,
                    "entry_acc:" + escape(instance.accession.lower())
                )
            if SerializerDetail.PROTEOME_DB in detail_filters or \
                    SerializerDetail.PROTEOME_DETAIL in detail_filters:
                representation["proteomes"] = self.to_proteomes_detail_representation(
                    self.searcher,
                    "entry_acc:" + escape(instance.accession.lower())
                )
            if SerializerDetail.SET_DB in detail_filters or \
                    SerializerDetail.SET_DETAIL in detail_filters:
                representation["sets"] = self.to_set_detail_representation(
                    instance,
                    self.searcher,
                    "entry_acc:" + escape(instance.accession.lower())
                )

        return representation

    @staticmethod
    def reformat_cross_references(cross_references):
        DEFAULT_DESCRIPTION = "Description of data source (to be defined in API)"
        DEFAULT_URL_PATTERN = "https://www.ebi.ac.uk/ebisearch/search.ebi?db=allebi&query={accession}"
        DEFAULT_RANK = 1000
        xrefSettings = settings.CROSS_REFERENCES

        reformattedCrossReferences = {}
        for database in cross_references.keys():
            accessions = cross_references[database]
            reformattedCrossReferences[database] = {
                "displayName": database,
                "description": DEFAULT_DESCRIPTION,
                "rank": DEFAULT_RANK,
                "accessions": []
            }

            if database in xrefSettings:
                if 'displayName' in xrefSettings[database]:
                    reformattedCrossReferences[database]['displayName'] = xrefSettings[database]['displayName']
                if 'description' in xrefSettings[database]:
                    reformattedCrossReferences[database]['description'] = xrefSettings[database]['description']
                if 'rank' in xrefSettings[database]:
                    reformattedCrossReferences[database]['rank'] = xrefSettings[database]['rank']

            for accession in accessions:
                accessionObj = {
                    'accession': accession,
                    'url': DEFAULT_URL_PATTERN
                }

                if database in xrefSettings and 'urlPattern' in xrefSettings[database]:
                    accessionObj['url'] = xrefSettings[database]['urlPattern']

                accessionObj['url'] = accessionObj['url'].replace('{accession}', accession)
                reformattedCrossReferences[database]['accessions'].append(accessionObj)
        return reformattedCrossReferences

    @staticmethod
    def to_metadata_representation(instance, searcher, sq):
        # recategorise_go_terms(instance.go_terms)
        results = EntryAnnotation.objects.filter(accession=instance.accession).only("type")
        # annotation_types = map(lambda x: x.type, results)
        annotation_types = [x.type for x in results]
        obj = {
            "accession": instance.accession,
            "entry_id": instance.entry_id,
            "type": instance.type,
            "go_terms": instance.go_terms,
            "source_database": instance.source_database,
            "member_databases": instance.member_databases,
            "integrated": instance.integrated.accession if instance.integrated else None,
            "hierarchy": instance.hierarchy,
            "name": {
                "name": instance.name,
                "short": instance.short_name,
                # "other": instance.other_names,
            },
            "description": instance.description,
            "wikipedia": instance.wikipedia,
            "literature": instance.literature,
            "counters": EntrySerializer.get_counters(instance, searcher, sq),
            "entry_annotations": annotation_types,
            "cross_references": EntrySerializer.reformat_cross_references(instance.cross_references)
        }
        return obj

    @staticmethod
    def get_counters(instance, searcher, sq):
        return {
            "proteins": searcher.get_number_of_field_by_endpoint("entry", "protein_acc", instance.accession, sq),
            "structures": searcher.get_number_of_field_by_endpoint("entry", "structure_acc", instance.accession, sq),
            "taxa": searcher.get_number_of_field_by_endpoint("entry", "tax_id", instance.accession, sq),
            "proteomes": searcher.get_number_of_field_by_endpoint("entry", "proteome_acc", instance.accession, sq),
            "sets": searcher.get_number_of_field_by_endpoint("entry", "set_acc", instance.accession, sq),
            "domain_architectures": searcher.get_number_of_field_by_endpoint("entry", "ida_id", instance.accession, sq),
        }

    def to_headers_representation(self, instance):
        headers = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name if instance.name else instance.short_name,
                "source_database": instance.source_database,
                "type": instance.type,
                "integrated": instance.integrated.accession if instance.integrated else None,
                "member_databases": instance.member_databases,
                "go_terms": instance.go_terms,
            }
        }
        return headers

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if EntrySerializer.grouper_is_empty(instance):
                raise ReferenceError('There are not entries for this request')
            return {
                        EntrySerializer.get_key_from_bucket(bucket): EntrySerializer.serialize_counter_bucket(bucket, "entries")
                        for bucket in instance["groups"]["buckets"]
                    }
        else:
            return {field_value: total for field_value, total in instance}

    @staticmethod
    def to_counter_representation(instance, filters=None):
        if filters is None:
            filters = []
        if "entries" not in instance:
            if EntrySerializer.counter_is_empty(instance):
                raise ReferenceError('There are not entries for this request')
            result = {
                "entries": {
                    "member_databases": {
                        EntrySerializer.get_key_from_bucket(bucket): EntrySerializer.serialize_counter_bucket(bucket, "entries")
                        for bucket in instance["databases"]["buckets"]
                    },
                    "integrated": 0,
                    "unintegrated": 0,
                    "interpro": 0,
                    "all": 0,
                }
            }
            if SerializerDetail.PROTEIN_DB in filters or\
                    SerializerDetail.STRUCTURE_DB in filters or\
                    SerializerDetail.SET_DB in filters or\
                    SerializerDetail.TAXONOMY_DB in filters or\
                    SerializerDetail.PROTEOME_DB in filters:
                result["entries"]["integrated"] = {"entries": 0}
                result["entries"]["unintegrated"] = {"entries": 0}
                result["entries"]["interpro"] = {"entries": 0}
                result["entries"]["all"] = {"entries": 0}

            if SerializerDetail.PROTEIN_DB in filters:
                result["entries"]["integrated"]["proteins"] = 0
                result["entries"]["unintegrated"]["proteins"] = 0
                result["entries"]["interpro"]["proteins"] = 0
                result["entries"]["all"]["proteins"] = 0
            if SerializerDetail.STRUCTURE_DB in filters:
                result["entries"]["integrated"]["structures"] = 0
                result["entries"]["unintegrated"]["structures"] = 0
                result["entries"]["interpro"]["structures"] = 0
                result["entries"]["all"]["structures"] = 0
            if SerializerDetail.TAXONOMY_DB in filters:
                result["entries"]["integrated"]["taxa"] = 0
                result["entries"]["unintegrated"]["taxa"] = 0
                result["entries"]["interpro"]["taxa"] = 0
                result["entries"]["all"]["taxa"] = 0
            if SerializerDetail.PROTEOME_DB in filters:
                result["entries"]["integrated"]["proteomes"] = 0
                result["entries"]["unintegrated"]["proteomes"] = 0
                result["entries"]["interpro"]["proteomes"] = 0
                result["entries"]["all"]["proteomes"] = 0
            if SerializerDetail.SET_DB in filters:
                result["entries"]["integrated"]["sets"] = 0
                result["entries"]["unintegrated"]["sets"] = 0
                result["entries"]["interpro"]["sets"] = 0
                result["entries"]["all"]["sets"] = 0

            if "unintegrated" in instance and (
                    ("count" in instance["unintegrated"] and instance["unintegrated"]["count"]) or
                    ("doc_count" in instance["unintegrated"] and instance["unintegrated"]["doc_count"]) > 0):
                result["entries"]["unintegrated"] = EntrySerializer.serialize_counter_bucket(instance["unintegrated"], "entries")
            if "all" in instance and (
                    ("count" in instance["all"] and instance["all"]["count"]) or
                    ("doc_count" in instance["all"] and instance["all"]["doc_count"]) > 0):
                result["entries"]["all"] = EntrySerializer.serialize_counter_bucket(instance["all"], "entries")
            if "integrated" in instance and (
                    ("count" in instance["integrated"] and instance["integrated"]["count"]) or
                    ("doc_count" in instance["integrated"] and instance["integrated"]["doc_count"]) > 0):
                result["entries"]["integrated"] = EntrySerializer.serialize_counter_bucket(instance["integrated"], "entries")
            if "interpro" in result["entries"]["member_databases"]:
                result["entries"]["interpro"] = result["entries"]["member_databases"]["interpro"]
                del result["entries"]["member_databases"]["interpro"]
            # vals = list(result["entries"]["member_databases"].values())
            # if len(vals) > 0:
            #     unintegrated = result["entries"]["unintegrated"]
            #     if type(unintegrated) != int and "entries" in unintegrated:
            #         unintegrated = unintegrated["entries"]
            #
            #     if type(vals[0]) == int:
            #         result["entries"]["integrated"] = sum(vals) - unintegrated
            #     else:
            #         result["entries"]["integrated"] = {
            #             "entries": sum([v["entries"] for v in vals]) - unintegrated
            #         }
            #         if "proteins" in result["entries"]["interpro"]:
            #             result["entries"]["integrated"]["proteins"] = result["entries"]["interpro"]["proteins"]
            #         if "structures" in result["entries"]["interpro"]:
            #             result["entries"]["integrated"]["structures"] = result["entries"]["interpro"]["structures"]
            #         if "organisms" in result["entries"]["interpro"]:
            #             result["entries"]["integrated"]["organisms"] = result["entries"]["interpro"]["organisms"]
            #         if "sets" in result["entries"]["interpro"]:
            #             result["entries"]["integrated"]["sets"] = result["entries"]["interpro"]["sets"]

            return result
        return instance

    dbcode = {
        "H": "Pfam",
        "M": "profile",
        "R": "SMART",
        "V": "PHANTER",
        "g": "MobiDB",
        "B": "SFLD",
        "P": "prosite",
        "X": "GENE 3D",
        "N": "TIGRFAMs",
        "J": "CDD",
        "Y": "SUPERFAMILY",
        "U": "PIRSF",
        "D": "ProDom",
        "Q": "HAMAP",
        "F": "Prints",
    }

    @staticmethod
    def get_key_from_bucket(bucket):
        key = str(bucket["val"] if "val" in bucket else bucket["key"])
        if key.upper() in EntrySerializer.dbcode:
            return EntrySerializer.dbcode[key.upper()].lower()
        return key

    @staticmethod
    def counter_is_empty(instance):
        return EntrySerializer.grouper_is_empty(instance, "databases")

    @staticmethod
    def grouper_is_empty(instance, field="groups"):
        if ("count" in instance and instance["count"] == 0) or \
           (len(instance[field]["buckets"]) == 0 and instance["unintegrated"]["unique"] == 0):
            return True
        if ("doc_count" in instance[field] and instance[field]["doc_count"] == 0) or \
           (len(instance[field]["buckets"]) == 0 and instance["unintegrated"]["unique"]["value"] == 0):
            return True
        return False

    def to_proteins_count_representation(self, instance):
        query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.searcher.get_counter_object("protein", query, self.get_extra_endpoints_to_count())
        )["proteins"]

    def to_structures_count_representation(self, instance):
        query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object("structure", query, self.get_extra_endpoints_to_count())
        )["structures"]

    def to_taxonomy_count_representation(self, instance):
        query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.taxonomy.TaxonomySerializer.to_counter_representation(
            self.searcher.get_counter_object("taxonomy", query, self.get_extra_endpoints_to_count())
        )["taxa"]

    def to_proteome_count_representation(self, instance):
        query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.proteome.ProteomeSerializer.to_counter_representation(
            self.searcher.get_counter_object("proteome", query, self.get_extra_endpoints_to_count())
        )["proteomes"]

    def to_set_count_representation(self, instance):
        query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.collection.SetSerializer.to_counter_representation(
            self.searcher.get_counter_object("set", query, self.get_extra_endpoints_to_count())
        )["sets"]

    @staticmethod
    def get_entry_header_from_search_object(obj, for_structure=False, include_entry=False, searcher=None, sq=None):
        header = {
            "accession": obj["entry_acc"],
            "entry_protein_locations": obj["entry_protein_locations"],
            "protein_length": obj["protein_length"],
            "source_database": obj["entry_db"],
            "entry_type": obj["entry_type"],
            "entry_integrated": obj["entry_integrated"],
        }
        if for_structure:
            header["chain"] = obj["structure_chain_acc"]
            header["protein"] = obj["protein_acc"]
            header["protein_structure_locations"] = obj["protein_structure_locations"]
        if include_entry:
            header["entry"] = EntrySerializer.to_metadata_representation(
                Entry.objects.get(accession=obj["entry_acc"].upper()), searcher, sq
            )

        return header

    @staticmethod
    def to_ida_list_representation(obj):
        # return obj
        return {
            "count": obj["ngroups"]["value"],
            "results": [
                {"ida": o["ida"], "ida_id": o["ida_id"], "unique_proteins": o["unique"]["value"]}
                for o in obj['groups']
            ]
        }

    class Meta:
        model = Entry
