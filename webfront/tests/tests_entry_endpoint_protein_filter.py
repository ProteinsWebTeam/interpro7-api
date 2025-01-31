from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class EntryWithFilterProteinRESTTest(InterproRESTTestCase):
    def test_can_get_protein_overview_from_entry(self):
        response = self.client.get("/api/entry/protein/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)
        self.assertIn(
            "proteins",
            response.data,
            "'proteins' should be one of the keys in the response",
        )
        self._check_protein_count_overview(response.data)

    def test_urls_that_return_list_of_accessions_and_proteins(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/protein/",
            "/api/entry/pfam/protein/",
            "/api/entry/unintegrated/protein/",
            "/api/entry/interpro/pfam/protein/",
            "/api/entry/unintegrated/pfam/protein/",
            f"/api/entry/interpro/{acc}/pfam/protein",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )

    def test_urls_that_return_entry_with_protein_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/entry/interpro/{acc}/protein",
            f"/api/entry/pfam/{pfam}/protein/",
            f"/api/entry/pfam/{pfam_un}/protein/",
            f"/api/entry/interpro/{acc}/pfam/{pfam}/protein/",
            f"/api/entry/interpro/pfam/{pfam}/protein/",
            f"/api/entry/unintegrated/pfam/{pfam_un}/protein/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_details(response.data["metadata"])
            self.assertIn(
                "proteins",
                response.data,
                "'proteins' should be one of the keys in the response",
            )
            self._check_protein_count_overview(response.data)


class EntryWithFilterProteinUniprotRESTTest(InterproRESTTestCase):
    def test_can_get_protein_match_from_entry(self):
        response = self.client.get("/api/entry/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "proteins",
            response.data["entries"]["unintegrated"],
            "'proteins' should be one of the keys in the response",
        )

    def test_can_get_proteins_from_interpro_protein(self):
        response = self.client.get("/api/entry/interpro/protein/uniprot?show-subset")
        self.assertEqual(len(response.data["results"]), 2)
        has_one = False
        has_two = False
        for result in response.data["results"]:
            if len(result["protein_subset"]) == 1:
                has_one = True
            elif len(result["protein_subset"]) == 2:
                has_two = True
            for match in result["protein_subset"]:
                self._check_match(match)

        self.assertTrue(
            has_one and has_two,
            "One of the entries should have one protein and the other one should have two",
        )

    def test_can_get_reviewed_from_interpro_protein(self):
        response = self.client.get("/api/entry/interpro/protein/reviewed?show-subset")
        self.assertEqual(len(response.data["results"]), 2)
        has_one = False
        has_two = False
        for result in response.data["results"]:
            if len(result["protein_subset"]) == 1:
                has_one = True
            elif len(result["protein_subset"]) == 2:
                has_two = True
            for match in result["protein_subset"]:
                self._check_match(match)
        self.assertTrue(
            has_one and not has_two,
            "One of the entries should have one protein and the other one should have two",
        )

    def test_can_get_matches_from_entries(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        tests = {
            f"/api/entry/interpro/{acc}/protein/uniprot": ["A1CUJ5", "P16582"],
            f"/api/entry/interpro/{acc}/protein/reviewed": ["A1CUJ5"],
            f"/api/entry/interpro/{acc}/pfam/{pfam}/protein/uniprot": ["A1CUJ5"],
            f"/api/entry/pfam/{pfam}/protein/uniprot": ["A1CUJ5"],
            f"/api/entry/unintegrated/pfam/{pfam_u}/protein/uniprot": ["M5ADK6"],
        }
        for url in tests:
            self._check_details_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=self._check_match,
                check_metadata_fn=self._check_entry_details,
                check_subset_fn=lambda subset: self.assertEqual(
                    len(subset), len(tests[url])
                )
                and self.assertEqual(
                    tests[url].sort(), [x["accession"].upper() for x in subset].sort()
                ),
            )


class EntryWithFilterProteinUniprotAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_entry_overview_filtered_by_protein(self):
        prot_s = "M5ADK6"
        tests = [f"/api/entry/protein/uniprot/{prot_s}"]
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_count_overview(response.data)

    def test_can_get_proteins_from_interpro_id_protein_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        prot = "A1CUJ5"
        prot_u = "M5ADK6"

        tests = {
            f"/api/entry/interpro/{acc}/protein/uniprot/{prot}": ["A1CUJ5"],
            f"/api/entry/interpro/{acc}/protein/reviewed/{prot}": ["A1CUJ5"],
            f"/api/entry/interpro/{acc}/pfam/{pfam}/protein/uniprot/{prot}": ["A1CUJ5"],
            f"/api/entry/pfam/{pfam}/protein/uniprot/{prot}": ["A1CUJ5"],
            f"/api/entry/unintegrated/pfam/{pfam_u}/protein/uniprot/{prot_u}": [
                "M5ADK6"
            ],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn(
                "proteins",
                response.data,
                "'proteins' should be one of the keys in the response",
            )
            self.assertEqual(
                len(response.data["proteins"]), len(tests[url]), f"failed at {url}"
            )
            for match in response.data["proteins"]:
                self._check_match(match)
                # self._check_protein_details(match["protein"])
            ids = [x["accession"].upper() for x in response.data["proteins"]]
            self.assertEqual(tests[url], ids)

    def test_can_get_proteins_from_entry_db_protein_id(self):
        acc = "IPR003165"
        prot = "A1CUJ5"
        prot_u = "M5ADK6"

        tests = {
            f"/api/entry/interpro/protein/uniprot/{prot}": ["A1CUJ5"],
            f"/api/entry/interpro/protein/reviewed/{prot}": ["A1CUJ5"],
            f"/api/entry/interpro/{acc}/pfam//protein/uniprot/{prot}": ["A1CUJ5"],
            f"/api/entry/pfam/protein/uniprot/{prot}": ["A1CUJ5"],
            f"/api/entry/unintegrated/pfam/protein/uniprot/{prot_u}": ["M5ADK6"],
            f"/api/entry/panther/protein/uniprot/{prot_u}": ["M5ADK6"],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            for entry in response.data["results"]:
                self.assertIn(
                    "proteins",
                    entry,
                    "'proteins' should be one of the keys in the response",
                )
                for match in entry["proteins"]:
                    self._check_match(match)
                    # self._check_protein_details(match["protein"])

    def test_urls_that_should_fails_with_no_content(self):
        acc = "IPR003165"
        pfam = "PF02171"
        prot = "A1CUJ5"
        pfam_u = "PF17180"
        prot_u = "M5ADK6"
        smart = "SM00002"
        tests = [
            f"/api/entry/interpro/protein/uniprot/{prot_u}",
            f"/api/entry/interpro/{acc}/protein/unreviewed/{prot}",
            f"/api/entry/interpro/{acc}/pfam/{pfam}/protein/unreviewed/{prot}",
            f"/api/entry/unintegrated/pfam/{pfam_u}/protein/uniprot/{prot}",
            f"/api/entry/unintegrated/pfam/{pfam_u}/protein/unreviewed/{prot_u}",
            f"/api/entry/unintegrated/smart/{smart}/protein/uniprot",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg=f"The URL [{url}] should've failed."
            )

    def test_urls_with_wrong_accession(self):
        acc = "IPR003165"
        pfam = "PF02171"
        prot = "A1CUJ5"
        tests = [
            f"/api/entry/interpro/{acc}/smart/{pfam}/protein/unreviewed/{prot}",
            f"/api/structure/PDB/101m/entry/smart/{pfam}",
            f"/api/entry/smart/{pfam}/structure/PDB/101m/"]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_404_NOT_FOUND,
                msg=f"The URL [{url}] should've failed.",
            )
        
    def test_urls_that_should_fail(self):
        acc = "IPR003165"
        pfam = "PF02171"
        prot = "A1CUJ5"
        tests = [
            f"/api/entry/unintegrated/pfam/{pfam}/protein/unreviewed/{prot}",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_204_NO_CONTENT,
                msg=f"The URL [{url}] should've failed.",
            )
