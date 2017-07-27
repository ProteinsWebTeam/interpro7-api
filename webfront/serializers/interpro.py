from django.conf import settings
from webfront.models import Entry
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
import webfront.serializers.uniprot
import webfront.serializers.pdb
import webfront.serializers.taxonomy
from webfront.serializers.utils import recategorise_go_terms
from webfront.views.queryset_manager import escape

class EntrySerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}

        representation = self.endpoint_representation(representation, instance, self.detail)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)

        return representation

    def endpoint_representation(self, representation, instance, detail):
        if detail == SerializerDetail.ALL or detail == SerializerDetail.ENTRY_DETAIL:
            representation["metadata"] = self.to_metadata_representation(instance, self.searcher)
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
        if SerializerDetail.ORGANISM_OVERVIEW in detail_filters:
            representation["organisms"] = self.to_organism_count_representation(instance)

        if detail != SerializerDetail.ENTRY_OVERVIEW:
            if SerializerDetail.PROTEIN_DB in detail_filters:
                representation["proteins"] = EntrySerializer.to_proteins_detail_representation(instance, self.searcher)
            if SerializerDetail.STRUCTURE_DB in detail_filters:
                representation["structures"] = EntrySerializer.to_structures_detail_representation(instance, self.searcher)
            if SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = EntrySerializer.to_proteins_detail_representation(instance, self.searcher)
            if SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = EntrySerializer.to_structures_detail_representation(instance, self.searcher)

        return representation

    @staticmethod
    def reformat_cross_references(cross_references):
        DEFAULT_DESCRIPTION = "Description of data source (to be defined in API)"
        DEFAULT_URL_PATTERN = "https://www.ebi.ac.uk/ebisearch/search.ebi?db=allebi&query={accession}"
        #fetches values from interpro.yml
        xrefSettings = settings.CROSS_REFERENCES

        reformattedCrossReferences = {}
        for database in cross_references.keys():
            accessions = cross_references[database]
            reformattedCrossReferences[database] = {}

            if database in xrefSettings and 'displayName' in xrefSettings[database]:
                reformattedCrossReferences[database]['displayName'] =  xrefSettings[database]['displayName']
            else:
                reformattedCrossReferences[database]['displayName'] = database

            if database in xrefSettings and 'description' in xrefSettings[database]:
                reformattedCrossReferences[database]['description'] =  xrefSettings[database]['description']
            else:
                reformattedCrossReferences[database]['description'] = DEFAULT_DESCRIPTION

            reformattedCrossReferences[database]['rank'] =  xrefSettings[database]['rank']

            reformattedCrossReferences[database]['accessions'] = []
            for accession in accessions:
                accessionObj = {}
                accessionObj['accession'] = accession

                if database in xrefSettings and 'urlPattern' in xrefSettings[database]:
                    accessionObj['url'] =  xrefSettings[database]['urlPattern']
                else:
                    accessionObj['url'] = DEFAULT_URL_PATTERN
                accessionObj['url'] = accessionObj['url'].replace('{accession}', accession)
                reformattedCrossReferences[database]['accessions'].append(accessionObj)
        return reformattedCrossReferences

    @staticmethod
    def to_metadata_representation(instance, solr):
        recategorise_go_terms(instance.go_terms)
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
                "other": instance.other_names,
            },
            "description": instance.description,
            "wikipedia": instance.wikipedia,
            "literature": instance.literature,
            "counters": {
                "proteins": solr.get_number_of_field_by_endpoint("entry", "protein_acc", instance.accession),
                "structures": solr.get_number_of_field_by_endpoint("entry", "structure_acc", instance.accession)
            },
            "cross_references": EntrySerializer.reformat_cross_references(instance.cross_references)
        }
        return obj

    @staticmethod
    def to_proteins_detail_representation(instance, solr, is_full=False):
        solr_query = "entry_acc:" + escape(instance.accession.lower())
        response = [
            webfront.serializers.uniprot.ProteinSerializer.get_protein_header_from_search_object(
                r,
                include_protein=is_full,
                solr=solr
            )
            for r in solr.get_group_obj_of_field_by_query(None, "protein_acc", fq=solr_query, rows=10)["groups"]
        ]
        if len(response) == 0:
            raise ReferenceError('There are not proteins for this request')
        return response

    @staticmethod
    def to_structures_detail_representation(instance, solr, is_full=False):
        solr_query = "entry_acc:" + escape(instance.accession.lower())
        response = [
            webfront.serializers.pdb.StructureSerializer.get_structure_from_search_object(
                r,
                include_structure=is_full,
                search=solr
            )
            for r in solr.execute_query(None, fq=solr_query, rows=10)
        ]
        if len(response) == 0:
            raise ReferenceError('There are not structures for this request')
        return response

    def to_headers_representation(self, instance):
        headers = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "source_database": instance.source_database,
                "type": instance.type,
                "integrated": instance.integrated.accession if instance.integrated else None,
                "member_databases": instance.member_databases,
                "go_terms": instance.go_terms,
            }
        }
        return headers

    @staticmethod
    def serialize_counter_bucket(bucket):
        output = bucket["unique"]
        is_solr = True
        if isinstance(output, dict):
            output = output["value"]
            is_solr = False
        if "protein" in bucket or "structure" in bucket:
            output = {"entries": output}
            if "protein" in bucket:
                output["proteins"] = bucket["protein"] if is_solr else bucket["protein"]["value"]
            if "structure" in bucket:
                output["structures"] = bucket["structure"] if is_solr else bucket["structure"]["value"]
        return output

    @staticmethod
    def to_group_representation(instance):
        if "groups" in instance:
            if EntrySerializer.grouper_is_empty(instance):
                raise ReferenceError('There are not entries for this request')
            return {
                        EntrySerializer.get_key_from_bucket(bucket): EntrySerializer.serialize_counter_bucket(bucket)
                        for bucket in instance["groups"]["buckets"]
                    }
        else:
            return {field_value: total for field_value, total in instance}

    @staticmethod
    def to_counter_representation(instance, filters=[]):
        if "entries" not in instance:
            if EntrySerializer.counter_is_empty(instance):
                raise ReferenceError('There are not entries for this request')
            result = {
                "entries": {
                    "member_databases": {
                        EntrySerializer.get_key_from_bucket(bucket): EntrySerializer.serialize_counter_bucket(bucket)
                        for bucket in instance["databases"]["buckets"]
                    },
                    "integrated": 0,
                    "unintegrated": 0,
                    "interpro": 0,
                }
            }
            if SerializerDetail.PROTEIN_DB in filters or SerializerDetail.STRUCTURE_DB in filters :
                result["entries"]["integrated"] = {"entries": 0}
                result["entries"]["unintegrated"] = {"entries": 0}
                result["entries"]["interpro"] = {"entries": 0}
            if SerializerDetail.PROTEIN_DB in filters:
                result["entries"]["integrated"]["proteins"] = 0
                result["entries"]["unintegrated"]["proteins"] = 0
                result["entries"]["interpro"]["proteins"] = 0
            if SerializerDetail.STRUCTURE_DB in filters:
                result["entries"]["integrated"]["structures"] = 0
                result["entries"]["unintegrated"]["structures"] = 0
                result["entries"]["interpro"]["structures"] = 0

            if "unintegrated" in instance and (
                    ("count" in instance["unintegrated"] and instance["unintegrated"]["count"]) or
                    ("doc_count" in instance["unintegrated"] and instance["unintegrated"]["doc_count"]) > 0):
                result["entries"]["unintegrated"] = EntrySerializer.serialize_counter_bucket(instance["unintegrated"])
            if "interpro" in result["entries"]["member_databases"]:
                result["entries"]["interpro"] = result["entries"]["member_databases"]["interpro"]
                del result["entries"]["member_databases"]["interpro"]
            vals = list(result["entries"]["member_databases"].values())
            if len(vals) > 0:
                if type(vals[0]) == int:
                    result["entries"]["integrated"] = sum(vals) - result["entries"]["unintegrated"]
                else:
                    result["entries"]["integrated"] = {
                        "entries": sum([v["entries"] for v in vals]) - result["entries"]["unintegrated"]["entries"]
                    }
                    if "proteins" in result["entries"]["interpro"]:
                        result["entries"]["integrated"]["proteins"] = result["entries"]["interpro"]["proteins"]
                    if "structures" in result["entries"]["interpro"]:
                        result["entries"]["integrated"]["structures"] = result["entries"]["interpro"]["structures"]

            return result
        return instance


    dbcode = {
        "H": "Pfam",
        "M": "prosite_profiles",
        "R": "SMART",
        "V": "PHANTER",
        "g": "MobiDB",
        "B": "SFLD",
        "P": "prosite_patterns",
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
        key = bucket["val"] if "val" in bucket else bucket["key"]
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
        solr_query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.searcher.get_counter_object("protein", solr_query, self.get_extra_endpoints_to_count())
        )["proteins"]

    def to_structures_count_representation(self, instance):
        solr_query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object("structure", solr_query, self.get_extra_endpoints_to_count())
        )["structures"]

    def to_organism_count_representation(self, instance):
        solr_query = "entry_acc:"+escape(instance.accession) if hasattr(instance, 'accession') else None
        return webfront.serializers.taxonomy.OrganismSerializer.to_counter_representation(
            self.searcher.get_counter_object("organism", solr_query, self.get_extra_endpoints_to_count())
        )["organisms"]

    @staticmethod
    def get_entry_header_from_solr_object(obj, for_structure=False, include_entry=False, solr=None):
        header = {
            "accession": obj["entry_acc"],
            "entry_protein_locations": obj["entry_protein_locations"],
            # "name": "PTHP_BUCAI",
            "protein_length": obj["protein_length"],
            "source_database": obj["entry_db"],
            "entry_type": obj["entry_type"],
            "entry_integrated": obj["integrated"],
        }
        if for_structure:
            header["chain"] = obj["chain"]
            header["protein"] = obj["protein_acc"]
            header["protein_structure_locations"] = obj["protein_structure_locations"]
        if include_entry:
            header["entry"] = EntrySerializer.to_metadata_representation(
                Entry.objects.get(accession=obj["entry_acc"].upper()), solr
            )

        return header

    @staticmethod
    def to_ida_list_representation(obj):
        # return obj
        return {
            "count": obj["ngroups"]["value"],
            "results": [
                {"IDA": o["IDA"], "IDA_FK": o["IDA_FK"], "unique_proteins": o["unique"]["value"]}
                for o in obj['groups']
            ]
        }

    class Meta:
        model = Entry
