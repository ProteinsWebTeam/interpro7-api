from django.shortcuts import render
from rest_framework import viewsets, generics
from webfront.models import interpro as interproModels
from webfront.serializers import interpro as interproSerializers


# class EntryViewSet(viewsets.ModelViewSet):
#     queryset = interpro.Entry.objects.using('interpro_ro').all()
#     serializer_class = IPSerializers.EntrySerializer


# class EntryViewSet(viewsets.ModelViewSet):
#     serializer_class = interproSerializers.EntrySerializer
#
#     def get_queryset(self):
#         queryset = interproModels.Entry.objects.using('interpro_ro').select_related().prefetch_related()
#         types = set(
#             [t.lower for t in self.request.query_params.getlist('type', ['all'])]
#         )
#         # print(dir(queryset))
#         # print(queryset.values()[0])
#         # print(len(queryset.values()))
#         if 'all' in types:
#             return queryset
#         else:
#             #for t in types:
#             #
#             return queryset

#
# class SingleEntryViewSet(viewsets.ModelViewSet):
#     serializer_class = interproSerializers.EntrySerializer
#
#     def get_queryset(self, acc):
#         queryset = interproModels.Entry.objects.using('interpro_ro').select_related().prefetch_related().get(entry_ac=acc)
#         types = set(
#             [t.lower for t in self.request.query_params.getlist('type', ['all'])]
#         )
#         # print(dir(queryset))
#         # print(queryset.values()[0])
#         # print(len(queryset.values()))
#         if 'all' in types:
#             return queryset
#         else:
#             #for t in types:
#             #
#             return queryset


class CvDatabaseViewSet(viewsets.ModelViewSet):
    queryset = interproModels.CvDatabase.objects.using('interpro_ro').all()
    serializer_class = interproSerializers.CvDatabaseSerializer
