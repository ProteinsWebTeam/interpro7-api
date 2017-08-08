from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase

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
        "prosite_profiles": [
            "PS50822",
            "PS01031",
        ],
        "interpro/pfam": [
            "PF02171",
        ],
        "interpro/smart": [
            "SM00950",
        ],
        "interpro/prosite_profiles": [
            "PS50822",
        ],
        "unintegrated/pfam": [
            "PF17180",
            "PF17176",
        ],
        "unintegrated/smart": [
            "SM00002",
        ],
        "unintegrated/prosite_profiles": [
            "PS01031",
        ],
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
}
plurals = {
    "entry": "entries",
    "protein": "proteins",
    "structure": "structures",
}

# TODO: Crete tests for entry/unintegrated


import unittest

class ObjectStructureTwoEndpointsTest(InterproRESTTestCase):

    def test_endpoints_independently(self):
        for endpoint in api_test_map:
            response = self.client.get("/api/"+endpoint)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_counter_by_endpoint(endpoint, response.data)

            for db in api_test_map[endpoint]:
                response_db = self.client.get("/api/"+endpoint+"/"+db)
                self.assertEqual(response_db.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response_db.data["results"]), len(api_test_map[endpoint][db]))
                self._check_is_list_of_metadata_objects(response_db.data["results"], "metadata")

                for acc in api_test_map[endpoint][db]:
                    current = "/api/"+endpoint+"/"+db+"/"+acc
                    response_acc = self.client.get(current)
                    self.assertEqual(response_acc.status_code, status.HTTP_200_OK)
                    self._check_object_by_accesssion(response_acc.data)

                    self._check_structure_and_chains(response_acc, endpoint, db, acc)

    def test_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue

                # [endpoint]/[endpoint]
                current = "/api/"+endpoint1+"/"+endpoint2
                response = self.client.get(current)
                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                self._check_counter_by_endpoint(endpoint1, response.data, "URL : [{}]".format(current))
                self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))

    def test_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    # [endpoint]/[db]/[endpoint]
                    current = "/api/"+endpoint1+"/"+db+"/"+endpoint2
                    response = self._get_in_debug_mode(current)
                    if response.status_code == status.HTTP_200_OK:
                        self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                        self._check_is_list_of_metadata_objects(response.data["results"], "URL : [{}]".format(current))
                        self._check_is_list_of_objects_with_key(response.data["results"],
                                                                plurals[endpoint2],
                                                                "URL : [{}]".format(current))
                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    # [endpoint]/[endpoint]/[db]
                    current = "/api/"+endpoint2+"/"+endpoint1+"/"+db+"/"
                    response = self._get_in_debug_mode(current)
                    if response.status_code == status.HTTP_200_OK:
                        self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                        self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                        self._check_count_overview_per_endpoints(response.data,
                                                                 plurals[endpoint1],
                                                                 plurals[endpoint2],
                                                                 "URL : [{}]".format(current))
                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                        self.fail("Unexpeted error code {} for the URL : [{}]".format(response.status_code, current))

    def test_acc_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for acc in api_test_map[endpoint1][db]:
                        # [endpoint]/[db]/[acc]/[endpoint]
                        current = "/api/"+endpoint1+"/"+db+"/"+acc+"/"+endpoint2
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                            self._check_object_by_accesssion(response.data, "URL : [{}]".format(current))
                            self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                            self._check_structure_and_chains(response, endpoint1, db, acc, "/"+endpoint2)
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for acc in api_test_map[endpoint1][db]:
                        # [endpoint]/[endpoint]/[db]/[acc]
                        current = "/api/"+endpoint2+"/"+endpoint1+"/"+db+"/"+acc+"/"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                            self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                            # self._check_count_overview_per_endpoints(response.data,
                            #                                          plurals[endpoint1],
                            #                                          plurals[endpoint2],
                            #                                          "URL : [{}]".format(current))
                            self._check_structure_chains_as_counter_filter(endpoint1, db, acc, endpoint2, "",
                                                                           plurals[endpoint1], plurals[endpoint2])
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.fail("ONLY 204 Errors are expected")

    def test_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    # [endpoint]/[db]/[endpoint]/[db]
                    for db2 in api_test_map[endpoint2]:
                        current = "/api/"+endpoint1+"/"+db+"/"+endpoint2+"/"+db2
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self._check_is_list_of_metadata_objects(response.data["results"],
                                                                    "URL : [{}]".format(current))
                            self._check_is_list_of_objects_with_key(response.data["results"],
                                                                    plurals[endpoint2],
                                                                    "URL : [{}]".format(current))
                            for result in [x[plurals[endpoint2]] for x in response.data["results"]]:
                                self._check_list_of_matches(result, "URL : [{}]".format(current))

                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for db2 in api_test_map[endpoint2]:
                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[endpoint]/[db]/[acc]
                            current = "/api/"+endpoint2+"/"+db2+"/"+endpoint1+"/"+db+"/"+acc
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                 "URL : [{}]".format(current))
                                self._check_is_list_of_metadata_objects(response.data["results"])
                                for result in [x[plurals[endpoint1]] for x in response.data["results"]]:
                                    self._check_list_of_matches(result, "URL : [{}]".format(current))
                                self._check_structure_chains_as_filter(endpoint1, db, acc,
                                                                       endpoint2+"/"+db2, "",
                                                                       plurals[endpoint1])
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                 "URL : [{}]".format(current))

    def test_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for db2 in api_test_map[endpoint2]:
                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[db]
                            current = "/api/"+endpoint1+"/"+db+"/"+acc+"/"+endpoint2+"/"+db2
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                 "URL : [{}]".format(current))
                                self._check_object_by_accesssion(response.data,
                                                                 "URL : [{}]".format(current))
                                self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                            "URL : [{}]".format(current))
                                self._check_structure_and_chains(response, endpoint1, db, acc,
                                                                 "/"+endpoint2+"/"+db2, plurals[endpoint2])
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for db2 in api_test_map[endpoint2]:
                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                            for acc2 in api_test_map[endpoint2][db2]:
                                current = "/api/"+endpoint1+"/"+db+"/"+acc+"/"+endpoint2+"/"+db2+"/"+acc2
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "URL : [{}]".format(current))
                                    self._check_object_by_accesssion(response.data)
                                    self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                "URL : [{}]".format(current))
                                    self._check_structure_and_chains(response, endpoint1, db, acc,
                                                                     "/"+endpoint2+"/"+db2+"/"+acc2, plurals[endpoint2])
                                    self._check_structure_chains_as_filter(endpoint2, db2, acc2,
                                                                           endpoint1+"/"+db+"/"+acc, "",
                                                                           plurals[endpoint2])
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ObjectStructureThreeEndpointsTest(InterproRESTTestCase):
    def test_endpoint_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue

                    # [endpoint]/[endpoint]
                    current = "/api/"+endpoint1+"/"+endpoint2+"/"+endpoint3
                    response = self.client.get(current)
                    self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                    self._check_counter_by_endpoint(endpoint1, response.data, "URL : [{}]".format(current))
                    self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                    self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))

    def test_endpoint_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[endpoint]/[db]/[endpoint]
                        current = "/api/"+endpoint2+"/"+endpoint1+"/"+db1+"/"+endpoint3
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                            self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                            self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                            # self._check_count_overview_per_endpoints(response.data,
                            #                                          plurals[endpoint1],
                            #                                          plurals[endpoint2],
                            #                                          "URL : [{}]".format(current))
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[db]/[endpoint]/[endpoint]
                        current = "/api/"+endpoint1+"/"+db1+"/"+endpoint2+"/"+endpoint3
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                            self._check_is_list_of_metadata_objects(response.data["results"],
                                                                    "URL : [{}]".format(current))
                            self._check_is_list_of_objects_with_key(response.data["results"],
                                                                    plurals[endpoint2],
                                                                    "URL : [{}]".format(current))
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_endpoint_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for acc in api_test_map[endpoint1][db1]:
                            # [endpoint]/[endpoint]/[endpoint]/[db]/[acc]
                            current = "/api/"+endpoint2+"/"+endpoint3+"/"+endpoint1+"/"+db1+"/"+acc+"/"
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                # self._check_count_overview_per_endpoints(response.data,
                                #                                          plurals[endpoint1],
                                #                                          plurals[endpoint2],
                                #                                          "URL : [{}]".format(current))
                                self._check_structure_chains_as_counter_filter(endpoint1, db1, acc,
                                                                               endpoint2+"/"+endpoint3, "",
                                                                               plurals[endpoint1],
                                                                               plurals[endpoint2])
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail("The response for [{}] had an HTTP error differen to 204".format(current))

    def test_endpoint_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                            # [endpoint]/[endpoint]/[endpoint]/[db]
                            current = "/api/"+endpoint2+"/"+endpoint3+"/"+endpoint1+"/"+db1+"/"
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                self._check_count_overview_per_endpoints(response.data,
                                                                         plurals[endpoint1],
                                                                         plurals[endpoint2],
                                                                         "URL : [{}]".format(current))
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail("The response for [{}] had an HTTP error differen to 204".format(current))

    def test_endpoint_acc_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for acc in api_test_map[endpoint1][db1]:
                            # [endpoint]/[endpoint]/[db]/[acc]/[endpoint]
                            current = "/api/"+endpoint2+"/"+endpoint1+"/"+db1+"/"+acc+"/"+"/"+endpoint3
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                # self._check_count_overview_per_endpoints(response.data,
                                #                                          plurals[endpoint1],
                                #                                          plurals[endpoint2],
                                #                                          "URL : [{}]".format(current))
                                self._check_structure_chains_as_counter_filter(endpoint1, db1, acc, endpoint2,
                                                                               "/"+endpoint3, plurals[endpoint1],
                                                                               plurals[endpoint2])
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail("The response for [{}] had an HTTP error differen to 204".format(current))

    def test_acc_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for acc in api_test_map[endpoint1][db1]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[endpoint]
                            current = "/api/"+endpoint1+"/"+db1+"/"+acc+"/"+endpoint2+"/"+endpoint3
                            response = self._get_in_debug_mode(current)

                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                self._check_object_by_accesssion(response.data, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint2, response.data, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                self._check_structure_and_chains(response, endpoint1, db1, acc,
                                                                 "/"+endpoint2+"/"+endpoint3)
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[db]/[endpoint]/[db]/[endpoint]
                        for db2 in api_test_map[endpoint2]:
                            current = "/api/"+endpoint1+"/"+db1+"/"+endpoint2+"/"+db2+"/"+endpoint3
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self._check_is_list_of_metadata_objects(response.data["results"],
                                                                        "URL : [{}]".format(current))
                                self._check_is_list_of_objects_with_key(response.data["results"],
                                                                        plurals[endpoint2],
                                                                        "URL : [{}]".format(current))
                                for result in [x[plurals[endpoint2]] for x in response.data["results"]]:
                                    self._check_list_of_matches(result, "URL : [{}]".format(current))
                                self._check_is_list_of_objects_with_key(response.data["results"],
                                                                        plurals[endpoint3],
                                                                        "URL : [{}]".format(current))
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            # [endpoint]/[db]/[endpoint]/[endpoint]/[db]
                            current = "/api/"+endpoint1+"/"+db1+"/"+endpoint3+"/"+endpoint2+"/"+db2
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self._check_is_list_of_metadata_objects(response.data["results"],
                                                                        "URL : [{}]".format(current))
                                self._check_is_list_of_objects_with_key(response.data["results"],
                                                                        plurals[endpoint2],
                                                                        "URL : [{}]".format(current))
                                for result in [x[plurals[endpoint2]] for x in response.data["results"]]:
                                    self._check_list_of_matches(result, "URL : [{}]".format(current))
                                self._check_is_list_of_objects_with_key(response.data["results"],
                                                                        plurals[endpoint3],
                                                                        "URL : [{}]".format(current))
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_endpoint_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            # [endpoint]/[endpoint]/[db]/[endpoint]/[db]
                            current = "/api/"+endpoint3+"/"+endpoint2+"/"+db2+"/"+endpoint1+"/"+db1
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                self._check_count_overview_per_endpoints(response.data,
                                                                         plurals[endpoint2],
                                                                         plurals[endpoint3],
                                                                         "URL : [{}]".format(current))
                                self._check_count_overview_per_endpoints(response.data,
                                                                         plurals[endpoint1],
                                                                         plurals[endpoint3],
                                                                         "URL : [{}]".format(current))
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail("The response for [{}] had an HTTP error differen to 204".format(current))

    def test_acc_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # [endpoint]/[db]/[acc]/[endpoint]/[db]/[endpoint]
                                current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"+endpoint2+"/"+db2+"/"+endpoint3
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "URL : [{}]".format(current))
                                    self._check_object_by_accesssion(response.data,
                                                                     "URL : [{}]".format(current))
                                    self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                "URL : [{}]".format(current))
                                    self._check_counter_by_endpoint(endpoint3, response.data,
                                                                    "URL : [{}]".format(current))
                                    self._check_structure_and_chains(response, endpoint1, db1, acc1,
                                                                     "/"+endpoint2+"/"+db2+"/"+endpoint3)
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_acc_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # [endpoint]/[db]/[acc]/[endpoint]/[endpoint]/[db]
                                current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"+endpoint3+"/"+endpoint2+"/"+db2
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "URL : [{}]".format(current))
                                    self._check_object_by_accesssion(response.data, "URL : [{}]".format(current))
                                    self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                "URL : [{}]".format(current))
                                    self._check_counter_by_endpoint(endpoint3, response.data,
                                                                    "URL : [{}]".format(current))
                                    self._check_structure_and_chains(response, endpoint1, db1, acc1,
                                                                     "/"+endpoint3+"/"+endpoint2+"/"+db2)
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_acc_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[db]/[endpoint]/[db]/[acc]/[endpoint]
                                current = "/api/"+endpoint2+"/"+db2+"/"+endpoint1+"/"+db1+"/"+acc1+"/"+endpoint3
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "URL : [{}]".format(current))
                                    self._check_is_list_of_metadata_objects(response.data["results"])
                                    for result in [x[plurals[endpoint1]] for x in response.data["results"]]:
                                        self._check_list_of_matches(result, "URL : [{}]".format(current))
                                    self._check_is_list_of_objects_with_key(response.data["results"],
                                                                            plurals[endpoint3],
                                                                            "URL : [{}]".format(current))
                                    self._check_structure_chains_as_filter(endpoint1, db1, acc1,
                                                                           endpoint2+"/"+db2, "/"+endpoint3,
                                                                           plurals[endpoint1])
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[db]/[endpoint]/[endpoint]/[db]/[acc]
                                current = "/api/"+endpoint2+"/"+db2+"/"+endpoint3+"/"+endpoint1+"/"+db1+"/"+acc1
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                     "URL : [{}]".format(current))
                                    self._check_is_list_of_metadata_objects(response.data["results"])
                                    for result in [x[plurals[endpoint1]] for x in response.data["results"]]:
                                        self._check_list_of_matches(result, "URL : [{}]".format(current))
                                    self._check_is_list_of_objects_with_key(response.data["results"],
                                                                            plurals[endpoint3],
                                                                            "URL : [{}]".format(current))
                                    self._check_structure_chains_as_filter(endpoint1, db1, acc1,
                                                                           endpoint2+"/"+db2+"/"+endpoint3,
                                                                           "", plurals[endpoint1])
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_endpoint_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[endpoint]/[db]/[endpoint]/[db]/[acc]
                                current = "/api/"+endpoint3+"/"+endpoint2+"/"+db2+"/"+endpoint1+"/"+db1+"/"+acc1
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                    self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                    self._check_count_overview_per_endpoints(response.data,
                                                                             plurals[endpoint2],
                                                                             plurals[endpoint3],
                                                                             "URL : [{}]".format(current))
                                    # self._check_count_overview_per_endpoints(response.data,
                                    #                                          plurals[endpoint1],
                                    #                                          plurals[endpoint3],
                                    #                                          "URL : [{}]".format(current))

                                    self._check_structure_chains_as_counter_filter(
                                        endpoint1, db1, acc1,
                                        endpoint3+"/"+endpoint2+"/"+db2+"/", "",
                                        plurals[endpoint1],
                                        plurals[endpoint3])
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.fail("The response for [{}] had an HTTP error differen to 204".format(current))

    def test_endpoint_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[endpoint]/[db]/[acc]/[endpoint]/[db]
                                current = "/api/"+endpoint3+"/"+endpoint1+"/"+db1+"/"+acc1+"/"+endpoint2+"/"+db2
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                                    self._check_counter_by_endpoint(endpoint3, response.data, "URL : [{}]".format(current))
                                    self._check_count_overview_per_endpoints(response.data,
                                                                             plurals[endpoint2],
                                                                             plurals[endpoint3],
                                                                             "URL : [{}]".format(current))
                                    # self._check_count_overview_per_endpoints(response.data,
                                    #                                          plurals[endpoint1],
                                    #                                          plurals[endpoint3],
                                    #                                          "URL : [{}]".format(current))

                                    self._check_structure_chains_as_counter_filter(
                                        endpoint1, db1, acc1,
                                        endpoint3, "/"+endpoint2+"/"+db2,
                                        plurals[endpoint1],
                                        plurals[endpoint3])
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.fail("Unexpeted error code {} for the URL : [{}]".format(response.status_code, current))

    def test_acc_acc_endpoint(self):
        tested = []
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                for acc2 in api_test_map[endpoint2][db2]:
                                    # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]/[endpoint]
                                    current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"\
                                              + endpoint2+"/"+db2+"/"+acc2+"/"+endpoint3
                                    tested.append(current)
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "URL : [{}]".format(current))
                                        self._check_object_by_accesssion(response.data)
                                        self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                    "URL : [{}]".format(current))
                                        self._check_counter_by_endpoint(endpoint3, response.data,
                                                                        "URL : [{}]".format(current))

                                        tested += self._check_structure_and_chains(
                                            response, endpoint1, db1, acc1,
                                            "/"+endpoint2+"/"+db2+"/"+acc2+"/"+endpoint3)

                                        tested += self._check_structure_chains_as_filter(
                                            endpoint2, db2, acc2, endpoint1+"/"+db1+"/"+acc1, "/"+endpoint3)

                                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_acc_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                for acc2 in api_test_map[endpoint2][db2]:
                                    # [endpoint]/[db]/[acc]/[endpoint]/[endpoint]/[db]/[acc]
                                    current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"\
                                              + endpoint3+"/"+endpoint2+"/"+db2+"/"+acc2
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "URL : [{}]".format(current))
                                        self._check_object_by_accesssion(response.data)
                                        self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                    "URL : [{}]".format(current))
                                        self._check_counter_by_endpoint(endpoint3, response.data,
                                                                        "URL : [{}]".format(current))

                                        self._check_structure_and_chains(
                                            response, endpoint1, db1, acc1,
                                            "/"+endpoint3+"/"+endpoint2+"/"+db2+"/"+acc2)

                                        self._check_structure_chains_as_filter(
                                            endpoint2, db2, acc2, endpoint1+"/"+db1+"/"+acc1+"/"+endpoint3, "")
                                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_endpoint_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                for acc2 in api_test_map[endpoint2][db2]:
                                    # /[endpoint]/[endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                                    current = "/api/"+endpoint3+"/"+endpoint1+"/"+db1+"/"+acc1+"/"\
                                              + endpoint2+"/"+db2+"/"+acc2
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "URL : [{}]".format(current))
                                        self._check_counter_by_endpoint(endpoint3, response.data,
                                                                        "URL : [{}]".format(current))
                                        # self._check_count_overview_per_endpoints(response.data,
                                        #                                          plurals[endpoint2],
                                        #                                          plurals[endpoint3],
                                        #                                          "URL : [{}]".format(current))
                                        # self._check_count_overview_per_endpoints(response.data,
                                        #                                          plurals[endpoint1],
                                        #                                          plurals[endpoint3],
                                        #                                          "URL : [{}]".format(current))
                                        self._check_structure_chains_as_counter_filter(
                                            endpoint1, db1, acc1,
                                            endpoint3, "/"+endpoint2+"/"+db2+"/"+acc2,
                                            plurals[endpoint1],
                                            plurals[endpoint3])
                                        self._check_structure_chains_as_counter_filter(
                                            endpoint2, db2, acc2,
                                            endpoint3+"/"+endpoint1+"/"+db1+"/"+acc1, "",
                                            plurals[endpoint2],
                                            plurals[endpoint3])
                                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                                        self.fail("Unexpeted error code {} for the URL : [{}]".format(response.status_code, current))

    def test_db_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                current = "/api/"+endpoint1+"/"+db1\
                                          + "/"+endpoint2+"/"+db2+"/"+endpoint3+"/"+db3
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self._check_is_list_of_metadata_objects(response.data["results"],
                                                                            "URL : [{}]".format(current))
                                    self._check_is_list_of_objects_with_key(response.data["results"],
                                                                            plurals[endpoint2],
                                                                            "URL : [{}]".format(current))
                                    for result in [x[plurals[endpoint2]] for x in response.data["results"]]:
                                        self._check_list_of_matches(result, "URL : [{}]".format(current))
                                    self._check_is_list_of_objects_with_key(response.data["results"],
                                                                            plurals[endpoint3],
                                                                            "URL : [{}]".format(current))
                                    for result in [x[plurals[endpoint3]] for x in response.data["results"]]:
                                        self._check_list_of_matches(result, "URL : [{}]".format(current))
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                                                     "URL : [{}]".format(current))

    def test_acc_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    # [endpoint]/[db]/[acc]/[endpoint]/[db]/[endpoint]/[db]
                                    current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"\
                                              + endpoint2+"/"+db2+"/"+endpoint3+"/"+db3
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "URL : [{}]".format(current))
                                        self._check_object_by_accesssion(response.data,
                                                                         "URL : [{}]".format(current))
                                        self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                    "URL : [{}]".format(current))
                                        self._check_list_of_matches(response.data[plurals[endpoint3]],
                                                                    "URL : [{}]".format(current))
                                        self._check_structure_and_chains(
                                            response, endpoint1, db1, acc1,
                                            "/"+endpoint2+"/"+db2+"/"+endpoint3+"/"+db3)
                                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    # /[endpoint]/[db]/[endpoint]/[db]/[acc]/[endpoint]/[db]
                                    current = "/api/"+endpoint2+"/"+db2+"/"\
                                              + endpoint1+"/"+db1+"/"+acc1+"/"+endpoint3+"/"+db3
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "URL : [{}]".format(current))
                                        self._check_is_list_of_metadata_objects(response.data["results"])
                                        for result in [x[plurals[endpoint1]] for x in response.data["results"]]:
                                            self._check_list_of_matches(result, "URL : [{}]".format(current))
                                        for result in [x[plurals[endpoint3]] for x in response.data["results"]]:
                                            self._check_list_of_matches(result, "URL : [{}]".format(current))

                                        self._check_structure_chains_as_filter(
                                            endpoint1, db1, acc1, endpoint2+"/"+db2, "/"+endpoint3+"/"+db3,
                                            plurals[endpoint1])
                                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    # /[endpoint]/[db]/[endpoint]/[db]/[endpoint]/[db]/[acc]
                                    current = "/api/"+endpoint2+"/"+db2+"/"\
                                              + endpoint3+"/"+db3+"/"+endpoint1+"/"+db1+"/"+acc1
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                         "URL : [{}]".format(current))
                                        self._check_is_list_of_metadata_objects(response.data["results"])
                                        for result in [x[plurals[endpoint1]] for x in response.data["results"]]:
                                            self._check_list_of_matches(result,
                                                                        "URL : [{}]".format(current))
                                        for result in [x[plurals[endpoint3]] for x in response.data["results"]]:
                                            self._check_list_of_matches(result,
                                                                        "URL : [{}]".format(current))
                                        self._check_structure_chains_as_filter(
                                            endpoint1, db1, acc1, endpoint2+"/"+db2+"/"+endpoint3+"/"+db3, "",
                                            plurals[endpoint1])

                                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                                        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_acc_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]/[endpoint]/[db]
                                        current = "/api/"+endpoint1+"/"+db1+"/"+acc1\
                                                  + "/"+endpoint2+"/"+db2+"/"+acc2+"/"+endpoint3+"/"+db3
                                        response = self._get_in_debug_mode(current)
                                        if response.status_code == status.HTTP_200_OK:
                                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                             "URL : [{}]".format(current))
                                            self._check_object_by_accesssion(response.data)
                                            self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                        "URL : [{}]".format(current))
                                            self._check_list_of_matches(response.data[plurals[endpoint3]],
                                                                        "URL : [{}]".format(current))
                                            self._check_structure_and_chains(
                                                response, endpoint1, db1, acc1,
                                                "/"+endpoint2+"/"+db2+"/"+acc2+"/"+endpoint3+"/"+db3)
                                            self._check_structure_chains_as_filter(
                                                endpoint2, db2, acc2, endpoint1+"/"+db1+"/"+acc1, "/"+endpoint3+"/"+db3,
                                                plurals[endpoint2])
                                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_acc_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[endpoint]/[db]/[acc]
                                        current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"\
                                                  + endpoint3+"/"+db3+"/"+endpoint2+"/"+db2+"/"+acc2
                                        response = self._get_in_debug_mode(current)
                                        if response.status_code == status.HTTP_200_OK:
                                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                             "URL : [{}]".format(current))
                                            self._check_object_by_accesssion(response.data)
                                            self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                        "URL : [{}]".format(current))
                                            self._check_list_of_matches(response.data[plurals[endpoint3]],
                                                                        "URL : [{}]".format(current))
                                            self._check_structure_and_chains(
                                                response, endpoint1, db1, acc1,
                                                "/"+endpoint3+"/"+db3+"/"+endpoint2+"/"+db2+"/"+acc2)
                                            self._check_structure_chains_as_filter(
                                                endpoint2, db2, acc2,
                                                endpoint1+"/"+db1+"/"+acc1+"/"+endpoint3+"/"+db3, "",
                                                plurals[endpoint2])
                                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_db_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                                        current = "/api/"+endpoint3+"/"+db3+"/"\
                                                  + endpoint1+"/"+db1+"/"+acc1+"/"+endpoint2+"/"+db2+"/"+acc2
                                        response = self._get_in_debug_mode(current)
                                        if response.status_code == status.HTTP_200_OK:
                                            self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                             "URL : [{}]".format(current))
                                            self._check_is_list_of_metadata_objects(response.data["results"])
                                            for result in [x[plurals[endpoint1]] for x in response.data["results"]]:
                                                self._check_list_of_matches(result, "URL : [{}]".format(current))
                                            for result in [x[plurals[endpoint2]] for x in response.data["results"]]:
                                                self._check_list_of_matches(result, "URL : [{}]".format(current))
                                            self._check_structure_chains_as_filter(
                                                endpoint1, db1, acc1, endpoint3+"/"+db3, "/"+endpoint2+"/"+db2+"/"+acc2,
                                                plurals[endpoint1])
                                            self._check_structure_chains_as_filter(
                                                endpoint2, db2, acc2,
                                                endpoint3+"/"+db3+"/"+endpoint1+"/"+db1+"/"+acc1, "",
                                                plurals[endpoint2])
                                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                                            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_acc_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                                        for acc3 in api_test_map[endpoint3][db3]:
                                            current = "/api/"+endpoint1+"/"+db1+"/"+acc1+"/"\
                                                      + endpoint2+"/"+db2+"/"+acc2+"/"+endpoint3+"/"+db3+"/"+acc3
                                            response = self._get_in_debug_mode(current)
                                            if response.status_code == status.HTTP_200_OK:
                                                self.assertEqual(response.status_code, status.HTTP_200_OK,
                                                                 "URL : [{}]".format(current))
                                                self._check_object_by_accesssion(response.data)
                                                self._check_list_of_matches(response.data[plurals[endpoint2]],
                                                                            "URL : [{}]".format(current))
                                                self._check_list_of_matches(response.data[plurals[endpoint3]],
                                                                            "URL : [{}]".format(current))
                                                self._check_structure_and_chains(
                                                    response, endpoint1, db1, acc1,
                                                    "/"+endpoint2+"/"+db2+"/"+acc2+"/"+endpoint3+"/"+db3+"/"+acc3)
                                                self._check_structure_chains_as_filter(
                                                    endpoint2, db2, acc2, endpoint1+"/"+db1+"/"+acc1,
                                                    "/"+endpoint3+"/"+db3+"/"+acc3,
                                                    plurals[endpoint2])
                                                self._check_structure_chains_as_filter(
                                                    endpoint3, db3, acc3,
                                                    endpoint1+"/"+db1+"/"+acc1+"/"+endpoint2+"/"+db2+"/"+acc2, "",
                                                    plurals[endpoint3])
                                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
