from django.test import TransactionTestCase

from unifam import settings
from webfront.models import Entry
from rest_framework import status
from rest_framework.test import APITransactionTestCase


class ModelTest(TransactionTestCase):
    #fixtures = ['webfront/tests/fixtures.json']
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def test_dummy_dataset_is_loaded(self):
        self.assertGreater(Entry.objects.all().count(), 0, "The dataset has to have at least one Entry")
        self.assertEqual(Entry.objects.filter(source_database="interpro").first().accession, "IPR003165")

    def test_content_of_a_json_attribute(self):
        entry = Entry.objects.get(accession="IPR003165")
        self.assertEqual(entry.member_databases["pfam"][0], "PF02171")


class EntryRESTTest(APITransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']
    db_members = {
        "pfam": 3,
        "smart": 2,
        "prosite_profiles": 2,
    }

    def test_can_read_entry_overview(self):
        response = self.client.get("/api/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("member_databases", response.data)
        self.assertIn("interpro", response.data)
        self.assertIn("unintegrated", response.data)

    def test_can_read_entry_interpro(self):
        response = self.client.get("/api/entry/interpro")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_can_read_entry_unintegrated(self):
        response = self.client.get("/api/entry/unintegrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_can_read_entry_interpro_id(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(acc, response.data["metadata"]["accession"])

    def test_fail_entry_interpro_unknown_id(self):
        prev = settings.DEBUG
        settings.DEBUG = False
        response = self.client.get("/api/entry/interpro/IPR999999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        settings.DEBUG = prev

    def test_bad_entry_point(self):
        prev = settings.DEBUG
        settings.DEBUG = False
        response = self.client.get("/api/bad_entry_point")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        settings.DEBUG = prev

    def test_can_read_entry_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), self.db_members[member])

    def test_can_read_entry_interpro_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1, "The dataset only has one interpro entry with 1 member entry")

    def test_can_read_entry_unintegrated_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/unintegrated/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), self.db_members[member]-1)

    def test_can_read_entry_interpro_id_member(self):
        acc = "IPR003165"
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/"+acc+"/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(acc, response.data[0]["metadata"]["integrated"])

    def test_can_read_entry_interpro_id_pfam_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        response = self.client.get("/api/entry/interpro/"+acc+"/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(acc, response.data["metadata"]["integrated"])

    def test_cant_read_entry_interpro_id_pfam_id_not_in_entry(self):
        prev = settings.DEBUG
        settings.DEBUG = False
        acc = "IPR003165"
        pfam = "PF17180"
        response = self.client.get("/api/entry/interpro/"+acc+"/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        settings.DEBUG = prev

    def test_can_read_entry_unintegrated_pfam_id(self):
        pfam = "PF17180"
        response = self.client.get("/api/entry/unintegrated/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_cant_read_entry_unintegrated_pfam_id_integrated(self):
        prev = settings.DEBUG
        settings.DEBUG = False
        pfam = "PF02171"
        response = self.client.get("/api/entry/unintegrated/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        settings.DEBUG = prev


class ProteinRESTTest(APITransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def test_can_read_protein_overview(self):
        response = self.client.get("/api/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("uniprot", response.data)

    def test_can_read_protein_uniprot(self):
        response = self.client.get("/api/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_can_read_protein_uniprot_id(self):
        response = self.client.get("/api/protein/uniprot/P16582")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)

