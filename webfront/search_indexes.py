from haystack import indexes
from webfront.models import ProteinEntryFeature


class ProteinEntryFeatureIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    protein_ac = indexes.CharField(model_attr='protein_id')
    method_ac = indexes.CharField(model_attr='entry_id')
    pos_from = indexes.CharField()
    pos_to = indexes.CharField()
    status = indexes.CharField()
    dbcode = indexes.CharField()
    evidence = indexes.CharField(null=True)
    seq_date = indexes.CharField()
    match_date = indexes.CharField()
    timestamp = indexes.CharField()
    userstamp = indexes.CharField()
    score = indexes.CharField(null=True)

    def get_model(self):
        return ProteinEntryFeature
