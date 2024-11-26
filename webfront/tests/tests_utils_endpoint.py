from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from webfront.models.interpro_new import Release_Note


class UtilsAccessionTest(InterproRESTTestCase):
    def test_can_read_structure_overview(self):
        response = self.client.get("/api/utils")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("available", response.data)
        self.assertIn("accession", response.data["available"])
        self.assertIn("release", response.data["available"])

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

    def test_accession_endpoint_with_protein_id(self):
        response = self.client.get("/api/utils/accession/CBPYA_ASPCL")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "protein")
        self.assertEqual(response.data["source_database"], "reviewed")
        self.assertEqual(response.data["accession"], "A1CUJ5")

    def test_accession_endpoint_with_gene_name(self):
        response = self.client.get("/api/utils/accession/FOLH1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["endpoint"], "protein")
        self.assertEqual(response.data["source_database"], "UniProt")
        self.assertIn("proteins", response.data)
        self.assertGreater(len(response.data["proteins"]), 0)
        self.assertIn("accession", response.data["proteins"][0])
        self.assertEqual(response.data["proteins"][0]["accession"], "Q0VDM6")
        self.assertIn("organism", response.data["proteins"][0])
        self.assertIn("tax_id", response.data["proteins"][0])
        self.assertIn("is_fragment", response.data["proteins"][0])


class UtilsReleaseTest(InterproRESTTestCase):
    def test_can_read_structure_overview(self):
        response = self.client.get("/api/utils")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("available", response.data)
        self.assertIn("accession", response.data["available"])
        self.assertIn("release", response.data["available"])

    def test_release_endpoint_doesnt_fail(self):
        response = self.client.get("/api/utils/release")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_release_version_endpoint_doesnt_fail(self):
        response = self.client.get("/api/utils/release/current")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get("/api/utils/release/70.0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_release_version_endpoint_fails(self):
        response = self.client.get("/api/utils/release/x")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_the_fixtures_are_loaded(self):
        notes = Release_Note.objects.all()
        self.assertEqual(notes.count(), 2)

    def test_release_endpoint_returns_the_fixtures(self):
        notes = Release_Note.objects.all()
        response = self.client.get("/api/utils/release")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(notes))
        for note in notes:
            self.assertIn(note.version, response.data)

    def test_release_current_is_same_as_accession(self):
        response1 = self.client.get("/api/utils/release/current")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        response2 = self.client.get("/api/utils/release/70.0")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, response1.data)

    def test_release_70_is_same_as_fixture(self):
        note_version = "70.0"
        note = Release_Note.objects.all().filter(version=note_version).first()
        response = self.client.get("/api/utils/release/" + note_version)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], note.content)
