
# class ProteinEntryConsolidator:
#     def __init__(self, view):
#         self.view = view


def consolidate_protein_entry(view):
    from webfront.models import ProteinEntryFeature
    from webfront.serializers.uniprot import ProteinSerializer
    from rest_framework.response import Response

    queryset = view.queryset
    serializer_class = view.serializer_class
    serializer_detail = view.serializer_detail
    serializer_detail_filter = view.serializer_detail_filter

    if hasattr(queryset, "model") and queryset.model is ProteinEntryFeature:
        if serializer_class == ProteinSerializer:
            ordering = view.pagination_class.ordering
            view.pagination_class.ordering = "-protein_id"
            queryset = view.paginate_queryset(queryset)
            view.pagination_class.ordering = ordering
            proteins = {}
            for row in queryset:
                if row.protein not in proteins:
                    proteins[row.protein] = ProteinSerializer.endpoint_representation(
                        {}, row.protein, serializer_detail)
                    proteins[row.protein]["entries"] = []
                # obj["entries"].append(ProteinSerializer.to_match_representation(
                #     row,
                #     serializer_detail_filter == SerializerDetail.ENTRY_PROTEIN_DETAIL))
                proteins[row.protein]["entries"].append(
                    ProteinSerializer.filter_representation({}, row, serializer_detail_filter))
            if view.many:
                return view.get_paginated_response(list(proteins.values()))
            else:
                if proteins:
                    return Response(list(proteins.values())[0])
                else:
                    raise ReferenceError("Empty result for API request.")
    return None
