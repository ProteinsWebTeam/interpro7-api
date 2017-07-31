from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.views.custom import SerializerDetail
from webfront.models import Taxonomy

class OrganismSerializer(ModelContentSerializer):

    def to_representation(self, instance):
        representation = {}
        representation = self.endpoint_representation(representation, instance)
        representation = self.filter_representation(representation, instance)
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

    def filter_representation(self, representation, instance):
        return representation

    @staticmethod
    def to_full_representation(instance, include_proteomes=False):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "scientific_name": instance.scientific_name,
                "full_name": instance.full_name,
                "lineage": instance.lineage,
                "rank": instance.rank,
                "children": instance.children,
                "parent": instance.parent.accession if instance.parent is not None else None
            }
        }
        if include_proteomes:
            obj["proteomes"] = [OrganismSerializer.to_full_proteome_representation(p)
                                for p in instance.proteome_set.all()
                                ]
        return obj

    @staticmethod
    def to_full_proteome_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "is_reference": instance.is_reference,
                "strain": instance.strain,
                "assembly": instance.assembly,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None
            }
        }

    @staticmethod
    def to_counter_representation(instance):
        if "organisms" not in instance:
            if ("count" in instance and instance["count"] == 0) or \
               ("doc_count" in instance["databases"] and instance["databases"]["doc_count"] == 0):
                raise ReferenceError('There are not structures for this request')
            instance = {
                "organisms": OrganismSerializer.serialize_counter_bucket(instance["databases"])
            }
        return instance


    @staticmethod
    def serialize_counter_bucket(bucket):
        output = {
            "taxa": bucket["unique"],
            "proteomes": bucket["proteomes"]
        }
        is_searcher = True
        if isinstance(output["taxa"], dict):
            output["taxa"] = output["taxa"]["value"]
            output["proteomes"] = output["proteomes"]["value"]
            is_searcher = False
        if "entry" in bucket or "protein" in bucket or "structure" in bucket:
            output = {"organisms": output}
            if "entry" in bucket:
                output["entries"] = bucket["entry"] if is_searcher else bucket["entry"]["value"]
            if "structure" in bucket:
                output["structures"] = bucket["structure"] if is_searcher else bucket["structure"]["value"]
        return output

    @staticmethod
    def to_headers_representation(instance, include_proteomes=False):
        obj = {
            "metadata": {
                "accession": instance.accession,
                "full_name": instance.full_name,
                "children": instance.children,
                "parent": instance.parent.accession if instance.parent is not None else None
            }
        }
        if include_proteomes:
            obj["proteomes"] = [p.accession for p in instance.proteome_set.all()]
        return obj

    @staticmethod
    def to_headers_proteome_representation(instance):
        return {
            "metadata": {
                "accession": instance.accession,
                "name": instance.name,
                "is_reference": instance.is_reference,
                "taxonomy": instance.taxonomy.accession if instance.taxonomy is not None else None
            }
        }
