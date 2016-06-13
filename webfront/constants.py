from enum import Enum
from django.db import models

from webfront.models import ProteinEntryFeature, Entry, Protein, ProteinStructureFeature, Structure


class SerializerDetail(Enum):
    ALL = 1

    ENTRY_HEADERS = 100
    ENTRY_OVERVIEW = 101
    ENTRY_DETAIL = 102
    ENTRY_PROTEIN = 103
    ENTRY_PROTEIN_DETAIL = 104
    ENTRY_PROTEIN_HEADERS = 105

    PROTEIN_HEADERS = 200
    PROTEIN_OVERVIEW = 201
    PROTEIN_DETAIL = 202
    PROTEIN_ENTRY_DETAIL = 203

    STRUCTURE_HEADERS = 300
    STRUCTURE_OVERVIEW = 301
    STRUCTURE_DETAIL = 302
    STRUCTURE_CHAIN = 303
    STRUCTURE_ENTRY_DETAIL = 304
    STRUCTURE_PROTEIN_DETAIL = 305


class QuerysetType(Enum):
    ENTRY = 100
    PROTEIN = 200
    STRUCTURE = 300
    ENTRY_PROTEIN = 150
    STRUCTURE_PROTEIN = 250


def get_queryset_type(queryset):

    if isinstance(queryset, models.Model):
        if isinstance(queryset, Entry):
            return QuerysetType.ENTRY
        elif isinstance(queryset, Protein):
            return QuerysetType.PROTEIN
        elif isinstance(queryset, Structure):
            return QuerysetType.STRUCTURE
        elif isinstance(queryset, ProteinEntryFeature):
            return QuerysetType.ENTRY_PROTEIN
        elif isinstance(queryset, ProteinStructureFeature):
            return QuerysetType.STRUCTURE_PROTEIN

    if hasattr(queryset, "model"):
        if queryset.model is Entry:
            return QuerysetType.ENTRY
        elif queryset.model is Protein:
            return QuerysetType.PROTEIN
        elif queryset.model is Structure:
            return QuerysetType.STRUCTURE
        elif queryset.model is ProteinEntryFeature:
            return QuerysetType.ENTRY_PROTEIN
        elif queryset.model is ProteinStructureFeature:
            return QuerysetType.STRUCTURE_PROTEIN
    return None
