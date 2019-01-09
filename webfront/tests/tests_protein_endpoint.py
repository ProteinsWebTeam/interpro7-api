from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class ProteinRESTTest(InterproRESTTestCase):
    def test_can_read_protein_overview(self):
        response = self.client.get("/api/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_protein_count_overview(response.data)

    def test_can_read_protein_uniprot(self):
        response = self.client.get("/api/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 4)

    def test_can_read_protein_uniprot_accession(self):
        response = self.client.get("/api/protein/uniprot/P16582")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self._check_protein_details(response.data["metadata"])
        self.assertIn("structures", response.data["metadata"]["counters"])
        self.assertIn("entries", response.data["metadata"]["counters"])
        self.assertEqual(1, response.data["metadata"]["counters"]["structures"])
        self.assertEqual(2, response.data["metadata"]["counters"]["entries"])

    def test_can_read_protein_id(self):
        url_id = "/api/protein/uniprot/CBPYA_ASPCL"
        response = self.client.get(url_id)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("a1cuj5", response.url.lower())

    def test_can_read_protein_reviewed(self):
        response = self.client.get("/api/protein/reviewed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_protein_reviewed_accession(self):
        response = self.client.get("/api/protein/reviewed/A1CUJ5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self._check_protein_details(response.data["metadata"])
        self.assertIn("structures", response.data["metadata"]["counters"])
        self.assertIn("entries", response.data["metadata"]["counters"])
        self.assertEqual(1, response.data["metadata"]["counters"]["structures"])
        self.assertEqual(5, response.data["metadata"]["counters"]["entries"])

    def test_cant_read_protein_bad_db(self):
        self._check_HTTP_response_code(
            "/api/protein/bad_db", code=status.HTTP_404_NOT_FOUND
        )

    def test_cant_read_protein_uniprot_bad_id(self):
        self._check_HTTP_response_code(
            "/api/protein/uniprot/badformmedID", code=status.HTTP_404_NOT_FOUND
        )
        self._check_HTTP_response_code(
            "/api/protein/uniprot/A1CUJ6",
            code=status.HTTP_204_NO_CONTENT,
            msg="It should fail as 204 because the ID is well formed but it is not in the BD",
        )
