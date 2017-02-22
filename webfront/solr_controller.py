from django.conf import settings
import json

import pysolr

from webfront.search_controller import SearchController


class SolrController(SearchController):

    def __init__(self, queryset_manager=None):
        self.solr = pysolr.Solr(settings.HAYSTACK_CONNECTIONS['default']['URL'], timeout=10)
        self.queryset_manager = queryset_manager

    def get_group_obj_of_field_by_query(self, query, field, fq=None, rows=0, start=0):
        query = self.queryset_manager.get_solr_query() if query is None else query.lower()
        parameters = {
            'group': 'true',
            'group.field': field,
            'group.ngroups': 'true',
            'rows': rows,
            'start': start,
            'fl': '*, entry_protein_coordinates:[json], protein_structure_coordinates:[json]',
        }
        if fq is not None:
            parameters['fq'] = fq.lower()
        res = self.solr.search(query, **parameters)
        res.grouped[field]["groups"] = [b["doclist"]["docs"][0] for b in res.grouped[field]["groups"]]
        return res.grouped[field]

    def get_chain(self):
        res = self.solr.search(self.queryset_manager.get_solr_query(), **{
            'fl': 'chain, structure_acc, protein_acc, protein_db, tax_id, protein_structure_coordinates:[json]',
        })
        return res.raw_response["response"]["docs"]

    def get_counter_object(self, endpoint, solr_query=None, extra_counters=[]):
        qs = self.queryset_manager.get_solr_query()
        if qs == '':
            qs = '*:*'
        if solr_query is not None:
            qs += ' && ' + solr_query.lower()
        facet = {
            "databases": {
                "type": "terms",
                "field": "{}_db".format(endpoint),
                "facet": {"unique": "unique({}_acc)".format(endpoint)}
            }
        }
        for ec in extra_counters:
            facet["databases"]["facet"][ec] = "unique({}_acc)".format(ec)
        if endpoint == "entry":
            facet["unintegrated"] = {
                "type": "query",
                "q": "!entry_db:interpro && !integrated:*",
                "facet": {"unique": "unique(entry_acc)"}
            }
            for ec in extra_counters:
                facet["unintegrated"]["facet"][ec] = "unique({}_acc)".format(ec)
        elif endpoint == "protein":
            facet["uniprot"] = {
                "type": "query",
                "q": "protein_db:*",
                "facet": {"unique": "unique(protein_acc)"}
            }
            for ec in extra_counters:
                facet["uniprot"]["facet"][ec] = "unique({}_acc)".format(ec)
        elif endpoint == "structure":
            facet["databases"]["type"] = "query"
            facet["databases"]["q"] = "structure_acc:*"
            for ec in extra_counters:
                facet["databases"]["facet"][ec] = "unique({}_acc)".format(ec)
            # return self.get_group_obj_of_field_by_query(qs, "structure_acc")
        parameters = {'facet': 'on', 'json.facet': json.dumps(facet)}
        # qs = qs.replace(" && ", "%20AND%20")
        res = self.solr.search(qs, **parameters)
        return res.raw_response["facets"]

    def get_list_of_endpoint(self, endpoint, solr_query=None):
        qs = self.queryset_manager.get_solr_query() if solr_query is None else solr_query
        if qs == '':
            qs = '*:*'
        res = self.solr.search(qs, **{
            'facet': 'on',
            'facet.pivot': '{}_acc'.format(endpoint),
            'rows': 0,
             # & facet.limit = 10 & facet.offset = 1 # for paging
        })
        return [x['value'].upper() for x in res.facets["facet_pivot"]['{}_acc'.format(endpoint)]]

    def execute_query(self, query, fq=None, rows=0, start=0):
        query = self.queryset_manager.get_solr_query() if query is None else query.lower()
        parameters = {
            'rows': rows,
            'start': start,
            'fl': '*, entry_protein_coordinates:[json], protein_structure_coordinates:[json]',
        }
        if fq is not None:
            parameters['fq'] = fq.lower()
        res = self.solr.search(query, **parameters)
        return res.docs

    def add(self, docs):
        return self.solr.add(docs)

    def clear_all_docs(self):
        return self.solr.delete(q='*:*')
