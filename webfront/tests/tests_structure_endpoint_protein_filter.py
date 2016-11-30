from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase

data_in_fixtures = {
    "2BKM": ["A0A0A2L2G2", "M5ADK6"],
    "1T2V": ["P16582", "P16582", "P16582", "P16582", "P16582"],
    "1JM7": ["A1CUJ5", "M5ADK6"],
    "1JZ8": ["A0A0A2L2G2", "A0A0A2L2G2"]
}


import unittest
@unittest.skip("refactoring for solr")
class StructureWithFilterProteinRESTTest(InterproRESTTestCase):

    def test_can_get_protein_overview_from_structure(self):
        response = self.client.get("/api/structure/protein/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_structure_count_overview(response.data)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self._check_protein_count_overview(response.data)

    def test_urls_that_return_list_of_accessions_and_proteins(self):
        urls = [
            "/api/structure/pdb/protein/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            # self._check_is_list_of_objects_with_key(response.data["results"], "proteins")

    def test_urls_that_return_structure_with_protein_count(self):
        for pdb in data_in_fixtures:
            urls = [
                "/api/structure/pdb/"+pdb+"/protein",
                "/api/structure/pdb/"+pdb+"/A/protein/",
                "/api/structure/pdb/"+pdb+"/B/protein/",
                ]
            for url in urls:
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self._check_structure_details(response.data["metadata"])
                self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
                self._check_protein_count_overview(response.data)


@unittest.skip("refactoring for solr")
class StructureWithFilterProteinUniprotRESTTest(InterproRESTTestCase):

    def test_can_get_protein_match_from_structure(self):
        response = self.client.get("/api/structure/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("proteins", response.data["structures"]["pdb"], "'proteins' should be one of the keys in the response")
        # uniprots = response.data["proteins"]
        # response = self.client.get("/api/structure/protein/swissprot")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # swissprots = response.data["proteins"]
        # response = self.client.get("/api/structure/protein/trembl")
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # trembls = response.data["proteins"]
        # self.assertEqual(uniprots, swissprots+trembls, "uniprot proteins should be equal to swissprot + trembl")

    def test_can_get_proteins_from_pdb_structures(self):
        response = self.client.get("/api/structure/pdb/protein/uniprot")
        self.assertEqual(len(response.data["results"]), len(data_in_fixtures))
        for result in response.data["results"]:
            self.assertEqual(len(result["proteins"]), len(data_in_fixtures[result["metadata"]["accession"]]))
            for match in result["proteins"]:
                self.assertIn(match["accession"], data_in_fixtures[result["metadata"]["accession"]])
                self._check_structure_chain_details(match)

    def test_can_get_swissprot_from_pdb_structures(self):
        response = self.client.get("/api/structure/pdb/protein/swissprot")
        for result in response.data["results"]:
            for match in result["proteins"]:
                self.assertIn(match["accession"], data_in_fixtures[result["metadata"]["accession"]])
                self._check_structure_chain_details(match)

    def test_can_get_uniprot_matches_from_structures(self):
        tests = {"/api/structure/pdb/"+pdb+"/protein/uniprot": data_in_fixtures[pdb] for pdb in data_in_fixtures}
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self.assertEqual(len(response.data["proteins"]), len(tests[url]))
            for match in response.data["proteins"]:
                self._check_structure_chain_details(match)
            ids = [x["accession"] for x in response.data["proteins"]]
            self.assertEqual(tests[url].sort(), ids.sort())

    def test_can_get_uniprot_matches_from_structures_chain(self):
        tests = {"/api/structure/pdb/"+pdb+"/A/protein/uniprot": data_in_fixtures[pdb] for pdb in data_in_fixtures}
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            for match in response.data["proteins"]:
                self._check_structure_chain_details(match)
                self.assertIn(match["accession"], tests[url])


@unittest.skip("refactoring for solr")
class StructureWithFilterProteinUniprotAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_proteins_from_pdb_id_protein_id(self):
        pdb = "1JM7"
        prot_a = "A1CUJ5"
        prot_b = "M5ADK6"

        tests = {
            "/api/structure/pdb/"+pdb+"/protein/uniprot/"+prot_a: [prot_a],
            "/api/structure/pdb/"+pdb+"/protein/uniprot/"+prot_b: [prot_b],
            "/api/structure/pdb/"+pdb+"/A/protein/uniprot/"+prot_a: [prot_a],
            "/api/structure/pdb/"+pdb+"/A/protein/swissprot/"+prot_a: [prot_a],
            "/api/structure/pdb/"+pdb+"/B/protein/uniprot/"+prot_b: [prot_b],
            "/api/structure/pdb/"+pdb+"/B/protein/swissprot/"+prot_b: [prot_b],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self.assertEqual(len(response.data["proteins"]), len(tests[url]))
            for match in response.data["proteins"]:
                self._check_structure_chain_details(match)
                self._check_protein_details(match["protein"])
            ids = [x["protein"]["accession"] for x in response.data["proteins"]]
            self.assertEqual(tests[url], ids)

    def test_can_get_proteins_from_structure_db_protein_id(self):
        prot_s = "M5ADK6"
        prot_t = "P16582"

        tests = {
            "/api/structure/pdb/protein/uniprot/"+prot_s: ["2BKM", "1JM7"],
            "/api/structure/pdb/protein/swissprot/"+prot_s: ["2BKM", "1JM7"],
            "/api/structure/pdb/protein/trembl/"+prot_t: ["1T2V", "1T2V", "1T2V", "1T2V", "1T2V"],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            for structure in response.data["results"]:
                self.assertIn("proteins", structure, "'proteins' should be one of the keys in the response")
                for match in structure["proteins"]:
                    self._check_structure_chain_details(match)
                    self._check_protein_details(match["protein"])
            ids = [x["metadata"]["accession"] for x in response.data["results"]]
            self.assertEqual(tests[url].sort(), ids.sort())

    def test_can_get_proteins_from_structure_protein_id(self):
        prot_s = "M5ADK6"
        response = self.client.get("/api/structure/protein/uniprot/"+prot_s)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_structure_count_overview(response.data)
        # TODO: improve this test

    def test_urls_that_should_fail_with_no_content(self):
        pdb = "1JM7"
        prot_s = "M5ADK6"
        prot_t = "P16582"
        tests = [
            "/api/structure/pdb/"+pdb+"/protein/uniprot/bad_uniprot",
            "/api/structure/pdb/"+pdb+"/protein/trembl/"+prot_s,
            "/api/structure/pdb/protein/trembl/"+prot_s,
            "/api/structure/pdb/protein/swissprot/"+prot_t,
            ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")

    def test_urls_that_should_fails(self):
        pdb = "1JM7"
        prot_s = "M5ADK6"
        prot_t = "P16582"
        tests = [
            "/api/structure/pdb/BADP/protein/uniprot/"+prot_s,
            ]
        for url in tests:
            self._check_HTTP_response_code(url, code=status.HTTP_404_NOT_FOUND, msg="The URL ["+url+"] should've failed.")
