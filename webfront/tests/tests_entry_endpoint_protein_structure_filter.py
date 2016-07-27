from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
import logging

structure_urls = [
    "structure/",
    "structure/pdb/",
    "structure/pdb/1JM7",
]

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
endpoint_plurals = {
    "entry": "entries",
    "protein": "proteins",
    "structure": "structures",
}
# TODO: Create tests for Chains in structure
# TODO: Crete tests for entry/unintegrated


class ObjectStructureTest(InterproRESTTestCase):

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
                    response_acc = self.client.get("/api/"+endpoint+"/"+db+"/"+acc)
                    self.assertEqual(response_acc.status_code, status.HTTP_200_OK)
                    self._check_object_by_accesssion(response_acc.data)

    def test_combining_two_endpoints(self):
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

                for db in api_test_map[endpoint1]:
                    # [endpoint]/[db]/[endpoint]
                    current = "/api/"+endpoint1+"/"+db+"/"+endpoint2
                    response_db = self.client.get(current)
                    self.assertEqual(response_db.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                    self._check_is_list_of_metadata_objects(response_db.data["results"], "URL : [{}]".format(current))
                    self._check_is_list_of_objects_with_key(response_db.data["results"],
                                                            endpoint_plurals[endpoint2],
                                                            "URL : [{}]".format(current))

                    # [endpoint]/[endpoint]/[db]
                    current = "/api/"+endpoint2+"/"+endpoint1+"/"+db+"/"
                    response_db = self.client.get(current)
                    self.assertEqual(response_db.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                    self._check_counter_by_endpoint(endpoint2, response_db.data, "URL : [{}]".format(current))
                    self._check_count_overview_per_endpoints(response_db.data,
                                                             endpoint_plurals[endpoint1],
                                                             endpoint_plurals[endpoint2],
                                                             "URL : [{}]".format(current))

                    for acc in api_test_map[endpoint1][db]:
                        # [endpoint]/[db]/[acc]/[endpoint]
                        current = "/api/"+endpoint1+"/"+db+"/"+acc+"/"+endpoint2
                        response_acc = self.client.get(current)
                        self.assertEqual(response_acc.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                        self._check_object_by_accesssion(response_acc.data, "URL : [{}]".format(current))
                        self._check_counter_by_endpoint(endpoint2, response_acc.data, "URL : [{}]".format(current))

                        # [endpoint]/[endpoint]/[db]/[acc]
                        current = "/api/"+endpoint2+"/"+endpoint1+"/"+db+"/"+acc+"/"
                        response_acc = self.client.get(current)
                        self.assertEqual(response_acc.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                        self._check_counter_by_endpoint(endpoint2, response_acc.data, "URL : [{}]".format(current))
                        self._check_count_overview_per_endpoints(response_acc.data,
                                                                 endpoint_plurals[endpoint1],
                                                                 endpoint_plurals[endpoint2],
                                                                 "URL : [{}]".format(current))

                    # [endpoint]/[db]/[endpoint]/[db]
                    for db2 in api_test_map[endpoint2]:
                        current = "/api/"+endpoint1+"/"+db+"/"+endpoint2+"/"+db2
                        response_db = self._get_in_debug_mode(current)
                        if response_db.status_code == status.HTTP_200_OK:
                            self._check_is_list_of_metadata_objects(response_db.data["results"],
                                                                    "URL : [{}]".format(current))
                            self._check_is_list_of_objects_with_key(response_db.data["results"],
                                                                    endpoint_plurals[endpoint2],
                                                                    "URL : [{}]".format(current))
                            for result in [x[endpoint_plurals[endpoint2]] for x in response_db.data["results"]]:
                                for match in result:
                                    self.assertIn("coordinates", match, "URL : [{}]".format(current))
                                    self.assertIn("source_database", match, "URL : [{}]".format(current))
                                    self.assertIn("accession", match, "URL : [{}]".format(current))
                        elif response_db.status_code != status.HTTP_204_NO_CONTENT:
                            logging.info("({}) - [{}]".format(response_db.status_code, current))
                            self.client.get(current)

                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[db]
                            current = "/api/"+endpoint1+"/"+db+"/"+acc+"/"+endpoint2+"/"+db2
                            print("URL: [{}]".format(current))
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                logging.info("({}) - [{}]".format(response_db.status_code, current))
                                self.client.get(current)

                            # [endpoint]/[db]/[endpoint]/[db]/[acc]
                            current = "/api/"+endpoint2+"/"+db2+"/"+endpoint1+"/"+db+"/"+acc
                            print("URL: [{}]".format(current))
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(response_acc.status_code, status.HTTP_200_OK, "URL : [{}]".format(current))
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                logging.info("({}) - [{}]".format(response_db.status_code, current))
                                self.client.get(current)

                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]


class EntryWithFilterProteinStructureRESTTest(InterproRESTTestCase):

    def test_can_get_protein_overview_from_entry(self):
        for append in structure_urls:
            response = self.client.get("/api/entry/protein/"+append)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_count_overview(response.data)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self._check_protein_count_overview(response.data)

#     def test_urls_that_return_list_of_accessions_and_proteins(self):
#         acc = "IPR003165"
#         urls = [
#             "/api/entry/interpro/protein/",
#             "/api/entry/pfam/protein/",
#             "/api/entry/unintegrated/protein/",
#             "/api/entry/interpro/pfam/protein/",
#             "/api/entry/unintegrated/pfam/protein/",
#             "/api/entry/interpro/"+acc+"/pfam/protein",
#             ]
#         for url in urls:
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
#
#     def test_urls_that_return_entry_with_protein_count(self):
#         acc = "IPR003165"
#         pfam = "PF02171"
#         pfam_un = "PF17176"
#         urls = [
#             "/api/entry/interpro/"+acc+"/protein",
#             "/api/entry/pfam/"+pfam+"/protein/",
#             "/api/entry/pfam/"+pfam_un+"/protein/",
#             "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/",
#             "/api/entry/interpro/pfam/"+pfam+"/protein/",
#             "/api/entry/unintegrated/pfam/"+pfam_un+"/protein/",
#             ]
#         for url in urls:
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self._check_entry_details(response.data["metadata"])
#             self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
#             self._check_protein_count_overview(response.data["proteins"])
#
#
# class EntryWithFilterProteinUniprotRESTTest(InterproRESTTestCase):
#
#     def test_can_get_protein_match_from_entry(self):
#         response = self.client.get("/api/entry/protein/uniprot")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
#         uniprots = response.data["proteins"]
#         response = self.client.get("/api/entry/protein/swissprot")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         swissprots = response.data["proteins"]
#         response = self.client.get("/api/entry/protein/trembl")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         trembls = response.data["proteins"]
#         self.assertEqual(uniprots, swissprots+trembls, "uniprot proteins should be equal to swissprot + trembl")
#
#     def test_can_get_proteins_from_interpro_protein(self):
#         response = self.client.get("/api/entry/interpro/protein/uniprot")
#         self.assertEqual(len(response.data["results"]), 2)
#         has_one = False
#         has_two = False
#         for result in response.data["results"]:
#             if len(result["proteins"]) == 1:
#                 has_one = True
#             elif len(result["proteins"]) == 2:
#                 has_two = True
#             for match in result["proteins"]:
#                 self._check_match(match)
#
#         self.assertTrue(has_one and has_two,
#                         "One of the entries should have one protein and the other one should have two")
#
#     def test_can_get_swissprot_from_interpro_protein(self):
#         response = self.client.get("/api/entry/interpro/protein/swissprot")
#         self.assertEqual(len(response.data["results"]), 2)
#         has_one = False
#         has_two = False
#         for result in response.data["results"]:
#             if len(result["proteins"]) == 1:
#                 has_one = True
#             elif len(result["proteins"]) == 2:
#                 has_two = True
#             for match in result["proteins"]:
#                 self._check_match(match)
#         self.assertTrue(has_one and not has_two,
#                         "One of the entries should have one protein and the other one should have two")
#
#     def test_can_get_matches_from_entries(self):
#         acc = "IPR003165"
#         pfam = "PF02171"
#         pfam_u = "PF17180"
#         smart = "SM00002"
#         tests = {
#             "/api/entry/interpro/"+acc+"/protein/uniprot": ["A1CUJ5", "P16582"],
#             "/api/entry/interpro/"+acc+"/protein/swissprot": ["A1CUJ5"],
#             "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/uniprot": ["A1CUJ5"],
#             "/api/entry/pfam/"+pfam+"/protein/uniprot": ["A1CUJ5"],
#             "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/uniprot": ["M5ADK6"],
#             "/api/entry/unintegrated/smart/"+smart+"/protein/uniprot": []
#         }
#         for url in tests:
#             response = self.client.get(url)
#             self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
#             self.assertEqual(len(response.data["proteins"]), len(tests[url]))
#             for match in response.data["proteins"]:
#                 self._check_match(match)
#             ids = [x["accession"] for x in response.data["proteins"]]
#             self.assertEqual(tests[url], ids)
#
#
# class EntryWithFilterProteinUniprotAccessionRESTTest(InterproRESTTestCase):
#     def test_can_get_entry_overview_filtered_by_protein(self):
#         prot_s = "M5ADK6"
#         tests = [
#             "/api/entry/protein/uniprot/"+prot_s,
#             ]
#         for url in tests:
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self._check_entry_count_overview(response.data)
#
#     def test_can_get_proteins_from_interpro_id_protein_id(self):
#         acc = "IPR003165"
#         pfam = "PF02171"
#         pfam_u = "PF17180"
#         prot = "A1CUJ5"
#         prot_u = "M5ADK6"
#
#         tests = {
#             "/api/entry/interpro/"+acc+"/protein/uniprot/"+prot: ["A1CUJ5"],
#             "/api/entry/interpro/"+acc+"/protein/swissprot/"+prot: ["A1CUJ5"],
#             "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/uniprot/"+prot: ["A1CUJ5"],
#             "/api/entry/pfam/"+pfam+"/protein/uniprot/"+prot: ["A1CUJ5"],
#             "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/uniprot/"+prot_u: ["M5ADK6"],
#         }
#         for url in tests:
#             response = self.client.get(url)
#             self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
#             self.assertEqual(len(response.data["proteins"]), len(tests[url]), "failed at "+url)
#             for match in response.data["proteins"]:
#                 self._check_match(match)
#                 self._check_protein_details(match["protein"])
#             ids = [x["accession"] for x in response.data["proteins"]]
#             self.assertEqual(tests[url], ids)
#
#     def test_can_get_proteins_from_entr_db_protein_id(self):
#         acc = "IPR003165"
#         prot = "A1CUJ5"
#         prot_u = "M5ADK6"
#
#         tests = {
#             "/api/entry/interpro/protein/uniprot/"+prot: ["A1CUJ5"],
#             "/api/entry/interpro/protein/swissprot/"+prot: ["A1CUJ5"],
#             "/api/entry/interpro/"+acc+"/pfam//protein/uniprot/"+prot: ["A1CUJ5"],
#             "/api/entry/pfam/protein/uniprot/"+prot: ["A1CUJ5"],
#             "/api/entry/unintegrated/pfam/protein/uniprot/"+prot_u: ["M5ADK6"],
#         }
#         for url in tests:
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
#             for entry in response.data["results"]:
#                 self.assertIn("proteins", entry, "'proteins' should be one of the keys in the response")
#                 for match in entry["proteins"]:
#                     self._check_match(match)
#                     self._check_protein_details(match["protein"])
#
#     def test_urls_that_should_fails(self):
#         acc = "IPR003165"
#         pfam = "PF02171"
#         prot = "A1CUJ5"
#         pfam_u = "PF17180"
#         prot_u = "M5ADK6"
#         tests = [
#             "/api/entry/interpro/protein/uniprot/"+prot_u,
#             "/api/entry/interpro/"+acc+"/protein/trembl/"+prot,
#             "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/trembl/"+prot,
#             "/api/entry/interpro/"+acc+"/smart/"+pfam+"/protein/trembl/"+prot,
#             "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/uniprot/"+prot,
#             "/api/entry/unintegrated/pfam/"+pfam+"/protein/trembl/"+prot,
#             "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/trembl/"+prot_u,
#             ]
#         for url in tests:
#             self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")
