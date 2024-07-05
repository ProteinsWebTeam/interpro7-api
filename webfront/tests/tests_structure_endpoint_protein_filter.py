from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase

data_in_fixtures = {
    "2bkm": ["a0a0a2l2g2", "m5adk6"],
    "1t2v": ["p16582", "p16582", "p16582", "p16582", "p16582"],
    "1jm7": ["a1cuj5", "m5adk6"],
    "1jz8": ["a0a0a2l2g2", "a0a0a2l2g2"],
}


class StructureWithFilterProteinRESTTest(InterproRESTTestCase):
    def test_can_get_protein_overview_from_structure(self):
        response = self.client.get("/api/structure/protein/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_structure_count_overview(response.data)
        self.assertIn(
            "proteins",
            response.data,
            "'proteins' should be one of the keys in the response",
        )
        self._check_protein_count_overview(response.data)

    def test_urls_that_return_list_of_accessions_and_proteins(self):
        urls = ["/api/structure/pdb/protein/"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            # self._check_is_list_of_objects_with_key(response.data["results"], "proteins")

    def test_urls_that_return_structure_with_protein_count(self):
        for pdb in data_in_fixtures:
            urls = [
                f"/api/structure/pdb/{pdb}/protein",
                f"/api/structure/pdb/{pdb}/A/protein/",
                f"/api/structure/pdb/{pdb}/B/protein/",
            ]
            for url in urls:
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self._check_structure_details(response.data["metadata"])
                self.assertIn(
                    "proteins",
                    response.data,
                    "'proteins' should be one of the keys in the response",
                )
                self._check_protein_count_overview(response.data)


class StructureWithFilterProteinUniprotRESTTest(InterproRESTTestCase):
    def test_can_get_protein_match_from_structure(self):
        response = self.client.get("/api/structure/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "proteins",
            response.data["structures"]["pdb"],
            "'proteins' should be one of the keys in the response",
        )
        # uniprots = response.data["proteins"]
        # response = self.client.get("/api/structure/protein/reviewed")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # reviewed = response.data["proteins"]
        # response = self.client.get("/api/structure/protein/unreviewed")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # unreviewed = response.data["proteins"]
        # self.assertEqual(uniprots, reviewed+unreviewed, "uniprot proteins should be equal to reviewed + unreviewed")

    def test_can_get_proteins_from_pdb_structures(self):
        self._check_list_url_with_and_without_subset(
            "/api/structure/pdb/protein/uniprot",
            "protein",
            check_inner_subset_fn=self._check_structure_chain_details,
            check_results_fn=lambda results: self.assertEqual(
                len(results), len(data_in_fixtures)
            ),
            check_result_fn=lambda result: self.assertEqual(
                len(result["protein_subset"]),
                len(data_in_fixtures[result["metadata"]["accession"]]),
                f"different length while testing {result['metadata']['accession']}",
            ),
        )

    def test_can_get_reviewed_from_pdb_structures(self):
        self._check_list_url_with_and_without_subset(
            "/api/structure/pdb/protein/reviewed",
            "protein",
            check_inner_subset_fn=self._check_structure_chain_details,
        )

    def test_can_get_uniprot_matches_from_structures(self):
        tests = {
            f"/api/structure/pdb/{pdb}/protein/uniprot": data_in_fixtures[pdb]
            for pdb in data_in_fixtures
        }
        for url in tests:
            self._check_details_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=self._check_structure_chain_details,
                check_metadata_fn=self._check_structure_details,
                check_subset_fn=lambda s: self.assertEqual(len(s), len(tests[url]))
                and self.assertEqual(
                    tests[url].sort(), [x["accession"].lower() for x in s].sort()
                ),
            )

    def test_can_get_uniprot_matches_from_structures_chain(self):
        tests = {
            f"/api/structure/pdb/{pdb}/A/protein/uniprot": data_in_fixtures[pdb]
            for pdb in data_in_fixtures
        }
        for url in tests:
            self._check_details_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda match: self._check_structure_chain_details(
                    match
                )
                and self.assertIn(match["accession"].lower(), tests[url]),
                check_metadata_fn=self._check_structure_details,
            )


class StructureWithFilterProteinUniprotAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_proteins_from_pdb_id_protein_id(self):
        pdb = "1JM7"
        prot_a = "A1CUJ5"
        prot_b = "M5ADK6"

        tests = {
            f"/api/structure/pdb/{pdb}/protein/uniprot/{prot_a}": [prot_a],
            f"/api/structure/pdb/{pdb}/protein/uniprot/{prot_b}": [prot_b],
            f"/api/structure/pdb/{pdb}/A/protein/uniprot/{prot_a}": [prot_a],
            f"/api/structure/pdb/{pdb}/A/protein/reviewed/{prot_a}": [prot_a],
            f"/api/structure/pdb/{pdb}/B/protein/uniprot/{prot_b}": [prot_b],
            f"/api/structure/pdb/{pdb}/B/protein/reviewed/{prot_b}": [prot_b],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn(
                "proteins",
                response.data,
                "'proteins' should be one of the keys in the response",
            )
            self.assertEqual(len(response.data["proteins"]), len(tests[url]))
            for match in response.data["proteins"]:
                self._check_structure_chain_details(match)
            ids = [x["accession"].upper() for x in response.data["proteins"]]
            self.assertEqual(tests[url], ids)

    def test_can_get_proteins_from_structure_db_protein_id(self):
        prot_s = "M5ADK6"
        prot_t = "P16582"

        tests = {
            f"/api/structure/pdb/protein/uniprot/{prot_s}": ["2BKM", "1JM7"],
            f"/api/structure/pdb/protein/reviewed/{prot_s}": ["2BKM", "1JM7"],
            f"/api/structure/pdb/protein/unreviewed/{prot_t}": [
                "1T2V",
                "1T2V",
                "1T2V",
                "1T2V",
                "1T2V",
            ],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            for structure in response.data["results"]:
                self.assertIn(
                    "proteins",
                    structure,
                    "'proteins' should be one of the keys in the response",
                )
                for match in structure["proteins"]:
                    self._check_structure_chain_details(match)
            ids = [x["metadata"]["accession"] for x in response.data["results"]]
            self.assertEqual(tests[url].sort(), ids.sort())

    def test_can_get_proteins_from_structure_protein_id(self):
        prot_s = "M5ADK6"
        response = self.client.get(f"/api/structure/protein/uniprot/{prot_s}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_structure_count_overview(response.data)
        # TODO: improve this test

    def test_urls_that_should_fail_with_no_content(self):
        pdb = "1JM7"
        prot_s = "M5ADK6"
        prot_t = "P16582"
        tests = [
            f"/api/structure/pdb/{pdb}/protein/uniprot/bad_uniprot",
            f"/api/structure/pdb/{pdb}/protein/unreviewed/{prot_s}",
            f"/api/structure/pdb/protein/unreviewed/{prot_s}",
            f"/api/structure/pdb/protein/reviewed/{prot_t}",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg=f"The URL [{url}] should've failed."
            )

    def test_urls_that_should_fail(self):
        pdb = "1JM7"
        prot_s = "M5ADK6"
        tests = [
            f"/api/structure/pdb/bad_structure/protein/uniprot/{prot_s}",
            f"/api/bad_endpoint/pdb/{pdb}/protein/uniprot/{prot_s}",
            f"/api/structure/bad_db/{pdb}/protein/uniprot/{prot_s}",
            f"/api/structure/pdb/{pdb}/protein/uniprot/bad_protein",
            f"/api/structure/pdb/{pdb}/protein/bad_db/{prot_s}",
            f"/api/structure/pdb/{pdb}/bad_endpoint/uniprot/{prot_s}",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_404_NOT_FOUND,
                msg=f"The URL [{url}] should've failed.",
            )
        tests = [
            f"/api/structure/pdb/BADP/protein/uniprot/{prot_s}",
            f"/api/structure/pdb/{pdb}/protein/uniprot/bad_prot",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_204_NO_CONTENT,
                msg=f"The URL [{url}] should've failed.",
            )
