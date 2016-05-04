
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
    if queryset.model is ProteinEntryFeature:
        if serializer_class == ProteinSerializer:
            obj = None
            for row in queryset:
                if obj is None:
                    obj = ProteinSerializer.to_full_representation(row.protein)
                    obj["entries"] = []
                obj["entries"].append(ProteinSerializer.to_match_representation(
                    row,
                    serializer_detail == SerializerDetail.ENTRY_PROTEIN_DETAIL))
            return obj
    return None
