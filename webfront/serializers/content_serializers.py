from rest_framework import serializers

from webfront.views.custom import SerializerDetail

#
# class ContentSerializer(serializers.Serializer):
#     def __init__(self, *args, **kwargs):
#         content = kwargs.pop('content', [])
#         self.detail = kwargs.pop('serializer_detail', SerializerDetail.ALL)
#
#         super(ContentSerializer, self).__init__(*args, **kwargs)
#         try:
#             for to_be_removed in set(self.Meta.optionals) - set(content):
#                 self.fields.pop(to_be_removed)
#         except AttributeError:
#             pass


class ModelContentSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        content = kwargs.pop('content', [])
        self.detail = kwargs.pop('serializer_detail', SerializerDetail.ALL)

        super(ModelContentSerializer, self).__init__(*args, **kwargs)
        try:
            for to_be_removed in set(self.Meta.optionals) - set(content):
                self.fields.pop(to_be_removed)
        except AttributeError:
            pass
