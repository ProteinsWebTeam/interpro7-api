from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class UtilsTest(InterproRESTTestCase):

    def test_can_read_structure_overview(self):
        response = self.client.get("/api/utils")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("available", response.data)
        self.assertIn("accession", response.data["available"])

    def test_accession_endpoint_doesnt_fail(self):
        response = self.client.get("/api/utils/accession")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accession_endpoint_with_unexisting_acc(self):
        response = self.client.get("/api/utils/accession/xxXx")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_accession_endpoint_with_ipro(self):
        response = self.client.get("/api/utils/accession/IPR003165")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "entry")
        self.assertEqual(response.data["source_database"], "interpro")

    def test_accession_endpoint_with_protein(self):
        response = self.client.get("/api/utils/accession/A1CUJ5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "protein")
        self.assertEqual(response.data["source_database"], "reviewed")

    def test_accession_endpoint_with_structure(self):
        response = self.client.get("/api/utils/accession/1JM7")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "structure")
        self.assertEqual(response.data["source_database"], "pdb")

    def test_accession_endpoint_with_proteome(self):
        response = self.client.get("/api/utils/accession/UP000012042")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "proteome")
        self.assertEqual(response.data["source_database"], "uniprot")

    def test_accession_endpoint_with_set(self):
        response = self.client.get("/api/utils/accession/CL0001")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "set")
        self.assertEqual(response.data["source_database"], "pfam")

    def test_accession_endpoint_with_taxonomy(self):
        response = self.client.get("/api/utils/accession/344612")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "taxonomy")
        self.assertEqual(response.data["source_database"], "uniprot")

