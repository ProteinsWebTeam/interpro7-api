from django.test import TransactionTestCase
from webfront.models import Entry
from rest_framework import status
from rest_framework.test import APITransactionTestCase


class ModelTest(TransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json']

    def test_dummy_dataset_is_loaded(self):
        self.assertGreater(Entry.objects.all().count(), 0, "The dataset has to have at least one Entry")
        self.assertEqual(Entry.objects.filter(source_database="interpro").first().accession, "IPR003165")

    def test_content_of_a_json_attribute(self):
        entry = Entry.objects.get(id="id1")
        self.assertEqual(entry.member_databases["pfam"][0], "PF02171")


class EntryRESTTest(APITransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json']

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
        self.assertEqual(len(response.data), 2)

    def test_can_read_entry_interpro_id(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(acc, response.data["metadata"]["accession"])

    def test_fail_entry_interpro_unknown_id(self):
        response = self.client.get("/api/entry/interpro/IPR999999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_entry_point(self):
        response = self.client.get("/api/bad_entry_point")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_read_entry_pfam(self):
        response = self.client.get("/api/entry/pfam")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
