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
        "unintegrated": [
            "PF17180",
            "PF17176",
            "SM00002",
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
        "swissprot": [
            "A1CUJ5",
            "M5ADK6",
        ],
        "trembl": [
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
rel_aux = {
    ("protein", "structure"): [
        ["A1CUJ5", "1JM7"],
        ["M5ADK6", "2BKM"],
        ["M5ADK6", "1JM7"],
        ["A0A0A2L2G2", "1JZ8"],
        ["A0A0A2L2G2", "2BKM"],
        ["P16582", "1T2V"],
    ],
    ("entry", "protein"): [
        ["IPR003165", "A1CUJ5"],
        ["IPR003165", "P16582"],
        ["IPR001165", "A1CUJ5"],
        ["PF02171", "A1CUJ5"],
        ["PF17180", "M5ADK6"],
        ["PF17176", "A1CUJ5"],
        ["SM00950", "A1CUJ5"],
        ["PS50822", "P16582"],
    ],
    ("entry", "structure"): [
        ["IPR003165", "1JM7"],
        ["IPR003165", "1T2V"],
        ["IPR001165", "1JM7"],
        ["PF02171", "1JM7"],
        ["PF17180", "2BKM"],
        ["PF17180", "1JM7"],
        ["PF17176", "1JM7"],
        ["PS50822", "1T2V"],
        ["SM00950", "1JM7"],
    ]
}
relationships = {}
for e1, e2 in rel_aux:
    relationships[(e1, e2)] = rel_aux[(e1, e2)]
    relationships[(e2, e1)] = [[y, x] for x, y in relationships[(e1, e2)]]

plurals = {
    "entry": "entries",
    "protein": "proteins",
    "structure": "structures",
}
singular = {v: k for k, v in plurals.items()}


class ThreeEndpointsContentTest(InterproRESTTestCase):

    def test_endpoint_endpoint_endpoint(self):
        response1 = self.client.get("/api/entry/protein/structure")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response1.data)
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                        continue
                    url = "/api/{}/{}/{}".format(endpoint1, endpoint2, endpoint3)
                    response2 = self.client.get(url)
                    self.assertEqual(response2.status_code, status.HTTP_200_OK)
                    self.assertEqual(response1.data, response2.data)

    def test_endpoint_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint1 == endpoint3 or endpoint2 == endpoint3:
                        continue
                    for db3 in api_test_map[endpoint3]:
                        url = "/api/{}/{}/{}/{}".format(endpoint1, endpoint2, endpoint3, db3)
                        # print(url)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                        expected = self.get_expected_payload(endpoint1, endpoint2, endpoint3, db3)
                        self.assertEqual(response.data, expected)

                        url = "/api/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, endpoint2)
                        # print(url)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                        self.assertEqual(response.data, expected)

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
                            unintegrated = {"PF":"/pfam", "SM":"/smart", "PS":"/prosite_profiles", }[acc3[:2]] if db3 == "unintegrated" else ""
                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint2, endpoint3, db3+unintegrated, acc3)
                            response = self.client.get(url)
                            self.assertEqual(response.status_code, status.HTTP_200_OK)
                            expected = self.get_expected_payload(endpoint1, endpoint2, endpoint3, db3, acc3=acc3)
                            self.assertEqual(response.data, expected)

                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint3, db3+unintegrated, acc3, endpoint2)
                            response = self.client.get(url)
                            self.assertEqual(response.status_code, status.HTTP_200_OK)
                            self.assertEqual(response.data, expected)

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
                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint2, db2, endpoint3, db3)
                            # print(url)
                            response = self.client.get(url)
                            self.assertEqual(response.status_code, status.HTTP_200_OK)
                            expected = self.get_expected_payload(endpoint1, endpoint2, endpoint3, db3, db2=db2)
                            self.assertEqual(response.data, expected)

                            url = "/api/{}/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, endpoint2, db2)
                            # print(url)
                            response = self.client.get(url)
                            self.assertEqual(response.status_code, status.HTTP_200_OK)
                            self.assertEqual(response.data, expected)

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
                            if db3 == "unintegrated":
                                continue
                            #     TODO: Make a plan to test unintegrated IDs
                            for acc3 in api_test_map[endpoint3][db3]:
                                url = "/api/{}/{}/{}/{}/{}/{}".format(endpoint1, endpoint2, db2, endpoint3, db3, acc3)
                                response = self.client.get(url)
                                self.assertEqual(response.status_code, status.HTTP_200_OK)
                                expected = self.get_expected_payload(endpoint1, endpoint2, endpoint3, db3, db2=db2, acc3=acc3)
                                self.assertEqual(response.data, expected)

                                url = "/api/{}/{}/{}/{}/{}/{}".format(endpoint1, endpoint3, db3, acc3, endpoint2, db2)
                                response = self.client.get(url)
                                self.assertEqual(response.status_code, status.HTTP_200_OK)
                                self.assertEqual(response.data, expected)

    def get_expected_payload(self, endpoint1, endpoint2, endpoint3, db3, db2=None, acc3=None):
        payload = {}
        accs3 = api_test_map[endpoint3][db3]
        if acc3 in accs3:
            accs3 = [acc3]
        accs2 = api_test_map[endpoint2][db2] if db2 is not None else None

        for ep in api_test_map:
            eps = plurals[ep]
            if eps == plurals[endpoint1] or (db2 is None and eps == plurals[endpoint2]):
                payload[eps] = {}
                for db in api_test_map[ep]:
                    accs = api_test_map[ep][db]
                    if ep != "entry" or db == "interpro" or db == "unintegrated":
                        obj = payload[eps]
                    else:
                        if "member_databases" not in payload[eps]:
                            payload[eps]["member_databases"] = {}
                        obj = payload[eps]["member_databases"]
                    obj[db] = {
                        plurals[endpoint3]: len(self.get_set_of_shared_ids(ep, db, accs, endpoint3, db3, accs3, endpoint2, db2, accs2)),
                        eps: len(self.get_set_of_shared_ids(endpoint3, db3, accs3, ep, db, accs, endpoint2, db2, accs2)),
                    }
                    if db2 is not None:
                        obj[db][plurals[endpoint2]] = len(self.get_set_of_shared_ids(ep, db, accs, endpoint2, db2, accs2, endpoint3, db3, accs3 ))
        return payload

    def get_set_of_shared_ids(self, endpoint1, db1, accs1, endpoint2, db2, accs2, endpoint3=None, db3=None, accs3=None):
        shared_ids = set([x[1]
                         for x in relationships[endpoint1, endpoint2]
                         if x[0] in accs1 and x[1] in accs2])
        if db3 is not None:
            link_ids = set([x[1]
                            for x in relationships[endpoint1, endpoint3]
                            if x[0] in accs1 and x[1] in accs3])
            return set([x[1]
                       for x in relationships[endpoint3, endpoint2]
                       if x[0] in accs3 and x[1] in accs2 and x[0] in link_ids and x[1] in shared_ids])

        return shared_ids


