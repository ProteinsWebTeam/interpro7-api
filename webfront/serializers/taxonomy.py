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
        # detail = self.detail
        return instance

    def filter_representation(self, representation, instance):
        return representation
