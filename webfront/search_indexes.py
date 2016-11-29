from haystack import indexes
from webfront.models import ProteinEntryFeature


class ProteinEntryFeatureIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    entry_acc = indexes.CharField(model_attr='entry_id')
    entry_type = indexes.CharField()
    entry_db = indexes.CharField()
    integrated = indexes.CharField(null=True)
    protein_acc = indexes.CharField(model_attr='protein_id')
    protein_db = indexes.CharField()
    tax_id = indexes.CharField()
    entry_protein_coordinates = indexes.CharField()
    structure_acc = indexes.CharField(null=True)
    protein_structure_coordinates = indexes.CharField(null=True)
    chain = indexes.CharField(null=True)

    def get_model(self):
        return ProteinEntryFeature
