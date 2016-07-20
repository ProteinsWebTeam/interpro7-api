from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class EntryWithFilterStructureRESTTest(InterproRESTTestCase):

    def test_can_get_structure_overview_from_entry(self):
        response = self.client.get("/api/entry/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)
        self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
        self._check_structure_count_overview(response.data["structures"])

    def test_urls_that_return_list_of_accessions_and_structure(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/structure/",
            "/api/entry/pfam/structure/",
            "/api/entry/unintegrated/structure/",
            "/api/entry/interpro/pfam/structure/",
            "/api/entry/unintegrated/pfam/structure/",
            "/api/entry/interpro/"+acc+"/pfam/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")

    def test_urls_that_return_entry_with_structure_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/entry/interpro/"+acc+"/structure",
            "/api/entry/pfam/"+pfam+"/structure/",
            "/api/entry/pfam/"+pfam_un+"/structure/",
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/structure/",
            "/api/entry/interpro/pfam/"+pfam+"/structure/",
            "/api/entry/unintegrated/pfam/"+pfam_un+"/structure/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_details(response.data["metadata"])
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_structure_count_overview(response.data["structures"])


class EntryWithFilterStructurePDBRESTTest(InterproRESTTestCase):

    def test_can_get_structure_match_from_entry(self):
        response = self.client.get("/api/entry/structure/pdb")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
        self._check_entry_count_overview(response.data)
        self.assertIsInstance(response.data["structures"], int)

    def test_can_get_structures_from_interpro_structure(self):
        response = self.client.get("/api/entry/interpro/structure/pdb")
        self.assertEqual(len(response.data["results"]), 2)
        for result in response.data["results"]:
            for match in result["structures"]:
                # self.assertIn(match["structure"], data_in_fixtures[result["accession"]])
                self._check_entry_structure_details(match)

    def test_can_get_matches_from_entries(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        smart = "SM00002"
        tests = {
            "/api/entry/interpro/"+acc+"/structure/pdb": ["1JM7", "1T2V", "1T2V", "1T2V", "1T2V", "1T2V"],
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/structure/pdb": ["1JM7"],
            "/api/entry/pfam/"+pfam+"/structure/pdb": ["1JM7"],
            "/api/entry/unintegrated/pfam/"+pfam_u+"/structure/pdb": ["1JM7", "2BKM"],
            "/api/entry/unintegrated/smart/"+smart+"/structure/pdb": []
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self.assertEqual(len(response.data["structures"]), len(tests[url]), "on url: "+url)
            for match in response.data["structures"]:
                self._check_entry_structure_details(match)
            ids = [x["structure"] for x in response.data["structures"]]
            self.assertEqual(tests[url].sort(), ids.sort())


class EntryWithFilterstructurepdbAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_entry_overview_filtered_by_structure(self):
        pdb = "1JM7"
        tests = [
            "/api/entry/structure/pdb/"+pdb,
            ]
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_count_overview(response.data)

    def test_can_get_structures_from_interpro_id_structure_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        pdb_1 = "1JM7"
        pdb_2 = "2BKM"

        tests = {
            "/api/entry/interpro/"+acc+"/structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/pfam/"+pfam+"/structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/unintegrated/pfam/"+pfam_u+"/structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/unintegrated/pfam/"+pfam_u+"/structure/pdb/"+pdb_2: [pdb_2],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self.assertEqual(len(response.data["structures"]), len(tests[url]), "failed at "+url)
            for match in response.data["structures"]:
                self._check_entry_structure_details(match)
            ids = [x["structure"]["accession"] for x in response.data["structures"]]
            self.assertEqual(tests[url], ids)

    def test_can_get_structures_from_entry_db_structure_id(self):
        acc = "IPR003165"
        pdb_1 = "1JM7"
        pdb_2 = "2BKM"

        tests = {
            "/api/entry/interpro/structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/interpro/"+acc+"/pfam//structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/pfam/structure/pdb/"+pdb_1: [pdb_1],
            "/api/entry/unintegrated/pfam/structure/pdb/"+pdb_2: [pdb_2],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            for entry in response.data["results"]:
                self.assertIn("structures", entry, "'structures' should be one of the keys in the response")
                for match in entry["structures"]:
                    self._check_entry_structure_details(match)
                    self._check_structure_details(match["structure"])

    def test_urls_that_should_fails(self):
        acc = "IPR003165"
        pdb_1 = "1T2V"
        pdb_2 = "2BKM"
        pfam = "PF02171"
        pfam_u = "PF17180"
        tests = [
            "/api/entry/interpro/structure/pdb/"+pdb_2,
            "/api/entry/interpro/"+acc+"/structure/pdb/"+pdb_2,
            "/api/entry/unintegrated/pfam/"+pfam_u+"/structure/pdb/"+pdb_1,
            "/api/entry/unintegrated/pfam/"+pfam+"/structure/pdb/"+pdb_2,
            ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")
