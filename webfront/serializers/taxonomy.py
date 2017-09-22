from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Taxonomy, Proteome
import webfront.serializers.interpro
import webfront.serializers.uniprot
import webfront.serializers.pdb
from webfront.views.queryset_manager import escape


class OrganismSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(representation, instance, self.detail_filters, self.detail)
        return representation

    def endpoint_representation(self, representation, instance):
        detail = self.detail
        if detail == SerializerDetail.ALL:
            representation = self.to_full_representation(instance)
        elif detail == SerializerDetail.ORGANISM_TAXONOMY_PROTEOME:
            representation = self.to_full_representation(instance, True)
        elif detail == SerializerDetail.ORGANISM_PROTEOME:
            representation = self.to_full_proteome_representation(instance)
        elif detail == SerializerDetail.ORGANISM_OVERVIEW:
            representation = self.to_counter_representation(instance)
        elif detail == SerializerDetail.ORGANISM_HEADERS:
            representation = self.to_headers_representation(instance)
        elif detail == SerializerDetail.ORGANISM_PROTEOME_HEADERS:
            representation = self.to_headers_proteome_representation(instance)
        elif detail == SerializerDetail.ORGANISM_TAXONOMY_PROTEOME_HEADERS:
            representation = self.to_headers_representation(instance, True)
        return representation

    def filter_representation(self, representation, instance, detail_filters, detail):
        s = self.searcher
        if SerializerDetail.ENTRY_OVERVIEW in detail_filters:
            representation["entries"] = self.to_entries_count_representation(instance)
        if SerializerDetail.PROTEIN_OVERVIEW in detail_filters:
            representation["proteins"] = self.to_proteins_count_representation(instance)
        if SerializerDetail.STRUCTURE_OVERVIEW in detail_filters:
            representation["structures"] = self.to_structures_count_representation(instance)
        if detail != SerializerDetail.ORGANISM_OVERVIEW:
            if SerializerDetail.ENTRY_DB in detail_filters or \
                    SerializerDetail.ENTRY_DETAIL in detail_filters:
                representation["entries"] = self.to_entries_detail_representation(
                    instance, s, self.get_searcher_query(instance)
                )
            if SerializerDetail.STRUCTURE_DB in detail_filters or \
                    SerializerDetail.STRUCTURE_DETAIL in detail_filters:
                representation["structures"] = self.to_structures_detail_representation(
                    instance, s, self.get_searcher_query(instance)
                )
            if SerializerDetail.PROTEIN_DB in detail_filters or \
                    SerializerDetail.PROTEIN_DETAIL in detail_filters:
                representation["proteins"] = self.to_proteins_detail_representation(
                    instance, self.searcher, self.get_searcher_query(instance),
                    include_chains=True, include_coordinates=False
                )
        return representation

    def to_full_representation(self, instance, include_proteomes=False):
        s = self.searcher
        obj = {
            "metadata": {
                "accession": instance.accession,
                "lineage": instance.lineage,
                "rank": instance.rank,
                "children": instance.children,
                "source_database": "taxonomy",
                "parent": instance.parent.accession if instance.parent is not None else None,
                "name": {
                    "name": instance.scientific_name,
                    "short": instance.full_name,
                },
                "counters": {
                    "entries": s.get_number_of_field_by_endpoint("organism", "entry_acc", instance.accession),
                    "structures": s.get_number_of_field_by_endpoint("organism", "structure_acc", instance.accession),
                    "proteins": s.get_number_of_field_by_endpoint("organism", "protein_acc", instance.accession)
                }
            }
        }
        if include_proteomes:
            obj["proteomes"] = [OrganismSerializer.to_full_proteome_representation(p)
                                for p in instance.proteome_set.all()
                                ]
        return obj

    def to_full_proteome_representation(self, instance):
        s = self.searcher
        return {
            "metadata": {
                "accession": instance.accession,
                "name": {
                    "name": instance.name
                },
                "source_database": "proteome",
                "is_reference": instance.is_reference,
                "strain": instance.strain,
                "assembly": instance.assembly,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None,
                "counters": {
                    "entries": s.get_number_of_field_by_endpoint("organism", "entry_acc", instance.taxonomy.accession),
                    "structures": s.get_number_of_field_by_endpoint("organism", "structure_acc", instance.taxonomy.accession),
                    "proteins": s.get_number_of_field_by_endpoint("organism", "protein_acc", instance.taxonomy.accession)
                }

            }
        }

    @staticmethod
    def to_counter_representation(instance):
        if "organisms" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise ReferenceError('There are not structures for this request')
            instance = {
                "organisms": OrganismSerializer.serialize_counter_bucket(instance["databases"], "organisms")
            }
        return instance

    @staticmethod
    def serialize_counter_bucket(bucket, plural):
        output = {
            "taxonomy": bucket["unique"],
            "proteome": bucket["proteomes"]
        }
        is_searcher = True
        if isinstance(output["taxonomy"], dict):
            output["taxonomy"] = output["taxonomy"]["value"]
            output["proteome"] = output["proteome"]["value"]
            is_searcher = False
        if "entry" in bucket or "protein" in bucket or "structure" in bucket:
            output = {
                "taxonomy": {"organisms": output["taxonomy"]},
                "proteome": {"organisms": output["proteome"]},
            }
            # output = {"organisms": output}
            if "entry" in bucket:
                output["taxonomy"]["entries"] = bucket["entry"] if is_searcher else bucket["entry"]["value"]
                output["proteome"]["entries"] = bucket["entry"] if is_searcher else bucket["entry"]["value"]
            if "protein" in bucket:
                output["taxonomy"]["proteins"] = bucket["protein"] if is_searcher else bucket["protein"]["value"]
                output["proteome"]["proteins"] = bucket["protein"] if is_searcher else bucket["protein"]["value"]
            if "structure" in bucket:
                output["taxonomy"]["structures"] = bucket["structure"] if is_searcher else bucket["structure"]["value"]
                output["proteome"]["structures"] = bucket["structure"] if is_searcher else bucket["structure"]["value"]
        return output

    @staticmethod
    def to_headers_representation(instance, include_proteomes=False):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "name": instance.full_name,
                "children": instance.children,
                "parent": instance.parent.accession if instance.parent is not None else None,
                "source_database": "taxonomy"
            }
        }
        if include_proteomes:
            obj["proteomes"] = [p.accession for p in instance.proteome_set.all()]
            obj["source_database"] = "proteome"
        return obj

    @staticmethod
    def to_headers_proteome_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "is_reference": instance.is_reference,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None,
                "source_database": "taxonomy" if instance.taxonomy is not None else "proteome",
            }
        }

    @staticmethod
    def get_searcher_query(instance):
        if isinstance(instance, Taxonomy):
            return "lineage:" + escape(instance.accession).lower() if hasattr(instance, 'accession') else None
        if isinstance(instance, Proteome):
            return "proteomes:" + escape(instance.accession).lower() if hasattr(instance, 'accession') else None
        return None

    def to_entries_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.interpro.EntrySerializer.to_counter_representation(
            self.searcher.get_counter_object("entry", query, self.get_extra_endpoints_to_count()),
            self.detail_filters
        )["entries"]

    def to_proteins_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.uniprot.ProteinSerializer.to_counter_representation(
            self.searcher.get_counter_object("protein", query, self.get_extra_endpoints_to_count())
        )["proteins"]

    def to_structures_count_representation(self, instance):
        query = self.get_searcher_query(instance)
        return webfront.serializers.pdb.StructureSerializer.to_counter_representation(
            self.searcher.get_counter_object("structure", query, self.get_extra_endpoints_to_count())
        )["structures"]

    @staticmethod
    def get_organism_from_search_object(obj, include_chain=False):
        header = {
            "accession": obj["tax_id"],
            "lineage": obj["lineage"],
            "proteomes": obj["proteomes"],
            "source_database": "taxonomy"
        }
        if include_chain:
            header["chain"] = obj["chain"]
        return header

