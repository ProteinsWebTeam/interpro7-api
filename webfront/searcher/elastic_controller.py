import http.client
import json
import urllib.parse

from webfront.searcher.search_controller import SearchController

from django.conf import settings
import logging

es_results = list()


def getAfterBeforeFromCursor(cursor):
    after = None
    before = None
    if cursor is not None:
        if cursor[0] == "-":
            before = cursor[1:]
        else:
            after = cursor
    return after, before


class ElasticsearchController(SearchController):
    def __init__(self, queryset_manager=None):
        url = urllib.parse.urlparse(settings.SEARCHER_URL)
        proxy = settings.HTTP_PROXY
        self.server = url.hostname
        self.port = url.port
        self.index = settings.SEARCHER_INDEX
        self.queryset_manager = queryset_manager
        self.headers = {"Content-Type": "application/json"}
        if proxy is not None and proxy != "":
            proxy = urllib.parse.urlparse(proxy)
            self.connection = http.client.HTTPConnection(proxy.hostname, proxy.port)
            self.connection.set_tunnel(self.server, self.port)
        else:
            self.connection = http.client.HTTPConnection(self.server, self.port)

    def add(self, docs, is_ida=False):
        body = ""
        for doc in docs:
            body += (
                '{ "index": { "_id":"'
                + str(doc["id"])
                + '"}}\n'
                + json.dumps(doc)
                + "\n"
            )
        conn = http.client.HTTPConnection(self.server, self.port)
        index = settings.SEARCHER_IDA_INDEX if is_ida else self.index
        conn.request("POST", "/" + index + "/_bulk/", body, self.headers)
        response = conn.getresponse()
        return response

    def clear_all_docs(self):
        body = '{ "query": { "match_all": {} } }'
        conn = http.client.HTTPConnection(self.server, self.port)
        conn.request(
            "POST",
            "/" + self.index + "/_delete_by_query?conflicts=proceed",
            body,
            self.headers,
        )
        return conn.getresponse()

    def get_grouped_object(
        self, endpoint, field, query=None, extra_counters=[], size=10
    ):
        qs = self.queryset_manager.get_searcher_query()
        if qs == "":
            qs = "*:*"
        if query is not None:
            qs += " && " + query.lower()
        facet = {
            "aggs": {
                "groups": {
                    "terms": {"field": field, "size": size, "execution_hint": "map"},
                    "aggs": {
                        "unique": {"cardinality": {"field": "{}_acc".format(endpoint)}}
                    },
                }
            },
            "size": 0,
        }
        for ec in extra_counters:
            facet["aggs"]["groups"]["aggs"][ec] = {
                "cardinality": {"field": "{}_acc".format(ec)}
            }
        response = self._elastic_json_query(qs, facet)
        return response["aggregations"]

    def get_counter_object(self, endpoint, query=None, extra_counters=[]):
        qs = self.queryset_manager.get_searcher_query()
        if qs == "":
            qs = "*:*"
        if query is not None:
            qs += " && " + query.lower()
        facet = {
            "aggs": {
                "databases": {
                    "terms": {
                        "field": "{}_db".format(endpoint),
                        "execution_hint": "map",
                        "size": 50,
                    },
                    "aggs": {
                        "unique": {"cardinality": {"field": "{}_acc".format(endpoint)}}
                    },
                }
            },
            "size": 0,
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
                            {"exists": {"field": "entry_integrated"}},
                        ]
                    }
                },
                "aggs": {"unique": {"cardinality": {"field": "entry_acc"}}},
            }
            facet["aggs"]["all"] = {
                "filter": {"bool": {"must": [{"exists": {"field": "entry_db"}}]}},
                "aggs": {"unique": {"cardinality": {"field": "entry_acc"}}},
            }
            facet["aggs"]["integrated"] = {
                "filter": {
                    "bool": {"must": [{"exists": {"field": "entry_integrated"}}]}
                },
                "aggs": {"unique": {"cardinality": {"field": "entry_acc"}}},
            }
            self.add_extra_counters(facet, "unintegrated", extra_counters)
            self.add_extra_counters(facet, "integrated", extra_counters)
            self.add_extra_counters(facet, "all", extra_counters)

    def tune_counter_facet_for_protein(self, facet, endpoint, extra_counters):
        if endpoint == "protein":
            facet["aggs"]["uniprot"] = {
                "filter": {"exists": {"field": "protein_acc"}},
                "aggs": {"unique": {"cardinality": {"field": "protein_acc"}}},
            }
            self.add_extra_counters(facet, "uniprot", extra_counters)

    def tune_counter_facet_for_structure(self, facet, endpoint, extra_counters):
        if endpoint == "structure":
            facet["aggs"]["databases"]["filter"] = {
                "exists": {"field": "structure_acc"}
            }
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
                "aggs": {"unique": {"cardinality": {"field": "set_acc"}}},
            }
            self.add_extra_counters(facet, "all", extra_counters)

    def add_subterm_aggs(self, obj, field, size):
        obj["aggs"] = {
            "subgroups": {
                "terms": {"field": field, "size": size, "execution_hint": "map"},
                "aggs": {"tops": {"top_hits": {"size": 1}}},
            }
        }

    def get_group_obj_of_field_by_query(
        self, query, fields, fq=None, rows=1, inner_field_to_count=None
    ):
        query = self.queryset_manager.get_searcher_query() if query is None else query
        check_multiple_fields = type(fields) is list
        field = fields[0] if check_multiple_fields else fields
        facet = {
            "aggs": {
                "ngroups": {"cardinality": {"field": field}},
                "groups": {
                    "terms": {"field": field, "size": rows, "execution_hint": "map"},
                    "aggs": {"tops": {"top_hits": {"size": 1}}},
                },
            },
            "size": 0,
        }
        if inner_field_to_count is not None:
            facet["aggs"]["groups"]["aggs"]["unique"] = {
                "cardinality": {"field": inner_field_to_count}
            }
        if check_multiple_fields:
            obj = facet["aggs"]["groups"]
            for f in fields[1:]:
                self.add_subterm_aggs(obj, f, rows)
                obj = obj["aggs"]["subgroups"]
        if fq is not None:
            query += " && " + fq
        response = self._elastic_json_query(query, facet)
        buckets = response["aggregations"]["groups"]["buckets"]
        if len(buckets) > 0 and "tops" not in buckets[0]:
            buckets = [b for sb in buckets for b in sb["subgroups"]["buckets"]]
        output = {
            "groups": [
                bucket["tops"]["hits"]["hits"][0]["_source"] for bucket in buckets
            ],
            "ngroups": response["aggregations"]["ngroups"],
        }
        if inner_field_to_count is not None:
            i = 0
            for bucket in response["aggregations"]["groups"]["buckets"]:
                output["groups"][i]["unique"] = bucket["unique"]
                i += 1

        return output

    def get_group_obj_copy_of_field_by_query(
        self, query, field, fq=None, rows=1, cursor=None, inner_field_to_count=None
    ):
        # TODO: change to new pagination
        query = self.queryset_manager.get_searcher_query() if query is None else query
        facet = {
            "aggs": {
                "ngroups": {"cardinality": {"field": field}},
                "groups": {
                    "composite": {
                        "size": rows,
                        "sources": [{"source": {"terms": {"field": field}}}],
                    },
                    "aggs": {"tops": {"top_hits": {"size": 1}}},
                },
            },
            "size": 0,
        }
        after, before = getAfterBeforeFromCursor(cursor)
        self.addAfterKeyToQueryComposite(
            facet["aggs"]["groups"]["composite"], after, before
        )
        if inner_field_to_count is not None:
            facet["aggs"]["groups"]["aggs"]["unique"] = {
                "cardinality": {"field": inner_field_to_count}
            }
        if fq is not None:
            query += " && " + fq
        response = self._elastic_json_query(query, facet)
        after_key = self.getAfterKey(response, facet, before, query)
        before_key = self.getBeforeKey(response, facet, before, query)
        buckets = response["aggregations"]["groups"]["buckets"]
        if len(buckets) > 0 and "tops" not in buckets[0]:
            buckets = [b for sb in buckets for b in sb["subgroups"]["buckets"]]
        output = {
            "groups": [
                bucket["tops"]["hits"]["hits"][0]["_source"] for bucket in buckets
            ],
            "ngroups": response["aggregations"]["ngroups"],
            "after_key": after_key,
            "before_key": before_key,
        }
        if inner_field_to_count is not None:
            i = 0
            for bucket in response["aggregations"]["groups"]["buckets"]:
                output["groups"][i]["unique"] = bucket["unique"]
                i += 1

        return output

    def get_list_of_endpoint(self, endpoint, query=None, rows=10, start=0, cursor=None):
        qs = self.queryset_manager.get_searcher_query() if query is None else query
        if qs == "":
            qs = "*:*"
        facet = {
            "aggs": {
                "ngroups": {"cardinality": {"field": endpoint + "_acc"}},
                "groups": {
                    "composite": {
                        "size": rows,
                        "sources": [
                            {"source": {"terms": {"field": "{}_acc".format(endpoint)}}}
                        ],
                    }
                },
            },
            "size": 0,
        }
        after, before = getAfterBeforeFromCursor(cursor)
        self.addAfterKeyToQueryComposite(
            facet["aggs"]["groups"]["composite"], after, before
        )
        if endpoint == "organism" or endpoint == "taxonomy":
            facet["aggs"]["ngroups"]["cardinality"]["field"] = "tax_id"
            facet["aggs"]["groups"]["composite"]["sources"][0]["source"]["terms"][
                "field"
            ] = "tax_id"
        elif endpoint == "proteome":
            facet["aggs"]["ngroups"]["cardinality"]["field"] = "proteome_acc"
            facet["aggs"]["groups"]["composite"]["sources"][0]["source"]["terms"][
                "field"
            ] = "proteome_acc"
        response = self._elastic_json_query(qs, facet)
        count = response["aggregations"]["ngroups"]["value"]
        accessions = [
            str(x["key"]["source"]).lower()
            for x in response["aggregations"]["groups"]["buckets"]
        ]
        after_key = self.getAfterKey(response, facet, before, qs)
        before_key = self.getBeforeKey(response, facet, before, qs)
        return accessions, count, after_key, before_key

    def get_chain(self):
        qs = self.queryset_manager.get_searcher_query()
        response = self._elastic_json_query(qs)
        return [ch["_source"] for ch in response["hits"]["hits"]]

    def get_document_by_any_accession(self, accession):
        q = "entry_acc:{} or protein_acc:{} or structure_acc:{} or proteome_acc:{} or set_acc:{}".format(
            accession, accession, accession, accession, accession
        )
        if accession.isnumeric():
            q += " or tax_id:{}".format(accession)
        return self._elastic_json_query(q, {"size": 1})

    def count_unique(self, query, field_to_count):
        qs = self.queryset_manager.get_searcher_query() if query is None else query
        if qs == "":
            qs = "*:*"
        facet = {
            "aggs": {"ngroups": {"cardinality": {"field": field_to_count}}},
            "size": 0,
        }
        response = self._elastic_json_query(qs, facet)
        return response["aggregations"]["ngroups"]["value"]

    def _get_cursor_from_doc(self, doc):
        return "{}|{}".format(doc["proteins"], doc["id"])

    def _get_parts_from_cursor(self, cursor):
        return cursor.split("|")

    def ida_query(self, query, size, cursor, is_testing_page=False):
        obj = {"sort": [{"proteins": "desc"}, {"id": "asc"}], "size": size}

        if cursor is not None:
            if cursor[0] == "-":
                obj["sort"][0]["proteins"] = "asc"
                obj["sort"][1]["id"] = "desc"
                obj["search_after"] = self._get_parts_from_cursor(cursor[1:])
            else:
                obj["search_after"] = self._get_parts_from_cursor(cursor)

        response = self.execute_query(query, None, None, obj, True)
        if not is_testing_page and len(response["hits"]["hits"]) > 0:
            after_key = self._get_cursor_from_doc(
                response["hits"]["hits"][-1]["_source"]
            )
            before_key = "-" + self._get_cursor_from_doc(
                response["hits"]["hits"][0]["_source"]
            )
            test_after = self.ida_query(query, size, after_key, True)
            if len(test_after["hits"]["hits"]) > 0:
                response["after_key"] = after_key
            test_before = self.ida_query(query, size, before_key, True)
            if len(test_before["hits"]["hits"]) > 0:
                response["before_key"] = after_key
        return response

    def execute_query(self, query, fq=None, rows=0, query_obj=None, is_ida=False):
        logger = logging.getLogger("interpro.elastic")
        if query is None:
            query = self.queryset_manager.get_searcher_query()
        q = query
        if fq is not None:
            q = query + " && " + fq.lower()
        q = (
            q.replace(" && ", "%20AND%20")
            .replace(" || ", "%20OR%20")
            .replace(" to ", "%20TO%20")
        )
        index = settings.SEARCHER_IDA_INDEX if is_ida else self.index
        path = "/{}/_search?request_cache=true&q={}".format(index, q)
        if rows is not None:
            path += "&size={}".format(rows)
        logger.debug("URL:" + path)
        self.connection.request(
            "GET", path, query_obj and json.dumps(query_obj), self.headers
        )
        response = self.connection.getresponse()
        data = response.read().decode()
        return json.loads(data)

    def _elastic_json_query(self, q, query_obj=None, is_ida=False):
        logger = logging.getLogger("interpro.elastic")
        if query_obj is None:
            query_obj = {"from": 0}
        q = (
            q.replace(" && ", "%20AND%20")
            .replace(" to ", "%20TO%20")
            .replace(" or ", "%20OR%20")
            .replace(" || ", "%20OR%20")
        )
        index = settings.SEARCHER_IDA_INDEX if is_ida else self.index
        path = "/" + index + "/_search?request_cache=true&q=" + q
        logger.debug("URL:" + path)
        self.connection.request("GET", path, json.dumps(query_obj), self.headers)
        response = self.connection.getresponse()
        data = response.read().decode()
        obj = json.loads(data)
        if settings.DEBUG:
            es_results.append(obj)
        return obj

    def addAfterKeyToQueryComposite(self, composite, after, before):
        if after is not None:
            composite["after"] = {"source": after.lower()}
        elif before is not None:
            composite["after"] = {"source": before.lower()}
            composite["sources"][0]["source"]["terms"]["order"] = "desc"

    def getAfterKey(self, response, facet, before, qs):
        after_key = None
        if before is not None:
            try:
                after_key = response["aggregations"]["groups"]["buckets"][0]["key"][
                    "source"
                ]
            except:
                pass
        elif "after_key" in response["aggregations"]["groups"]:
            after_key = response["aggregations"]["groups"]["after_key"]["source"]

        if after_key is not None:
            facet["aggs"]["groups"]["composite"]["after"] = {"source": after_key}
            facet["aggs"]["groups"]["composite"]["sources"][0]["source"]["terms"][
                "order"
            ] = "asc"
            next_response = self._elastic_json_query(qs, facet)
            if len(next_response["aggregations"]["groups"]["buckets"]) == 0:
                after_key = None
        return after_key

    def getBeforeKey(self, response, facet, before, qs):
        before_key = None
        try:
            if before is not None:
                before_key = response["aggregations"]["groups"]["buckets"][-1]["key"][
                    "source"
                ]
            else:
                before_key = response["aggregations"]["groups"]["buckets"][0]["key"][
                    "source"
                ]
        except:
            pass
        if before_key is not None:
            facet["aggs"]["groups"]["composite"]["after"] = {"source": before_key}
            facet["aggs"]["groups"]["composite"]["sources"][0]["source"]["terms"][
                "order"
            ] = "desc"
            prev_response = self._elastic_json_query(qs, facet)
            if len(prev_response["aggregations"]["groups"]["buckets"]) == 0:
                before_key = None
        return before_key
