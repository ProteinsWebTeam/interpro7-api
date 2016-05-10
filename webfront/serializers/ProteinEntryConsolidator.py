
# class ProteinEntryConsolidator:
#     def __init__(self, view):
#         self.view = view


def consolidate_protein_entry(view):
    from webfront.models import ProteinEntryFeature
    from webfront.serializers.uniprot import ProteinSerializer
    from webfront.views.custom import SerializerDetail
    queryset = view.queryset
    serializer_class = view.serializer_class
    serializer_detail = view.serializer_detail
    serializer_detail_filter = view.serializer_detail_filter
    if queryset.model is ProteinEntryFeature:
        if serializer_class == ProteinSerializer:
            obj = None
            for row in queryset:
                if obj is None:
                    obj = ProteinSerializer.endpoint_representation({}, row.protein, serializer_detail)
                    obj["entries"] = []
                # obj["entries"].append(ProteinSerializer.to_match_representation(
                #     row,
                #     serializer_detail_filter == SerializerDetail.ENTRY_PROTEIN_DETAIL))
                obj["entries"].append(ProteinSerializer.filter_representation({}, row, serializer_detail_filter))
            return obj
    return None
