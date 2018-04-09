import time
from tqdm import tqdm

from interpro import settings
from rest_framework import status

from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from webfront.searcher.elastic_controller import ElasticsearchController
from webfront.tests.actions_on_test_dataset import *

api_test_map = {
    "entry": {
        "interpro": [
            "IPR003165",
            "IPR001165"
        ],
        "pfam": [
            "PF02171",
            "PF17180",
            "PF17176",
        ],
        "smart": [
            "SM00950",
            "SM00002",
        ],
        "profile": [
            "PS50822",
            "PS01031",
        ]
    },
    "protein": {
        "uniprot": [
            "A1CUJ5",
            "M5ADK6",
            "A0A0A2L2G2",
            "P16582",
        ],
        "reviewed": [
            "A1CUJ5",
            "M5ADK6",
        ],
        "unreviewed": [
            "A0A0A2L2G2",
            "P16582",
        ],
    },
    "structure": {
        "pdb": [
            "1JM7",
            "1T2V",
            "2BKM",
            "1JZ8",
        ]
    },
    "organism": {
        "taxonomy": [
            "1",
            "2",
            "2579",
            "40296",
            "344612",
            "1001583",
        ],
        "proteome": [
            "UP000006701",
            "UP000012042",
            "UP000030104",
        ]
    },
    "set": {
        "kegg": [
            "KEGG01"
        ],
        "pfam": [
            "CL0001",
            "CL0002"
        ]
    }
}

chains = {
    "1JM7": ["a", "b"],
    "1T2V": ["a", "b", "c", "d", "e"],
    "2BKM": ["a", "b"],
    "1JZ8": ["a", "b"],
}


class ActionsOnTestDocumentTest(InterproRESTTestCase):
    @classmethod
    def setUpClass(cls):
        super(InterproRESTTestCase, cls).setUpClass()
        search = ElasticsearchController()
        cls.all_docs = search.execute_query("*:*", rows=50)

    def tests_all_docs_are_loaded(self):
        self.assertNotEqual(None, self.all_docs)
        self.assertGreater(len(self.all_docs), 0)

    def tests_can_filter_by_entry_acc(self):
        empty = filter_by_value(self.all_docs, "entry_acc", "Unicorn")
        self.assertEqual(len(empty), 0)
        not_entry_acc = filter_by_value(self.all_docs, "entry_acc", None)
        self.assertLess(len(not_entry_acc), len(self.all_docs))
        with_entry_acc = filter_by_value(self.all_docs, "entry_acc", "*")
        self.assertLess(len(with_entry_acc), len(self.all_docs))
        self.assertEqual(len(with_entry_acc)+len(not_entry_acc), len(self.all_docs))
        filtered = filter_by_value(self.all_docs, "entry_acc", "ipr003165")
        self.assertGreater(len(filtered), 1)

    def tests_can_select(self):
        with_entry_acc = filter_by_value(self.all_docs, "entry_acc", "*")
        entry_acc_db = select_fields(with_entry_acc, ["entry_acc", "entry_db"])
        for doc in entry_acc_db:
            self.assertIn("entry_acc", doc)

    def tests_can_get_unique_set(self):
        with_entry_db = filter_by_value(self.all_docs, "entry_db", "*")
        entry_dbs = select_fields(with_entry_db, ["entry_db"])
        entry_dbs = unique(entry_dbs)
        entry_dbs = [d["entry_db"] for d in entry_dbs]
        self.assertEqual(len(entry_dbs), len(set(entry_dbs)))

    def tests_group_and_count(self):
        db_counts = group_by_field_and_count(self.all_docs, "entry_db", "entry_acc")
        for db in db_counts:
            c = 0
            for doc in self.all_docs:
                if "entry_db" in doc and doc["entry_db"] == db:
                    c += 1
            self.assertEqual(db_counts[db], c)

    def tests_group_and_count_unique(self):
        db_counts_unique = group_by_field_and_count(self.all_docs, "entry_db", "entry_acc", True)
        for db in db_counts_unique:
            uni = set()
            for doc in self.all_docs:
                if "entry_db" in doc and doc["entry_db"] == db:
                    uni.add(doc["entry_acc"])
            self.assertEqual(db_counts_unique[db], len(uni))

    def tests_contains_filter(self):
        with_root = filter_by_contain_value(self.all_docs, "lineage", "1")
        self.assertEqual(len(self.all_docs), len(with_root))
        with_bacteria = filter_by_contain_value(self.all_docs, "lineage", "2")
        self.assertGreater(len(self.all_docs), len(with_bacteria))
        with_tax_id = filter_by_value(self.all_docs, "tax_id", 344612)
        with_parent = filter_by_contain_value(with_tax_id, "lineage", "2579")
        self.assertEqual(len(with_parent), len(with_tax_id))


PAYLOAD_TYPE_COUNTER = 1
PAYLOAD_TYPE_LIST = 2
PAYLOAD_TYPE_ENTITY = 3


def get_url(endpoints, dbs=None, accs=None):
    url = "/api"
    for i in range(len(endpoints)):
        url += "/" + endpoints[i]
        if dbs is not None and dbs[i] is not None:
            url += "/" + dbs[i]
            if accs is not None and accs[i] is not None:
                url += "/" + accs[i]
    return url


class ThreeEndpointsTableTest(InterproRESTTestCase):
    @classmethod
    def setUpClass(cls):
        super(ThreeEndpointsTableTest, cls).setUpClass()
        search = ElasticsearchController()
        cls.all_docs = search.execute_query("*:*", rows=50)

    def assert_response_equal_to_expectd(self, url, data, payload_type, endpoints, dbs, accs):
        response = self._get_in_debug_mode(url)
        if len(data) == 0:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                             "It should be an empty response for URL {}".format(url))
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             "It should be an OK response for URL {}".format(url))
            if payload_type == PAYLOAD_TYPE_COUNTER:
                expected = get_counter_payload(data, endpoints, dbs, accs)
                self.assertEqual(
                    response.data, expected,
                    "The URL {} wasn't equal to the expected response.\nRESPONSE: {}\nEXPECTED: {}"
                    .format(url, response.data, expected)
                )
            elif payload_type == PAYLOAD_TYPE_LIST:
                expected = get_db_payload(data, endpoints, dbs, accs)
                self.assert_db_response_is_as_expected(response, expected, endpoints[0], url)
            elif payload_type == PAYLOAD_TYPE_ENTITY:
                expected = get_acc_payload(data, endpoints, dbs, accs)
                self.assert_obj_response_is_as_expected(
                    response.data, expected, endpoints[0], url
                )

    def assert_chain_urls(self, data, endpoints, dbs, accs):
        payload_type = PAYLOAD_TYPE_COUNTER
        if dbs[0] is not None:
            payload_type = PAYLOAD_TYPE_LIST
            if accs is not None and accs[0] is not None:
                payload_type = PAYLOAD_TYPE_ENTITY
        for i in range(len(accs)):
            if accs[i] is not None and endpoints[i] == "structure":
                for chain in chains[accs[i]]:
                    accs_copy = accs.copy()
                    accs_copy[i] = accs_copy[i] + "/" + chain
                    url = get_url(endpoints, dbs, accs_copy)
                    with_chain = filter_by_value(data, "chain", chain)
                    self.assert_response_equal_to_expectd(
                        url, with_chain, payload_type, endpoints, dbs, accs
                    )

    def assert_db_integration_urls(self, data, endpoints, dbs, accs=None):
        payload_type = PAYLOAD_TYPE_COUNTER
        if dbs[0] is not None:
            payload_type = PAYLOAD_TYPE_LIST
            if accs is not None and accs[0] is not None:
                payload_type = PAYLOAD_TYPE_ENTITY

        for i in range(len(dbs)):
            if dbs[i] is not None and endpoints[i] == "entry" and dbs[i] != "interpro":
                dbs_copy = dbs.copy()
                dbs_copy[i] = "unintegrated/"+dbs_copy[i]
                url = get_url(endpoints, dbs_copy, accs)
                unintegrated = filter_by_value(data, "integrated", None)
                unintegrated = exclude_by_value(unintegrated, "entry_db", "interpro")
                self.assert_response_equal_to_expectd(url, unintegrated, payload_type, endpoints, dbs, accs)

                dbs_copy = dbs.copy()
                dbs_copy[i] = "integrated/"+dbs_copy[i]
                url = get_url(endpoints, dbs_copy, accs)
                integrated = filter_by_value(data, "integrated", "*")
                self.assert_response_equal_to_expectd(url, integrated, payload_type, endpoints, dbs, accs)

    def test_endpoint_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                        continue
                    url = "/api/{}/{}/{}".format(endpoint1, endpoint2, endpoint3)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status.HTTP_200_OK, "URL: [{}]".format(url))
                    data = filter_by_endpoint(self.all_docs, endpoint1)
                    data = filter_by_endpoint(data, endpoint2)
                    data = filter_by_endpoint(data, endpoint3)
                    expected = get_counter_payload(data, [endpoint1, endpoint2, endpoint3])
                    self.assertEqual(
                        response.data, expected,
                        "The URL {} wasn't equal to the expected response.\nRESPONSE: {}\nEXPECTED: {}"
                        .format(url, response.data, expected)
                    )

    def test_endpoint_endpoint_db(self):
        for endpoint1 in ['set']: #api_test_map:
            for endpoint2 in ['entry']: # api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in ['protein']: # api_test_map:
                    if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                        continue
                    for db3 in ["uniprot"]: #api_test_map[endpoint3]:
                        url = "/api/{}/{}/{}/{}".format(endpoint1, endpoint2, endpoint3, db3)
                        response = self._get_in_debug_mode(url)
                        data = filter_by_endpoint(self.all_docs, endpoint1)
                        data = filter_by_endpoint(data, endpoint2)
                        data = filter_by_endpoint(data, endpoint3, db3)
                        if len(data) == 0:
                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                             "It should be an empty response for URL {}".format(url))
                        else:
                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                             "It should be an OK response for URL {}".format(url))
                            expected = get_counter_payload(
                                data,
                                [endpoint1, endpoint2, endpoint3],
                                [None, None, db3]
                            )
                            self.assertEqual(
                                response.data, expected,
                                "The URL {} wasn't equal to the expected response.\nRESPONSE: {}\nEXPECTED: {}"
                                .format(url, response.data, expected)
                            )

                            # test_endpoint_db_endpoint
                            url = "/api/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, endpoint2)
                            response2 = self.client.get(url)
                            self.assertEqual(response2.status_code, status.HTTP_200_OK, "URL: [{}]".format(url))
                            self.assertEqual(
                                response2.data, expected,
                                "The URL {} wasn't equal to the expected response.\nRESPONSE: {}\nEXPECTED: {}"
                                .format(url, response.data, expected)
                            )
                            self.assert_db_integration_urls(
                                data,
                                [endpoint1, endpoint2, endpoint3],
                                [None, None, db3]
                            )

    def test_endpoint_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                        continue
                    for db3 in api_test_map[endpoint3]:
                        for acc3 in api_test_map[endpoint3][db3]:
                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint2, endpoint3, db3, acc3)
                            response = self._get_in_debug_mode(url)
                            data = filter_by_endpoint(self.all_docs, endpoint1)
                            data = filter_by_endpoint(data, endpoint2)
                            data = filter_by_endpoint(data, endpoint3, db3, acc3)
                            if len(data) == 0:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                 "It should be an empty response for URL {}".format(url))
                            else:
                                self.assertEqual(
                                    response.status_code, status.HTTP_200_OK,
                                    "It should be an OK response for URL {}".format(url)
                                )
                                eps = [endpoint1, endpoint2, endpoint3]
                                dbs = [None, None, db3]
                                accs = [None, None, acc3]
                                expected = get_counter_payload(data, eps, dbs, accs)
                                self.assertEqual(
                                    len(response.data), len(expected),
                                    "The URL {} wasn't equal to the expected response.\nRESPONSE: {}\nEXPECTED: {}"
                                    .format(url, response.data, expected)
                                )
                                for key in response.data:
                                    self.assertEqual(
                                        response.data[key], expected[key],
                                        "The URL {} wasn't equal. Response on key {}.\nRESPONSE: {}\nEXPECTED: {}"
                                        .format(url, key, response.data, expected)
                                    )

                                # test_endpoint_acc_endpoint
                                url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, acc3, endpoint2)
                                response2 = self.client.get(url)
                                self.assertEqual(response2.status_code, status.HTTP_200_OK, "URL: [{}]".format(url))
                                self.assertEqual(
                                    len(response.data), len(expected),
                                    "The URL {} wasn't equal to the expected response.\nRESPONSE: {}\nEXPECTED: {}"
                                    .format(url, response.data, expected)
                                )
                                for key in response.data:
                                    self.assertEqual(
                                        response.data[key], expected[key],
                                        "The URL {} wasn't equal. Response on key {}.\nRESPONSE: {}\nEXPECTED: {}"
                                        .format(url, key, response.data, expected)
                                    )
                                self.assert_db_integration_urls(data, eps, dbs, accs)
                                self.assert_chain_urls(data, eps, dbs, accs)

    def test_endpoint_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db2 in api_test_map[endpoint2]:
                    for endpoint3 in api_test_map:
                        if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                            continue
                        for db3 in api_test_map[endpoint3]:
                            if not settings.DEBUG:
                                time.sleep(0.1)
                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint2, db2, endpoint3, db3)
                            response = self._get_in_debug_mode(url)
                            data = filter_by_endpoint(self.all_docs, endpoint1)
                            data = filter_by_endpoint(data, endpoint2, db2)
                            data = filter_by_endpoint(data, endpoint3, db3)
                            if len(data) == 0:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                 "It should be an empty response for URL {}".format(url))
                            else:
                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                 "It should be an OK response for URL {}".format(url))

                                expected = get_counter_payload(
                                    data,
                                    [endpoint1, endpoint2, endpoint3],
                                    [None, db2, db3],
                                )

                                self.assertEqual(response.data, expected)

                                url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, endpoint2, db2)
                                response = self.client.get(url)
                                self.assertEqual(response.status_code, status.HTTP_200_OK)
                                self.assertEqual(response.data, expected)
                                self.assert_db_integration_urls(
                                    data,
                                    [endpoint1, endpoint2, endpoint3],
                                    [None, db2, db3],
                                )

    def test_endpoint_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db2 in api_test_map[endpoint2]:
                    for endpoint3 in api_test_map:
                        if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                            continue
                        for db3 in api_test_map[endpoint3]:
                            for acc3 in api_test_map[endpoint3][db3]:
                                if not settings.DEBUG:
                                    time.sleep(0.1)
                                url = "/api/{}/{}/{}/{}/{}/{}".format(endpoint1, endpoint2, db2,
                                                                      endpoint3, db3, acc3)
                                response = self._get_in_debug_mode(url)
                                data = filter_by_endpoint(self.all_docs, endpoint1)
                                data = filter_by_endpoint(data, endpoint2, db2)
                                data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                if len(data) == 0:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                     "It should be an empty response for URL {}".format(url))
                                else:
                                    self.assertEqual(
                                        response.status_code, status.HTTP_200_OK,
                                        "It should be an OK response for URL {}".format(url)
                                    )
                                    eps = [endpoint1, endpoint2, endpoint3]
                                    dbs = [None, db2, db3]
                                    accs = [None, None, acc3]
                                    expected = get_counter_payload(data, eps, dbs, accs)

                                    self.assertEqual(response.data, expected)

                                    url = "/api/{}/{}/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, acc3,
                                                                          endpoint2, db2)
                                    response = self.client.get(url)
                                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                                    self.assertEqual(response.data, expected)
                                    self.assert_db_integration_urls(data, eps, dbs, accs)
                                    self.assert_chain_urls(data, eps, dbs, accs)

    def test_endpoint_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db2 in api_test_map[endpoint2]:
                    for endpoint3 in api_test_map:
                        if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                            continue
                        for acc2 in api_test_map[endpoint2][db2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc3 in api_test_map[endpoint3][db3]:
                                    if not settings.DEBUG:
                                        time.sleep(0.1)
                                    url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                        endpoint1, endpoint2, db2, acc2, endpoint3, db3, acc3
                                    )
                                    response = self._get_in_debug_mode(url)
                                    data = filter_by_endpoint(self.all_docs, endpoint1)
                                    data = filter_by_endpoint(data, endpoint2, db2, acc2)
                                    data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                    if len(data) == 0:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                         "It should be an empty response for URL {}".format(url))
                                    else:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "It should be an OK response for URL {}".format(url))
                                        eps = [endpoint1, endpoint2, endpoint3]
                                        dbs = [None, db2, db3]
                                        accs = [None, acc2, acc3]
                                        expected = get_counter_payload(data, eps, dbs, accs)

                                        self.assertEqual(response.data, expected)

                                        url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                            endpoint1, endpoint3, db3, acc3, endpoint2, db2, acc2
                                        )
                                        response = self.client.get(url)
                                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                                        self.assertEqual(response.data, expected)
                                        self.assert_db_integration_urls(data, eps, dbs, accs)
                                        self.assert_chain_urls(data, eps, dbs, accs)

    def assertFieldsInObjectsAreEqual(self, obj1, obj2, fields):
        for f in fields:
            self.assertEqual(
                str(obj1[f]).lower(), str(obj2[f]).lower(),
                "The field {} is different in the objects: \nObj1: {} \nObj2: {}:".format(f, obj1, obj2)
            )

    def test_db_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for db1 in api_test_map[endpoint1]:
                for endpoint2 in api_test_map:
                    if endpoint1 == endpoint2:
                        continue
                    for endpoint3 in api_test_map:
                        if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                            continue
                        if not settings.DEBUG:
                            time.sleep(0.1)
                        url = "/api/{}/{}/{}/{}".format(endpoint1, db1, endpoint2, endpoint3)
                        response = self._get_in_debug_mode(url)
                        data = filter_by_endpoint(self.all_docs, endpoint1, db1)
                        data = filter_by_endpoint(data, endpoint2)
                        data = filter_by_endpoint(data, endpoint3)
                        if len(data) == 0:
                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                             "It should be an empty response for URL {}".format(url))
                        else:
                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                             "It should be an OK response for URL {}".format(url))
                            expected = get_db_payload(
                                data,
                                [endpoint1, endpoint2, endpoint3],
                                [db1, None, None]
                            )
                            self.assertEqual(len(expected), len(response.data["results"]))
                            expected.sort(key=lambda obj: str(obj["metadata"]["accession"]).lower())
                            response.data["results"].sort(key=lambda obj: str(obj["metadata"]["accession"]).lower())
                            for i in range(len(expected)):
                                obj1 = expected[i]
                                obj2 = response.data["results"][i]
                                for key in obj2:
                                    if key == "metadata":
                                        self.assertFieldsInObjectsAreEqual(
                                            obj1["metadata"], obj2["metadata"],
                                            payload_attributes[endpoint1]
                                        )
                                    else:
                                        self.assertEqual(obj1[key], obj2[key],
                                                         "the counter of {} of the {} {} doesn't match. URL: [{}]"
                                                         .format(key, endpoint1, obj1["metadata"]["accession"], url))

    def assert_obj_response_is_as_expected(self, obj_response, obj_expected, endpoint1, url):
        for key in obj_expected:
            if key == "metadata":
                self.assertFieldsInObjectsAreEqual(
                    obj_expected["metadata"], obj_response["metadata"],
                    payload_attributes[endpoint1]
                )
            else:
                if type(obj_expected[key]) == dict:
                    self.assertEqual(
                        obj_expected[key], obj_response[key],
                        "the counter of {} of the {} {} doesn't match. URL: [{}]".format(
                            key, endpoint1, obj_expected["metadata"]["accession"], url))
                else:
                    self.assertEqual(type(obj_expected[key]), list)
                    self.assertEqual(type(obj_response[key]), list)
                    self.assertEqual(len(obj_response[key]), len(obj_expected[key]), "URL: {}".format(url))
                    obj_expected[key].sort(key=lambda obj: str(obj["accession"]).lower())
                    obj_response[key].sort(key=lambda obj: str(obj["accession"]).lower())
                    for j in range(len(obj_expected[key])):
                        self.assertFieldsInObjectsAreEqual(
                            obj_expected[key][j], obj_response[key][j],
                            sublist_attributes[singular[key]]
                        )

    def assert_db_response_is_as_expected(self, response, expected, endpoint1, url):
        self.assertEqual(len(expected), len(response.data["results"]))
        expected.sort(key=lambda obj: str(obj["metadata"]["accession"]).lower())
        response.data["results"].sort(key=lambda obj: str(obj["metadata"]["accession"]).lower())
        for i in range(len(expected)):
            obj_expected = expected[i]
            obj_response = response.data["results"][i]
            self.assert_obj_response_is_as_expected(obj_expected, obj_response, endpoint1, url)

    def test_db_db_endpoint(self):
        for endpoint1 in api_test_map:
            for db1 in api_test_map[endpoint1]:
                for endpoint2 in api_test_map:
                    if endpoint1 == endpoint2:
                        continue
                    for db2 in api_test_map[endpoint2]:
                        for endpoint3 in api_test_map:
                            if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                continue
                            if not settings.DEBUG:
                                time.sleep(0.1)
                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, db1, endpoint2, db2, endpoint3)
                            response = self._get_in_debug_mode(url)
                            data = filter_by_endpoint(self.all_docs, endpoint1, db1)
                            data = filter_by_endpoint(data, endpoint2, db2)
                            data = filter_by_endpoint(data, endpoint3)
                            if len(data) == 0:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                 "It should be an empty response for URL {}".format(url))
                            else:
                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                 "It should be an OK response for URL {}".format(url))
                                expected = get_db_payload(
                                    data,
                                    [endpoint1, endpoint2, endpoint3],
                                    [db1, db2, None]
                                )
                                self.assert_db_response_is_as_expected(response, expected, endpoint1, url)

                                # test_db_endpoint_db
                                url = "/api/{}/{}/{}/{}/{}".format(endpoint1, db1, endpoint3, endpoint2, db2)
                                response = self.client.get(url)
                                self.assertEqual(response.status_code, status.HTTP_200_OK)
                                self.assert_db_response_is_as_expected(response, expected, endpoint1, url)
                                self.assert_db_integration_urls(
                                    data,
                                    [endpoint1, endpoint2, endpoint3],
                                    [db1, db2, None],
                                )

    def test_db_db_db(self):
        for endpoint1 in api_test_map:
            for db1 in api_test_map[endpoint1]:
                for endpoint2 in api_test_map:
                    if endpoint1 == endpoint2:
                        continue
                    for db2 in api_test_map[endpoint2]:
                        for endpoint3 in api_test_map:
                            if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                continue
                            for db3 in api_test_map[endpoint3]:
                                if not settings.DEBUG:
                                    time.sleep(0.1)
                                url = "/api/{}/{}/{}/{}/{}/{}".format(endpoint1, db1, endpoint2, db2, endpoint3, db3)
                                response = self._get_in_debug_mode(url)
                                data = filter_by_endpoint(self.all_docs, endpoint1, db1)
                                data = filter_by_endpoint(data, endpoint2, db2)
                                data = filter_by_endpoint(data, endpoint3, db3)
                                if len(data) == 0:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                     "It should be an empty response for URL {}".format(url))
                                else:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "It should be an OK response for URL {}".format(url))
                                    expected = get_db_payload(
                                        data,
                                        [endpoint1, endpoint2, endpoint3],
                                        [db1, db2, db3]
                                    )
                                    self.assert_db_response_is_as_expected(response, expected, endpoint1, url)
                                    self.assert_db_integration_urls(
                                        data,
                                        [endpoint1, endpoint2, endpoint3],
                                        [db1, db2, db3],
                                    )

    def test_db_db_acc(self):
        for endpoint1 in api_test_map:
            for db1 in api_test_map[endpoint1]:
                for endpoint2 in api_test_map:
                    if endpoint1 == endpoint2:
                        continue
                    for db2 in api_test_map[endpoint2]:
                        for endpoint3 in api_test_map:
                            if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                continue
                            for db3 in api_test_map[endpoint3]:
                                for acc3 in api_test_map[endpoint3][db3]:
                                    if not settings.DEBUG:
                                        time.sleep(0.1)
                                    url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                        endpoint1, db1, endpoint2, db2, endpoint3, db3, acc3)
                                    data = filter_by_endpoint(self.all_docs, endpoint1, db1)
                                    data = filter_by_endpoint(data, endpoint2, db2)
                                    data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                    response = self._get_in_debug_mode(url)
                                    if len(data) == 0:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                         "It should be an empty response for URL {}".format(url))
                                    else:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "It should be an OK response for URL {}".format(url))
                                        eps = [endpoint1, endpoint2, endpoint3]
                                        dbs = [db1, db2, db3]
                                        accs = [None, None, acc3]
                                        expected = get_db_payload(data, eps, dbs, accs)
                                        self.assert_db_response_is_as_expected(response, expected, endpoint1, url)
                                        self.assert_db_integration_urls(data, eps, dbs, accs)
                                        self.assert_chain_urls(data, eps, dbs, accs)
                                        # test_db_acc_db
                                        url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                            endpoint1, db1, endpoint3, db3, acc3, endpoint2, db2)
                                        response = self.client.get(url)
                                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                                        self.assert_db_response_is_as_expected(response, expected, endpoint1, url)

    def test_db_acc_acc(self):
        for endpoint1 in api_test_map:
            for db1 in api_test_map[endpoint1]:
                for endpoint2 in api_test_map:
                    if endpoint1 == endpoint2:
                        continue
                    for db2 in api_test_map[endpoint2]:
                        for acc2 in api_test_map[endpoint2][db2]:
                            for endpoint3 in api_test_map:
                                if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                    continue
                                for db3 in api_test_map[endpoint3]:
                                    for acc3 in api_test_map[endpoint3][db3]:
                                        if not settings.DEBUG:
                                            time.sleep(0.1)
                                        url = "/api/{}/{}/{}/{}/{}/{}/{}/{}".format(
                                            endpoint1, db1, endpoint2, db2, acc2, endpoint3, db3, acc3)
                                        response = self._get_in_debug_mode(url)
                                        data = filter_by_endpoint(self.all_docs, endpoint1, db1)
                                        data = filter_by_endpoint(data, endpoint2, db2, acc2)
                                        data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                        if len(data) == 0:
                                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                             "It should be an empty response for URL {}".format(url))
                                        else:
                                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                             "It should be an OK response for URL {}".format(url))
                                            eps = [endpoint1, endpoint2, endpoint3]
                                            dbs = [db1, db2, db3]
                                            accs = [None, acc2, acc3]
                                            expected = get_db_payload(data, eps, dbs, accs)
                                            self.assert_db_response_is_as_expected(response, expected, endpoint1, url)
                                            self.assert_db_integration_urls(data, eps, dbs, accs)
                                            self.assert_chain_urls(data, eps, dbs, accs)

    def test_acc_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for db1 in api_test_map[endpoint1]:
                for acc1 in api_test_map[endpoint1][db1]:
                    for endpoint2 in api_test_map:
                        if endpoint1 == endpoint2:
                            continue
                        for endpoint3 in api_test_map:
                            if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                continue
                            if not settings.DEBUG:
                                time.sleep(0.1)
                            url = "/api/{}/{}/{}/{}/{}".format(
                                endpoint1, db1, acc1, endpoint2, endpoint3)
                            data = filter_by_endpoint(self.all_docs, endpoint1, db1, acc1)
                            data = filter_by_endpoint(data, endpoint2)
                            data = filter_by_endpoint(data, endpoint3)
                            response = self._get_in_debug_mode(url)
                            if len(data) == 0:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                 "It should be an empty response for URL {}".format(url))
                            else:
                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                 "It should be an OK response for URL {}".format(url))
                                eps = [endpoint1, endpoint2, endpoint3]
                                dbs = [db1, None, None]
                                accs = [acc1, None, None]
                                expected = get_acc_payload(data, eps, dbs, accs)
                                self.assert_obj_response_is_as_expected(
                                    response.data, expected, endpoint1, url
                                )
                                self.assert_db_integration_urls(data, eps, dbs, accs)
                                self.assert_chain_urls(data, eps, dbs, accs)

    def test_acc_endpoint_db(self):
        for endpoint1 in tqdm(api_test_map, desc="AED - Endpoint"):
            for db1 in tqdm(api_test_map[endpoint1], desc="AED - DB"):
                for acc1 in api_test_map[endpoint1][db1]:
                    for endpoint2 in api_test_map:
                        if endpoint1 == endpoint2:
                            continue
                        for endpoint3 in api_test_map:
                            if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                continue
                            for db3 in api_test_map[endpoint3]:
                                if not settings.DEBUG:
                                    time.sleep(0.1)
                                url = "/api/{}/{}/{}/{}/{}/{}".format(
                                    endpoint1, db1, acc1, endpoint2, endpoint3, db3)
                                data = filter_by_endpoint(self.all_docs, endpoint1, db1, acc1)
                                data = filter_by_endpoint(data, endpoint2)
                                data = filter_by_endpoint(data, endpoint3, db3)
                                response = self._get_in_debug_mode(url)
                                if len(data) == 0:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                     "It should be an empty response for URL {}".format(url))
                                else:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "It should be an OK response for URL {}".format(url))
                                    eps = [endpoint1, endpoint2, endpoint3]
                                    dbs = [db1, None, db3]
                                    accs = [acc1, None, None]
                                    expected = get_acc_payload(data, eps, dbs, accs)
                                    self.assert_obj_response_is_as_expected(
                                        response.data, expected, endpoint1, url
                                    )

                                    # test_acc_db_endpoint
                                    url = "/api/{}/{}/{}/{}/{}/{}".format(
                                        endpoint1, db1, acc1, endpoint3, db3, endpoint2)
                                    response = self.client.get(url)
                                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                                    self.assert_obj_response_is_as_expected(
                                        response.data, expected, endpoint1, url
                                    )
                                    self.assert_db_integration_urls(data, eps, dbs, accs)
                                    self.assert_chain_urls(data, eps, dbs, accs)

    def test_acc_endpoint_acc(self):
        for endpoint1 in tqdm(api_test_map, desc="AEA - Endpoint"):
            for db1 in tqdm(api_test_map[endpoint1], desc="AEA - DB"):
                for acc1 in api_test_map[endpoint1][db1]:
                    for endpoint2 in api_test_map:
                        if endpoint1 == endpoint2:
                            continue
                        for endpoint3 in api_test_map:
                            if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                continue
                            for db3 in api_test_map[endpoint3]:
                                for acc3 in api_test_map[endpoint3][db3]:
                                    if not settings.DEBUG:
                                        time.sleep(0.1)
                                    url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                        endpoint1, db1, acc1, endpoint2, endpoint3, db3, acc3)
                                    data = filter_by_endpoint(self.all_docs, endpoint1, db1, acc1)
                                    data = filter_by_endpoint(data, endpoint2)
                                    data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                    response = self._get_in_debug_mode(url)
                                    if len(data) == 0:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                         "It should be an empty response for URL {}".format(url))
                                    else:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "It should be an OK response for URL {}".format(url))
                                        eps = [endpoint1, endpoint2, endpoint3]
                                        dbs = [db1, None, db3]
                                        accs = [acc1, None, acc3]
                                        expected = get_acc_payload(data, eps, dbs, accs)
                                        self.assert_obj_response_is_as_expected(
                                            response.data, expected, endpoint1, url
                                        )
                                        self.assert_db_integration_urls(data, eps, dbs, accs)
                                        self.assert_chain_urls(data, eps, dbs, accs)

                                        # test_acc_acc_endpoint
                                        url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                            endpoint1, db1, acc1, endpoint3, db3, acc3, endpoint2)
                                        response = self.client.get(url)
                                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                                        self.assert_obj_response_is_as_expected(
                                            response.data, expected, endpoint1, url
                                        )

    def test_acc_db_db(self):
        for endpoint1 in tqdm(api_test_map, desc="ADD - Endpoint"):
            for db1 in tqdm(api_test_map[endpoint1], desc="ADD - DB"):
                for acc1 in api_test_map[endpoint1][db1]:
                    for endpoint2 in api_test_map:
                        if endpoint1 == endpoint2:
                            continue
                        for db2 in api_test_map[endpoint2]:
                            for endpoint3 in api_test_map:
                                if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                    continue
                                for db3 in api_test_map[endpoint3]:
                                    if not settings.DEBUG:
                                        time.sleep(0.1)
                                    url = "/api/{}/{}/{}/{}/{}/{}/{}".format(
                                        endpoint1, db1, acc1, endpoint2, db2, endpoint3, db3)
                                    data = filter_by_endpoint(self.all_docs, endpoint1, db1, acc1)
                                    data = filter_by_endpoint(data, endpoint2, db2)
                                    data = filter_by_endpoint(data, endpoint3, db3)
                                    response = self._get_in_debug_mode(url)
                                    if len(data) == 0:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                         "It should be an empty response for URL {}".format(url))
                                    else:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "It should be an OK response for URL {}".format(url))
                                        eps = [endpoint1, endpoint2, endpoint3]
                                        dbs = [db1, db2, db3]
                                        accs = [acc1, None, None]
                                        expected = get_acc_payload(data, eps, dbs, accs)
                                        self.assert_obj_response_is_as_expected(
                                            response.data, expected, endpoint1, url
                                        )
                                        self.assert_db_integration_urls(data, eps, dbs, accs)
                                        self.assert_chain_urls(data, eps, dbs, accs)

    def test_acc_db_acc(self):
        for endpoint1 in tqdm(api_test_map, desc="ADA - Endpoint"):
            for db1 in tqdm(api_test_map[endpoint1], desc="ADA - DB"):
                for acc1 in api_test_map[endpoint1][db1]:
                    for endpoint2 in api_test_map:
                        if endpoint1 == endpoint2:
                            continue
                        for db2 in api_test_map[endpoint2]:
                            for endpoint3 in api_test_map:
                                if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                    continue
                                for db3 in api_test_map[endpoint3]:
                                    for acc3 in api_test_map[endpoint3][db3]:
                                        if not settings.DEBUG:
                                            time.sleep(0.1)
                                        url = "/api/{}/{}/{}/{}/{}/{}/{}/{}".format(
                                            endpoint1, db1, acc1, endpoint2, db2, endpoint3, db3, acc3)
                                        data = filter_by_endpoint(self.all_docs, endpoint1, db1, acc1)
                                        data = filter_by_endpoint(data, endpoint2, db2)
                                        data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                        response = self._get_in_debug_mode(url)
                                        if len(data) == 0:
                                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                             "It should be an empty response for URL {}".format(url))
                                        else:
                                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                             "It should be an OK response for URL {}".format(url))
                                            eps = [endpoint1, endpoint2, endpoint3]
                                            dbs = [db1, db2, db3]
                                            accs = [acc1, None, acc3]
                                            expected = get_acc_payload(data, eps, dbs, accs)
                                            self.assert_obj_response_is_as_expected(
                                                response.data, expected, endpoint1, url
                                            )
                                            self.assert_db_integration_urls(data, eps, dbs, accs)
                                            self.assert_chain_urls(data, eps, dbs, accs)

                                            # test_acc_acc_db
                                            url = "/api/{}/{}/{}/{}/{}/{}/{}/{}".format(
                                                endpoint1, db1, acc1, endpoint3, db3, acc3, endpoint2, db2)
                                            response = self.client.get(url)
                                            self.assertEqual(response.status_code, status.HTTP_200_OK)
                                            self.assert_obj_response_is_as_expected(
                                                response.data, expected, endpoint1, url
                                            )

    def test_acc_acc_acc(self):
        for endpoint1 in tqdm(api_test_map, desc="AAA - Endpoint"):
            for db1 in tqdm(api_test_map[endpoint1], desc="AAA - DB"):
                for acc1 in api_test_map[endpoint1][db1]:
                    for endpoint2 in api_test_map:
                        if endpoint1 == endpoint2:
                            continue
                        for db2 in api_test_map[endpoint2]:
                            for acc2 in api_test_map[endpoint2][db2]:
                                for endpoint3 in api_test_map:
                                    if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                                        continue
                                    for db3 in api_test_map[endpoint3]:
                                        for acc3 in api_test_map[endpoint3][db3]:
                                            if not settings.DEBUG:
                                                time.sleep(0.1)
                                            url = "/api/{}/{}/{}/{}/{}/{}/{}/{}/{}".format(
                                                endpoint1, db1, acc1, endpoint2, db2, acc2, endpoint3, db3, acc3)
                                            data = filter_by_endpoint(self.all_docs, endpoint1, db1, acc1)
                                            data = filter_by_endpoint(data, endpoint2, db2, acc2)
                                            data = filter_by_endpoint(data, endpoint3, db3, acc3)
                                            response = self._get_in_debug_mode(url)
                                            if len(data) == 0:
                                                self.assertEqual(
                                                    response.status_code, status.HTTP_204_NO_CONTENT,
                                                    "It should be an empty response for URL {}".format(url)
                                                )
                                            else:
                                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                                 "It should be an OK response for URL {}".format(url))
                                                eps = [endpoint1, endpoint2, endpoint3]
                                                dbs = [db1, db2, db3]
                                                accs = [acc1, acc2, acc3]
                                                expected = get_acc_payload(data, eps, dbs, accs)
                                                self.assert_obj_response_is_as_expected(
                                                    response.data, expected, endpoint1, url
                                                )
                                                self.assert_db_integration_urls(data, eps, dbs, accs)
                                                self.assert_chain_urls(data, eps, dbs, accs)

