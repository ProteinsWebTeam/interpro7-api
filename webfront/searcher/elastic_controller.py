from django.conf import settings
import http.client
import json
import urllib.parse

from webfront.searcher.search_controller import SearchController

from django.conf import settings
import logging

es_results = list()

class ElasticsearchController(SearchController):

    def __init__(self, queryset_manager=None):
        url = urllib.parse.urlparse(settings.SEARCHER_URL)
        self.server = url.hostname
        self.port = url.port
        parts = url.path.split("/")
        self.index = parts[1]
        self.type = parts[2]
        self.queryset_manager = queryset_manager
        self.headers = {"Content-Type": "application/json"}
        self.connection = http.client.HTTPConnection(self.server, self.port)

    def add(self, docs):
        body = ""
        for doc in docs:
            body += '{ "index": { "_type": "'+self.type+'", "_id":"'+doc["id"]+'"}}\n'+json.dumps(doc)+'\n'
        conn = http.client.HTTPConnection(self.server, self.port)
        conn.request("POST", "/"+self.index+"/_bulk/", body, self.headers)
        return conn.getresponse()

    def clear_all_docs(self):
        body = '{ "query": { "match_all": {} } }'
        conn = http.client.HTTPConnection(self.server, self.port)
        conn.request(
            "POST",
            "/"+self.index+"/"+self.type+"/_delete_by_query?conflicts=proceed",
            body,
            self.headers
        )
        return conn.getresponse()

    def get_grouped_object(self, endpoint, field, query=None, extra_counters=[], size=10):
        qs = self.queryset_manager.get_searcher_query()
        if qs == '':
            qs = '*:*'
        if query is not None:
            qs += ' && ' + query.lower()
        facet = {
            "aggs": {
                "groups": {
                    "terms": {
                        "field": field,
                        "size": size,
                        "execution_hint": "map",
                    },
                    "aggs": {
                        "unique": {
                            "cardinality": {"field": "{}_acc".format(endpoint)}
                        },
                    }
                }
            },
            "size": 0
        }
        for ec in extra_counters:
            facet["aggs"]["groups"]["aggs"][ec] = {"cardinality": {"field": "{}_acc".format(ec)}}
        response = self._elastic_json_query(qs, facet)
        return response["aggregations"]

    def get_counter_object(self, endpoint, query=None, extra_counters=[]):
        qs = self.queryset_manager.get_searcher_query()
        if qs == '':
            qs = '*:*'
        if query is not None:
            qs += ' && ' + query.lower()
        facet = {
            "aggs": {
                "databases": {
                    "terms": {
                        "field": "{}_db".format(endpoint),
                        "execution_hint": "map",
                        "size": 50,
                    },
                    "aggs": {
                        "unique": {
                            "cardinality": {"field": "{}_acc".format(endpoint)}
                        },
                    }
                }
            },
            "size": 0
        }
        self.add_extra_counters(facet, "databases", extra_counters)

        self.tune_counter_facet_for_entry(facet, endpoint, extra_counters)
        self.tune_counter_facet_for_protein(facet, endpoint, extra_counters)
        self.tune_counter_facet_for_structure(facet, endpoint, extra_counters)
        self.tune_counter_facet_for_taxonomy(facet, endpoint, extra_counters)
        self.tune_counter_facet_for_proteome(facet, endpoint, extra_counters)
        self.tune_counter_facet_for_set(facet, endpoint, extra_counters)

        response = self._elastic_json_query(qs, facet)
        return response["aggregations"]

    @staticmethod
    def add_extra_counters(facet, agg_name, extra_counters):
        for ec in extra_counters:
            field = "{}_acc".format(ec)
            if ec == "organism" or ec == "taxonomy":
                field = "tax_id"
            elif ec == "proteome":
                field = "proteome_acc"
            facet["aggs"][agg_name]["aggs"][ec] = {"cardinality": {"field": field}}

    def tune_counter_facet_for_entry(self, facet, endpoint, extra_counters):
        if endpoint == "entry":
            facet["aggs"]["unintegrated"] = {
                "filter": {
                    "bool": {
                        "must_not": [
                            {"term": {"entry_db": "interpro"}},
                            {"exists": {"field": "entry_integrated"}}
                        ]
                    }
                },
                "aggs": {"unique": {"cardinality": {"field": "entry_acc"}}}
            }
            facet["aggs"]["all"] = {
                "filter": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "entry_db"}}
                        ]
                    }
                },
                "aggs": {"unique": {"cardinality": {"field": "entry_acc"}}}
            }
            facet["aggs"]["integrated"] = {
                "filter": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "entry_integrated"}}
                        ]
                    }
                },
                "aggs": {"unique": {"cardinality": {"field": "entry_acc"}}}
            }
            self.add_extra_counters(facet, "unintegrated", extra_counters)
            self.add_extra_counters(facet, "integrated", extra_counters)
            self.add_extra_counters(facet, "all", extra_counters)

    def tune_counter_facet_for_protein(self, facet, endpoint, extra_counters):
        if endpoint == "protein":
            facet["aggs"]["uniprot"] = {
              "filter": {"exists": {"field": "protein_acc"}},
              "aggs": {"unique": {"cardinality": {"field": "protein_acc"}}}
            }
            self.add_extra_counters(facet, "uniprot", extra_counters)

    def tune_counter_facet_for_structure(self, facet, endpoint, extra_counters):
        if endpoint == "structure":
            facet["aggs"]["databases"]["filter"] = {"exists": {"field": "structure_acc"}}
            del facet["aggs"]["databases"]["terms"]
            self.add_extra_counters(facet, "databases", extra_counters)

    def tune_counter_facet_for_taxonomy(self, facet, endpoint, extra_counters):
        if endpoint == "taxonomy":
            facet["aggs"]["databases"]["filter"] = {"exists": {"field": "tax_id"}}
            facet["aggs"]["databases"]["aggs"]["unique"] = {
                "cardinality": {"field": "tax_id"}
            }
            del facet["aggs"]["databases"]["terms"]
            self.add_extra_counters(facet, "databases", extra_counters)

    def tune_counter_facet_for_proteome(self, facet, endpoint, extra_counters):
        if endpoint == "proteome":
            facet["aggs"]["databases"]["filter"] = {"exists": {"field": "proteome_acc"}}
            facet["aggs"]["databases"]["aggs"]["unique"] = {
                "cardinality": {"field": "proteome_acc"}
            }
            del facet["aggs"]["databases"]["terms"]
            self.add_extra_counters(facet, "databases", extra_counters)

    def tune_counter_facet_for_set(self, facet, endpoint, extra_counters):
        if endpoint == "set":
            facet["aggs"]["all"] = {
              "filter": {"exists": {"field": "set_acc"}},
              "aggs": {"unique": {"cardinality": {"field": "set_acc"}}}
            }
            self.add_extra_counters(facet, "all", extra_counters)

    def add_subterm_aggs(self, obj, field, size):
        obj["aggs"] = {
            "subgroups": {
                "terms": {
                    "field": field,
                    "size": size,
                    "execution_hint": "map",
                },
                "aggs": {
                    "tops": {"top_hits": {"size": 1}}
                }
            }
        }

    def get_group_obj_of_field_by_query(self, query, fields, fq=None, rows=1, start=0, inner_field_to_count=None):
        query = self.queryset_manager.get_searcher_query() if query is None else query
        check_multiple_fields = type(fields) is list
        field = fields[0] if check_multiple_fields else fields
        facet = {
            "aggs": {
                "ngroups": {
                    "cardinality": {
                        "field": field
                    }
                },
                "groups": {
                    "terms": {
                        "field": field,
                        "size": start+rows,
                        "execution_hint": "map",
                    },
                    "aggs": {
                        "tops": {"top_hits": {"size": 1}}
                    }
                },
            },
            "size": 0
        }
        if inner_field_to_count is not None:
            facet["aggs"]["groups"]["aggs"]["unique"] = {"cardinality": {"field": inner_field_to_count}}
        if check_multiple_fields:
            obj = facet["aggs"]["groups"]
            for f in fields[1:]:
                self.add_subterm_aggs(obj, f, start+rows)
                obj = obj["aggs"]["subgroups"]
        if fq is not None:
            query += " && "+fq
        response = self._elastic_json_query(query, facet)
        buckets = response["aggregations"]["groups"]["buckets"]
        if len(buckets)>0 and "tops" not in buckets[0]:
            buckets = [
                b for sb in buckets for b in sb["subgroups"]["buckets"]
            ]
        output = {
            "groups":  [
                bucket["tops"]["hits"]["hits"][0]["_source"]
                for bucket in buckets[start:start+rows]
            ],
            "ngroups": response["aggregations"]["ngroups"]
        }
        if inner_field_to_count is not None:
            i = 0
            for bucket in response["aggregations"]["groups"]["buckets"][start:start+rows]:
                output["groups"][i]["unique"] = bucket["unique"]
                i += 1

        return output

    def get_list_of_endpoint(self, endpoint, query=None, rows=10, start=0):
        qs = self.queryset_manager.get_searcher_query() if query is None else query
        if qs == '':
            qs = '*:*'
        facet = {
            "aggs": {
                "ngroups": {
                    "cardinality": {
                        "field": endpoint+"_acc"
                    }
                },
                "rscount": {
                    "terms": {
                        "field": '{}_acc'.format(endpoint),
                        "size": start+rows,
                        "order": {"_term": "asc"},
                        "execution_hint": "map",
                    }
                }
            },
            "size": 0
        }
        if endpoint == "organism" or endpoint == "taxonomy":
            facet["aggs"]["ngroups"]["cardinality"]["field"] = "tax_id"
            facet["aggs"]["rscount"]["terms"]["field"] = "tax_id"
        elif endpoint == "proteome":
            facet["aggs"]["ngroups"]["cardinality"]["field"] = "proteome_acc"
            facet["aggs"]["rscount"]["terms"]["field"] = "proteome_acc"
        response = self._elastic_json_query(qs, facet)
        count = len(response["aggregations"]["rscount"]["buckets"])
        if count == start + rows:
            count = response["aggregations"]["ngroups"]["value"]
        # TODO: return only the subset of interest [start:] This however requires to re think the way pagination works
        return [str(x['key']).lower() for x in response["aggregations"]["rscount"]["buckets"]], count

    def get_chain(self):
        qs = self.queryset_manager.get_searcher_query()
        response = self._elastic_json_query(qs)
        return [ch["_source"] for ch in response["hits"]["hits"]]

    def get_document_by_any_accession(self, accession):
        q = "entry_acc:{} or protein_acc:{} or structure_acc:{} or proteome_acc:{} or set_acc:{}"\
            .format(accession, accession, accession, accession, accession)
        if accession.isnumeric():
            q += " or tax_id:{}".format(accession)
        return self._elastic_json_query(q, {"size":1})

    def count_unique(self, query, field_to_count):
        qs = self.queryset_manager.get_searcher_query() if query is None else query
        if qs == '':
            qs = '*:*'
        facet = {
            "aggs": {
                "ngroups": {
                    "cardinality": {
                        "field": field_to_count
                    }
                },
            },
            "size": 0
        }
        response = self._elastic_json_query(qs, facet)
        return response["aggregations"]["ngroups"]["value"]

    # TODO: Used only for the tests... Move it there
    def execute_query(self, query, fq=None, rows=0, start=0):
        logger = logging.getLogger("interpro.elastic")
        q = query = self.queryset_manager.get_searcher_query() if query is None else query.lower()
        if fq is not None:
            q = query+" && "+fq.lower()
        q = q.replace(" && ", "%20AND%20").replace(" to ", "%20TO%20")
        path = "/"+self.index+"/"+self.type+"/_search?request_cache=true&q="+q+"&size="+str(rows)
        logger.debug("URL:"+path)
        self.connection.request(
            "GET",
            path,
            None,
            self.headers
        )
        response = self.connection.getresponse()
        data = response.read().decode()
        obj = json.loads(data)
        return [o["_source"] for o in obj["hits"]["hits"]]

    def _elastic_json_query(self, q, query_obj=None):
        logger = logging.getLogger("interpro.elastic")
        if query_obj is None:
            query_obj = {"from": 0}
        q = q.replace(" && ", "%20AND%20").replace(" to ", "%20TO%20").replace(" or ", "%20OR%20")
        path = "/"+self.index+"/"+self.type+"/_search?request_cache=true&q="+q
        logger.debug("URL:"+path)
        logger.debug("JSON:"+json.dumps(query_obj))
        self.connection.request(
            "GET",
            path,
            json.dumps(query_obj),
            self.headers
        )
        response = self.connection.getresponse()
        data = response.read().decode()
        obj = json.loads(data)
        if settings.DEBUG:
            es_results.append(obj)
        return obj
