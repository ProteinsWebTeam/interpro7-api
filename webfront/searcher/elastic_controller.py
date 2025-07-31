from http.client import HTTPSConnection
from base64 import b64encode
import ssl

import urllib.parse
import json
import re

from webfront.views.queryset_manager import escape
from webfront.searcher.search_controller import SearchController

from django.conf import settings
import logging

es_results = list()


def parseCursor(cursor):
    fields = {}
    for item in cursor.split(","):
        k, t, v = item.split("|")
        if t == "f":
            fields[k] = float(v)
        elif t == "i":
            fields[k] = int(v)
        else:
            fields[k] = v.lower()

    return fields


def encodeCursor(keys):
    if not keys:
        return None
    output = []
    for k, v in keys.items():
        if isinstance(v, float):
            t = "f"
        elif isinstance(v, int):
            t = "i"
        else:
            t = "s"
        output.append("{}|{}|{}".format(k, t, v))

    return ",".join(output)


def getAfterBeforeFromCursor(cursor):
    after = {}
    before = {}
    if cursor is not None:
        if cursor[0] == "-":
            before = parseCursor(cursor[1:])
        else:
            after = parseCursor(cursor)
    return after, before


# Authorization token: we need to base 64 encode it and then
# decode it to acsii as python 3 stores it as a byte string
def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


class ElasticsearchController(SearchController):
    def __init__(self, queryset_manager=None):
        url = urllib.parse.urlparse(settings.SEARCHER_URL)
        proxy = settings.HTTP_PROXY
        self.server = url.hostname
        self.port = url.port
        self.index = settings.SEARCHER_INDEX
        self.queryset_manager = queryset_manager
        self.headers = {"Content-Type": "application/json"}
        using_auth = settings.SEARCHER_USER != ""
        if using_auth:
            self.headers["Authorization"] = basic_auth(
                settings.SEARCHER_USER, settings.SEARCHER_PASSWORD
            )
        if proxy is not None and proxy != "":
            proxy = urllib.parse.urlparse(proxy)
            self.connection = HTTPSConnection(
                proxy.hostname,
                proxy.port,
                context=ssl._create_unverified_context() if url.scheme == "https" else None,
            )
            self.connection.set_tunnel(self.server, self.port)
        else:
            self.connection = HTTPSConnection(
                self.server,
                self.port,
                context=ssl._create_unverified_context() if url.scheme == "https" else None,
            )

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
        index = settings.SEARCHER_IDA_INDEX if is_ida else self.index
        self.connection.request("POST", "/" + index + "/_bulk/", body, self.headers)
        response = self.connection.getresponse()
        return response

    def clear_all_docs(self):
        body = '{ "query": { "match_all": {} } }'

        self.connection.request(
            "POST",
            "/" + self.index + "/_delete_by_query?conflicts=proceed",
            body,
            self.headers,
        )
        return self.connection.getresponse()

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
        qs = self.queryset_manager.get_searcher_query(use_lineage=True)
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
            if self.queryset_manager.main_endpoint == "structure":
                acc_field = "structure_protein_acc"
                db_field = "structure_protein_db"
            else:
                acc_field = "protein_acc"
                db_field = "protein_db"

            facet["aggs"]["databases"]["terms"]["field"] = db_field
            facet["aggs"]["databases"]["aggs"]["unique"]["cardinality"]["field"] = acc_field

            facet["aggs"]["uniprot"] = {
                "filter": {"exists": {"field": acc_field}},
                "aggs": {"unique": {"cardinality": {"field": acc_field}}},
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
            # the query might have a sorting parameter, so fq needs to be prepend
            query = fq + " && " + query
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

    def get_cardinality_field(self, endpoint):
        filters = self.queryset_manager.filters
        if endpoint == "protein" and filters.get("structure") and not filters.get("entry"):
            return "structure_protein_acc"

        return endpoint + "_acc"

    def get_list_of_endpoint(self, endpoint, query=None, rows=10, start=0, cursor=None):
        should_keep_elastic_order = False
        qs = self.queryset_manager.get_searcher_query() if query is None else query
        if qs == "":
            qs = "*:*"
        facet = {
            "aggs": {
                "ngroups": {"cardinality": {"field": self.get_cardinality_field(endpoint)}},
                "groups": {
                    "composite": {
                        "size": rows,
                        "sources": [
                            {"source": {"terms": {"field": self.get_cardinality_field(endpoint)}}}
                        ],
                    }
                },
            },
            "size": 0,
        }

        # Sort buckets by custom fields

        match = re.search(r"&?sort=(\w+):(\w+)", qs)
        if match:
            fields = self.queryset_manager.order_field.split(",")
            fields.reverse()
            for order_field in fields:
                [field, direction] = order_field.split(":")
                if field != facet["aggs"]["ngroups"]["cardinality"]["field"]:
                    # Custom field takes priority over default one ('source')
                    facet["aggs"]["groups"]["composite"]["sources"].insert(
                        0, {field: {"terms": {"field": field, "order": direction}}}
                    )
                    should_keep_elastic_order = True

        after, before = getAfterBeforeFromCursor(cursor)
        reset_direction = self.addAfterKeyToQueryComposite(
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
        if reset_direction:
            accessions.reverse()
            self.reverseOrderDirection(facet["aggs"]["groups"]["composite"])
        after_key = self.getAfterKey(response, facet, before, qs)
        before_key = self.getBeforeKey(response, facet, before, qs)
        return accessions, count, after_key, before_key, should_keep_elastic_order

    def get_chain(self):
        qs = self.queryset_manager.get_searcher_query()
        response = self._elastic_json_query(qs)
        return [ch["_source"] for ch in response["hits"]["hits"]]

    def get_document_by_any_accession(self, accession):
        acc = escape(accession)
        q = "entry_acc:{} or protein_acc:{} or structure_acc:{} or proteome_acc:{} or set_acc:{}".format(
            acc, acc, acc, acc, acc
        )
        if acc.isnumeric():
            q += " or tax_id:{}".format(acc)
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
        return "{}|{}".format(doc["counts"], doc["ida_id"])

    def _get_parts_from_cursor(self, cursor):
        return cursor.split("|")

    def ida_query(self, query, size, cursor, is_testing_page=False):
        obj = {"sort": [{"counts": "desc"}, {"ida_id": "asc"}], "size": size}

        if cursor is not None:
            if cursor[0] == "-":
                obj["sort"][0]["counts"] = "asc"
                obj["sort"][1]["ida_id"] = "desc"
                obj["search_after"] = self._get_parts_from_cursor(cursor[1:])
            else:
                obj["search_after"] = self._get_parts_from_cursor(cursor)

        response = self.execute_query(query, None, None, obj, True)
        if not is_testing_page and len(response["hits"]["hits"]) > 0:
            hits = response["hits"]["hits"]
            if cursor is not None and cursor[0] == "-":
                response["hits"]["hits"] = hits = hits[::-1]
            after_key = self._get_cursor_from_doc(hits[-1]["_source"])
            before_key = "-" + self._get_cursor_from_doc(hits[0]["_source"])
            test_after = self.ida_query(query, size, after_key, True)
            if len(test_after["hits"]["hits"]) > 0:
                response["after_key"] = after_key
            test_before = self.ida_query(query, size, before_key, True)
            if len(test_before["hits"]["hits"]) > 0:
                response["before_key"] = before_key
        return response

    def execute_query(self, query, fq=None, rows=0, query_obj=None, is_ida=False):
        logger = logging.getLogger("interpro.elastic")
        if query is None:
            query = self.queryset_manager.get_searcher_query()
        q = query
        if fq is not None:
            q = fq.lower() + " && " + query
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
        path = f"/{index}/_search?request_cache=true&q={q}"
        logger.debug("URL:" + path)
        self.connection.request("GET", path, json.dumps(query_obj), self.headers)
        response = self.connection.getresponse()
        data = response.read().decode()
        obj = json.loads(data)
        if settings.DEBUG:
            es_results.append(obj)
        return obj

    def addAfterKeyToQueryComposite(self, composite, after, before):
        if after:
            composite["after"] = after
            return False
        elif before:
            composite["after"] = before
            self.reverseOrderDirection(composite)
            return True

    def getAfterKey(self, response, facet, before, qs):
        after_key = None
        if before:
            try:
                after_key = response["aggregations"]["groups"]["buckets"][0]["key"]
            except:
                pass
        elif "after_key" in response["aggregations"]["groups"]:
            after_key = response["aggregations"]["groups"]["after_key"]

        if after_key is not None:
            facet["aggs"]["groups"]["composite"]["after"] = after_key
            next_response = self._elastic_json_query(qs, facet)
            if len(next_response["aggregations"]["groups"]["buckets"]) == 0:
                after_key = None
        return encodeCursor(after_key)

    def getBeforeKey(self, response, facet, before, qs):
        before_key = None
        try:
            if before:
                before_key = response["aggregations"]["groups"]["buckets"][-1]["key"]
            else:
                before_key = response["aggregations"]["groups"]["buckets"][0]["key"]
        except:
            pass
        if before_key:
            facet["aggs"]["groups"]["composite"]["after"] = before_key
            self.reverseOrderDirection(facet["aggs"]["groups"]["composite"])
            prev_response = self._elastic_json_query(qs, facet)
            if len(prev_response["aggregations"]["groups"]["buckets"]) == 0:
                before_key = None
        return encodeCursor(before_key)

    def reverseOrderDirection(self, composite):
        for field in composite["sources"]:
            for k, v in field.items():
                if v["terms"].get("order", "asc") == "asc":
                    v["terms"]["order"] = "desc"
                else:
                    v["terms"]["order"] = "asc"
