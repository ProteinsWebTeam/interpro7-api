from django.conf import settings

import pysolr


class SolrController:

    def __init__(self, queryset_manager= None):
        self.solr = pysolr.Solr(settings.HAYSTACK_CONNECTIONS['default']['URL'], timeout=10)
        self.queryset_manager = queryset_manager

    def get_number_of_field_by_endpoint(self, endpoint, field, accession):
        res = self.solr.search(endpoint+"_acc:" + accession, **{
            'group': 'true',
            'group.field': field,
            'group.ngroups': 'true',
            'rows': 0,
        })
        return res.grouped[field]["ngroups"]

    def get_chain(self):
        print(self.queryset_manager.get_solr_query())
        res = self.solr.search(self.queryset_manager.get_solr_query(), **{
            'fl': 'chain, structure_acc, protein_acc, protein_db, tax_id, protein_structure_coordinates:[json]',
        })
        return res.raw_response["response"]["docs"]
