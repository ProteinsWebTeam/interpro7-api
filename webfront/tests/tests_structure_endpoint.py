from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class StructureRESTTest(InterproRESTTestCase):

    def test_can_read_structure_overview(self):
        response = self.client.get("/api/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_structure_count_overview(response.data)

    def test_can_read_structure_pdb(self):
        response = self.client.get("/api/structure/pdb")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 4)

    def test_can_read_structure_pdb_accession(self):
        response = self.client.get("/api/structure/pdb/2BKM")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self._check_structure_details(response.data["metadata"])
        self.assertIn("proteins", response.data["metadata"]["counters"])
        self.assertIn("entries", response.data["metadata"]["counters"])
        self.assertEqual(2, response.data["metadata"]["counters"]["proteins"])
        self.assertEqual(1, response.data["metadata"]["counters"]["entries"])

    def test_can_read_structure_pdb_accession_chain(self):
        response = self.client.get("/api/structure/pdb/2bkm/B")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self._check_structure_details(response.data["metadata"])
        for chain in response.data["metadata"]["chains"].values():
            self._check_structure_chain_details(chain)
            self.assertEqual(chain["chain"], "B")


    # TODO:
    def test_cant_read_structure_bad_db(self):
        self._check_HTTP_response_code("/api/structure/bad_db", code=status.HTTP_404_NOT_FOUND)

    def test_cant_read_structure_pdb_bad_chain(self):
        self._check_HTTP_response_code("/api/structure/pdb/2bkm/C")
