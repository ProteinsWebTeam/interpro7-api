from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


import unittest


class EntryWithFilterStructureRESTTest(InterproRESTTestCase):
    def test_can_get_structure_overview_from_entry(self):
        response = self.client.get("/api/entry/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)
        self.assertIn(
            "structures",
            response.data,
            "'structures' should be one of the keys in the response",
        )
        self._check_structure_count_overview(response.data)

    def test_urls_that_return_list_of_accessions_and_structure(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/structure/",
            "/api/entry/pfam/structure/",
            "/api/entry/unintegrated/structure/",
            "/api/entry/interpro/pfam/structure/",
            "/api/entry/unintegrated/pfam/structure/",
            f"/api/entry/interpro/{acc}/pfam/structure",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )

    def test_urls_that_return_entry_with_structure_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/entry/interpro/{acc}/structure",
            f"/api/entry/pfam/{pfam}/structure/",
            f"/api/entry/pfam/{pfam_un}/structure/",
            f"/api/entry/interpro/{acc}/pfam/{pfam}/structure/",
            f"/api/entry/interpro/pfam/{pfam}/structure/",
            f"/api/entry/unintegrated/pfam/{pfam_un}/structure/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_details(response.data["metadata"])
            self.assertIn(
                "structures",
                response.data,
                "'structures' should be one of the keys in the response",
            )
            self._check_structure_count_overview(response.data)


class EntryWithFilterStructurePDBRESTTest(InterproRESTTestCase):
    def test_can_get_structure_match_from_entry(self):
        response = self.client.get("/api/entry/structure/pdb")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "structures",
            response.data["entries"]["interpro"],
            "'structures' should be one of the keys in the response",
        )
        self._check_entry_count_overview(response.data)
        self.assertIsInstance(response.data["entries"]["interpro"]["structures"], int)

    def test_can_get_structures_from_interpro_structure(self):
        self._check_list_url_with_and_without_subset(
            "/api/entry/interpro/structure/pdb",
            "structure",
            inner_subset_check_fn=self._check_entry_structure_details,
        )

    def test_can_get_structures_from_entry_acc_structure(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        tests = {
            f"/api/entry/interpro/{acc}/structure/pdb": [
                "1JM7",
                "1T2V",
                "1T2V",
                "1T2V",
                "1T2V",
                "1T2V",
            ],
            f"/api/entry/interpro/{acc}/pfam/{pfam}/structure/pdb": ["1JM7"],
            f"/api/entry/pfam/{pfam}/structure/pdb": ["1JM7"],
            f"/api/entry/unintegrated/pfam/{pfam_u}/structure/pdb": ["1JM7", "2BKM"],
        }

        def check_subset(subset):
            ids = [x["accession"] for x in subset]
            self.assertEqual(tests[url].sort(), ids.sort())

        for url in tests:
            self._check_details_url_with_and_without_subset(
                url,
                "structure",
                inner_subset_check_fn=self._check_entry_structure_details,
                subset_check_fn=check_subset,
            )

    def test_urls_that_should_fails_with_no_content(self):
        smart = "SM00002"
        tests = [f"/api/entry/unintegrated/smart/{smart}/structure/pdb"]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg=f"The URL [{url}] should've failed."
            )


class EntryWithFilterstructurepdbAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_entry_overview_filtered_by_structure(self):
        pdb = "1JM7"
        tests = [f"/api/entry/structure/pdb/{pdb}"]
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
            f"/api/entry/interpro/{acc}/structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/interpro/{acc}/pfam/{pfam}/structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/pfam/{pfam}/structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/unintegrated/pfam/{pfam_u}/structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/unintegrated/pfam/{pfam_u}/structure/pdb/{pdb_2}": [pdb_2],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn(
                "structures",
                response.data,
                "'structures' should be one of the keys in the response",
            )
            self.assertEqual(
                len(response.data["structures"]), len(tests[url]), f"failed at {url}"
            )
            for match in response.data["structures"]:
                self._check_entry_structure_details(match)
            ids = [x["accession"].upper() for x in response.data["structures"]]
            self.assertEqual(tests[url], ids)

    def test_can_get_structures_from_entry_db_structure_id(self):
        acc = "IPR003165"
        pdb_1 = "1JM7"
        pdb_2 = "2BKM"

        tests = {
            f"/api/entry/interpro/structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/interpro/{acc}/pfam//structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/pfam/structure/pdb/{pdb_1}": [pdb_1],
            f"/api/entry/unintegrated/pfam/structure/pdb/{pdb_2}": [pdb_2],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            for entry in response.data["results"]:
                self.assertIn(
                    "structures",
                    entry,
                    "'structures' should be one of the keys in the response",
                )
                for match in entry["structures"]:
                    self._check_entry_structure_details(match)
                    # self._check_structure_details(match["structure"])

    def test_urls_that_should_fails_with_no_content(self):
        acc = "IPR003165"
        pdb_1 = "1T2V"
        pdb_2 = "2BKM"
        pfam_u = "PF17180"
        tests = [
            f"/api/entry/interpro/structure/pdb/{pdb_2}",
            f"/api/entry/interpro/{acc}/structure/pdb/{pdb_2}",
            f"/api/entry/unintegrated/pfam/{pfam_u}/structure/pdb/{pdb_1}",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg=f"The URL [{url}] should've failed."
            )

    def test_urls_that_should_fail(self):
        pdb_2 = "2BKM"
        pfam = "PF02171"
        tests = [f"/api/entry/unintegrated/pfam/{pfam}/structure/pdb/{pdb_2}"]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_204_NO_CONTENT,
                msg=f"The URL [{url}] should've failed.",
            )
