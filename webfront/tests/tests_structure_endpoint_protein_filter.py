from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase

data_in_fixtures = {
    "2BKM": ["A0A0A2L2G2", "M5ADK6"],
    "1T2V": ["P16582", "P16582", "P16582", "P16582", "P16582"],
    "1JM7": ["A1CUJ5", "M5ADK6"],
}
class StructureWithFilterProteinRESTTest(InterproRESTTestCase):

    def test_can_get_protein_overview_from_entry(self):
        response = self.client.get("/api/structure/protein/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_structure_count_overview(response.data)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self._check_protein_count_overview(response.data["proteins"])

    def test_urls_that_return_list_of_accessions_and_proteins(self):
        urls = [
            "/api/structure/pdb/protein/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_accession(response.data["results"])
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")

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
                self._check_protein_count_overview(response.data["proteins"])


class StructureWithFilterProteinUniprotRESTTest(InterproRESTTestCase):

    def test_can_get_protein_match_from_structure(self):
        response = self.client.get("/api/structure/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        uniprots = response.data["proteins"]
        response = self.client.get("/api/structure/protein/swissprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        swissprots = response.data["proteins"]
        response = self.client.get("/api/structure/protein/trembl")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trembls = response.data["proteins"]
        self.assertEqual(uniprots, swissprots+trembls, "uniprot proteins should be equal to swissprot + trembl")

    def test_can_get_proteins_from_pdb_structures(self):
        response = self.client.get("/api/structure/pdb/protein/uniprot")
        self.assertEqual(len(response.data["results"]), len(data_in_fixtures))
        for result in response.data["results"]:
            self.assertEqual(len(result["proteins"]), len(data_in_fixtures[result["accession"]]))
            for match in result["proteins"]:
                self.assertIn(match["protein"], data_in_fixtures[result["accession"]])
                self._check_structure_chain_details(match)

    def test_can_get_swissprot_from_pdb_structures(self):
        response = self.client.get("/api/structure/pdb/protein/swissprot")
        for result in response.data["results"]:
            for match in result["proteins"]:
                self.assertIn(match["protein"], data_in_fixtures[result["accession"]])
                self._check_structure_chain_details(match)

    def test_can_get_uniprot_matches_from_structures(self):
        tests = {"/api/structure/pdb/"+pdb+"/protein/uniprot": data_in_fixtures[pdb] for pdb in data_in_fixtures}
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self.assertEqual(len(response.data["proteins"]), len(tests[url]))
            for match in response.data["proteins"]:
                self._check_structure_chain_details(match)
            ids = [x["protein"] for x in response.data["proteins"]]
            self.assertEqual(tests[url].sort(), ids.sort())

    def test_can_get_uniprot_matches_from_structures_chain(self):
        tests = {"/api/structure/pdb/"+pdb+"/A/protein/uniprot": data_in_fixtures[pdb] for pdb in data_in_fixtures}
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            for match in response.data["proteins"]:
                self._check_structure_chain_details(match)
                self.assertIn(match["protein"], tests[url])

#
# class StructureWithFilterProteinUniprotAccessionRESTTest(InterproRESTTestCase):
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
#             self.assertEqual(len(response.data["proteins"]), len(tests[url]))
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
#             self._check_is_list_of_objects_with_accession(response.data["results"])
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
#             "/api/entry/protein/uniprot/"+prot,
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
