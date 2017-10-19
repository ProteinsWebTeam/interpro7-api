from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase

data_in_fixtures = {
    "A0A0A2L2G2": ["2BKM", "1JZ8", "1JZ8"],
    "M5ADK6": ["2BKM", "1JM7"],
    "P16582": ["1T2V", "1T2V", "1T2V", "1T2V", "1T2V"],
    "A1CUJ5": ["1JM7"],
}
data_reviewed = ["A1CUJ5", "M5ADK6"]


import unittest


class ProteinWithFilterStructureRESTTest(InterproRESTTestCase):

    def test_can_get_structure_overview_from_protein(self):
        response = self.client.get("/api/protein/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_protein_count_overview(response.data)
        self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
        self._check_structure_count_overview(response.data)

    def test_urls_that_return_list_of_accessions_and_structures(self):
        urls = [
            "/api/protein/uniprot/structure/",
            "/api/protein/reviewed/structure/",
            "/api/protein/unreviewed/structure/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            # self._check_is_list_of_objects_with_key(response.data["results"], "structures")

    def test_urls_that_return_protein_with_structure_count(self):
        for prot in data_in_fixtures:
            urls = ["/api/protein/uniprot/"+prot+"/structure"]
            if prot in data_reviewed:
                urls.append("/api/protein/reviewed/"+prot+"/structure")
            else:
                urls.append("/api/protein/unreviewed/"+prot+"/structure")
            for url in urls:
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self._check_protein_details(response.data["metadata"])
                self.assertIn("structures", response.data["metadata"]["counters"], "'structures' should be one of the keys in the response")
                self.assertEqual(response.data["metadata"]["counters"]["structures"], len(list(set(data_in_fixtures[prot]))))


class ProteinWithFilterStructurePdbRESTTest(InterproRESTTestCase):

    def test_can_get_protein_match_from_structure(self):
        response = self.client.get("/api/protein/structure/pdb")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_protein_count_overview(response.data)
        self.assertIn("structures", response.data["proteins"]["uniprot"], "'structures' should be one of the keys in the response")

    def test_can_get_proteins_from_pdb_structures(self):
        response = self.client.get("/api/protein/uniprot/structure/pdb")
        self.assertEqual(len(response.data["results"]), len(data_in_fixtures))
        for result in response.data["results"]:
            self.assertEqual(len(result["structures"]),
                             len(data_in_fixtures[result["metadata"]["accession"]]),
                             "failing for "+result["metadata"]["accession"])
            for match in result["structures"]:
                self.assertIn(match["accession"].upper(), data_in_fixtures[result["metadata"]["accession"]])
                self._check_structure_chain_details(match)

    def test_can_get_reviewed_from_pdb_structures(self):
        response = self.client.get("/api/protein/reviewed/structure/pdb")
        self.assertEqual(len(response.data["results"]), len(data_reviewed))
        for result in response.data["results"]:
            self.assertEqual(len(result["structures"]),
                             len(data_in_fixtures[result["metadata"]["accession"]]),
                             "failing for "+result["metadata"]["accession"])
            self.assertIn(result["metadata"]["accession"], data_reviewed)
            for match in result["structures"]:
                self.assertIn(match["accession"].upper(), data_in_fixtures[result["metadata"]["accession"]])
                self._check_structure_chain_details(match)

    def test_can_get_uniprot_matches_from_structures(self):
        tests = {"/api/protein/uniprot/"+prot+"/structure/pdb": data_in_fixtures[prot] for prot in data_in_fixtures}
        for url in tests:
            response = self.client.get(url)
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self.assertEqual(len(response.data["structures"]), len(tests[url]))
            for match in response.data["structures"]:
                self._check_structure_chain_details(match)
            ids = [x["accession"] for x in response.data["structures"]]
            self.assertEqual(tests[url].sort(), ids.sort())

    def test_urls_that_should_fails(self):
        prot_s = "M5ADK6"
        prot_t = "P16582"
        tests = [
            "/api/protein/reviewed/"+prot_t+"/structure/pdb",
            "/api/protein/unreviewed/"+prot_s+"/structure/pdb",
            ]
        for url in tests:
            self._check_HTTP_response_code(url, code=status.HTTP_204_NO_CONTENT, msg="The URL ["+url+"] should've failed.")
        tests = [
            "/api/protein/unreviewed/BADP/structure/pdb",
            "/api/bad_endpoint/reviewed/"+prot_t+"/structure/pdb",
            "/api/protein/unreviewed/"+prot_s+"/bad_endpoint/pdb",
            "/api/protein/bad_db/"+prot_t+"/structure/pdb",
            "/api/protein/unreviewed/"+prot_s+"/structure/bad_db",
            ]
        for url in tests:
            self._check_HTTP_response_code(url, code=status.HTTP_404_NOT_FOUND, msg="The URL ["+url+"] should've failed.")


class ProteinWithFilterStructurePDBAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_proteins_from_pdb_id_protein_id(self):
        pdb = "1JM7"
        prot_a = "A1CUJ5"
        prot_b = "M5ADK6"

        tests = {
            "/api/protein/uniprot/"+prot_a+"/structure/pdb/"+pdb: [pdb],
            "/api/protein/uniprot/"+prot_b+"/structure/pdb/"+pdb: [pdb],
            "/api/protein/uniprot/"+prot_a+"/structure/pdb/"+pdb+"/A": [pdb],
            "/api/protein/uniprot/"+prot_b+"/structure/pdb/"+pdb+"/B": [pdb],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_protein_details(response.data["metadata"])
            self.assertEqual(len(response.data["structures"]), len(tests[url]), "URL: "+url)
            for match in response.data["structures"]:
                self._check_structure_chain_details(match)
            ids = [x["accession"].upper() for x in response.data["structures"]]
            self.assertEqual(tests[url], ids)

    def test_can_get_proteins_from_structure_db_protein_id(self):
        pdb_1 = "1T2V"
        pdb_2 = "2BKM"

        tests = {
            "/api/protein/uniprot/structure/pdb/"+pdb_1: ["P16582", "P16582", "P16582", "P16582", "P16582"],
            "/api/protein/uniprot/structure/pdb/"+pdb_2: ["M5ADK6", "A0A0A2L2G2"],
            "/api/protein/unreviewed/structure/pdb/"+pdb_2: ["A0A0A2L2G2"],
            "/api/protein/reviewed/structure/pdb/"+pdb_2: ["M5ADK6"],
            "/api/protein/uniprot/structure/pdb/"+pdb_1+"/A": ["P16582"],
            "/api/protein/uniprot/structure/pdb/"+pdb_2+"/B": ["M5ADK6", "A0A0A2L2G2"],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            for protein in response.data["results"]:
                self.assertIn("structures", protein, "'structures' should be one of the keys in the response")
                for match in protein["structures"]:
                    self._check_structure_chain_details(match)
                    # self._check_structure_details(match["structure"])
            ids = [x["metadata"]["accession"] for x in response.data["results"]]
            self.assertEqual(tests[url].sort(), ids.sort())

    def test_can_get_proteins_from_structure_protein_id(self):
        pdb_1 = "1T2V"
        response = self.client.get("/api/protein/structure/pdb/"+pdb_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_protein_count_overview(response.data)
        # TODO: improve this test

    def test_urls_that_should_fails_with_no_content(self):
        pdb_1 = "1JM7"
        # pdb_2 = "2BKM"
        # TODO: the one with pdb_2 has been commented, as it doesn't give error but rather an empty array
        # So evalluate what is the best approach
        prot_s1 = "A1CUJ5"
        prot_s2 = "M5ADK6"
        tests = [
            "/api/protein/uniprot/"+prot_s1+"/structure/pdb/"+pdb_1+"/B",
            "/api/protein/uniprot/"+prot_s2+"/structure/pdb/"+pdb_1+"/A",
            "/api/protein/unreviewed/structure/pdb/"+pdb_1,
            # "/api/protein/unreviewed/structure/pdb/"+pdb_2+"/B",
            ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")

    def test_urls_that_should_fail(self):
        pdb_1 = "1JM7"
        # pdb_2 = "2BKM"
        # TODO: the one with pdb_2 has been commented, as it doesn't give error but rather an empty array
        # So evalluate what is the best approach
        prot_s1 = "A1CUJ5"
        prot_s2 = "M5ADK6"
        tests = [
            "/api/protein/unreviewed/BAD_PROTEIN/structure/pdb/"+pdb_1,
            "/api/protein/structure/pdb/BAD_PDB"
            "/api/protein/unreviewed/"+prot_s2+"/structure/pdb/"+pdb_1,
        ]
        for url in tests:
            self._check_HTTP_response_code(url, code=status.HTTP_404_NOT_FOUND, msg="The URL ["+url+"] should've failed.")
