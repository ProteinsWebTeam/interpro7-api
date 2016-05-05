from django.test import TransactionTestCase

from unifam import settings
from webfront.models import Entry
from rest_framework import status
from rest_framework.test import APITransactionTestCase


class ModelTest(TransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def test_dummy_dataset_is_loaded(self):
        self.assertGreater(Entry.objects.all().count(), 0, "The dataset has to have at least one Entry")
        self.assertIn(Entry.objects.filter(source_database="interpro").first().accession, ["IPR003165", "IPR001165"])

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
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_entry_unintegrated(self):
        response = self.client.get("/api/entry/unintegrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

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
            self.assertEqual(len(response.data["results"]), self.db_members[member])

    def test_can_read_entry_interpro_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 1,
                             "The testdataset only has one interpro entry with 1 member entry")

    def test_can_read_entry_unintegrated_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/unintegrated/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), self.db_members[member]-1)

    def test_can_read_entry_interpro_id_member(self):
        acc = "IPR003165"
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/"+acc+"/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 1)
            # self.assertEqual(acc, response.data["results"][0]["metadata"]["integrated"])

    def test_can_read_entry_interpro_id_pfam_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        response = self.client.get("/api/entry/interpro/"+acc+"/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertIn("metadata", response.data.keys())
        self.assertIn("proteins", response.data.keys())

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

    def test_can_read_protein_uniprot_accession(self):
        response = self.client.get("/api/protein/uniprot/P16582")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)

    def test_can_read_protein_id(self):
        url_id = "/api/protein/uniprot/CBPYA_ASPCL"
        response = self.client.get(url_id)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("A1CUJ5", response.url)


class EntryProteinRESTTest(APITransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def test_can_get_protein_amount_from_interpro_id(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(response.data["proteins"], 2)

    def test_can_get_protein_amount_from_interpro_id_pfam_id(self):
        acc = "IPR003165"
        pf = "PF02171"
        response = self.client.get("/api/entry/interpro/"+acc+"/pfam/"+pf)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(response.data["proteins"], 1)

    def test_can_get_protein_overview_from_interpro_id_protein(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc+"/protein")
        self.assertIn("uniprot", response.data["proteins"])
        self.assertIn("trembl", response.data["proteins"])
        self.assertIn("swissprot", response.data["proteins"])

    def test_can_get_proteins_from_interpro_id_protein(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc+"/protein/uniprot")
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 2)
        ids = [x["accession"] for x in response.data["proteins"]]
        self.assertIn("A1CUJ5", ids)
        self.assertIn("P16582", ids)

    def test_can_get_swissprot_proteins_from_interpro_id_protein(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc+"/protein/swissprot")
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 1)
        ids = [x["accession"] for x in response.data["proteins"]]
        self.assertIn("A1CUJ5", ids)
        self.assertNotIn("P16582", ids)

    def test_can_get_proteins_from_interpro_id_protein_id(self):
        acc = "IPR003165"
        prot = "A1CUJ5"
        response = self.client.get("/api/entry/interpro/"+acc+"/protein/uniprot/"+prot)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 1)
        ids = [x["accession"] for x in response.data["proteins"]]
        self.assertIn("A1CUJ5", ids)
        self.assertNotIn("P16582", ids)

    def test_can_get_proteins_from_interpro_protein(self):
        response = self.client.get("/api/entry/interpro/protein/uniprot")
        self.assertEqual(len(response.data["results"]), 2)
        has_one = False
        has_two = False
        for result in response.data["results"]:
            if len(result["proteins"]) == 1:
                has_one = True
            elif len(result["proteins"]) == 2:
                has_two = True
        self.assertTrue(has_one and has_two,
                        "One of the entries should have one protein and the other one should have two")

    def test_fails_when_both_protein_and_entry_are_specified_but_non_existing(self):
        prev = settings.DEBUG
        settings.DEBUG = False
        acc = "IPR003165"
        tr = "A1CUJ5"
        response = self.client.get("/api/entry/interpro/"+acc+"/protein/trembl/"+tr)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        settings.DEBUG = prev

    def test_can_get_swissprot_from_interpro_protein(self):
        response = self.client.get("/api/entry/interpro/protein/swissprot")
        self.assertEqual(len(response.data["results"]), 2)
        has_one=False
        has_two=False
        for result in response.data["results"]:
            if len(result["proteins"]) == 1:
                has_one = True
            elif len(result["proteins"]) == 2:
                has_two = True
        self.assertTrue(has_one and not has_two,
                        "One of the entries should have one protein and the other one should have two")

    def test_can_get_swissprot_from_interpro_id_protein_id(self):
        acc = "IPR003165"
        uni = "A1CUJ5"
        response = self.client.get("/api/entry/interpro/"+acc+"/protein/swissprot/"+uni)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 1)
        ids = [x["accession"] for x in response.data["proteins"]]
        self.assertIn(uni, ids)
        self.assertNotIn("P16582", ids)

    def test_can_get_protein_overview_from_pfam_id(self):
        pfam = "PF02171"
        response = self.client.get("/api/entry/pfam/"+pfam+"/protein/")
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertIn("uniprot", response.data["proteins"])
        self.assertNotIn("trembl", response.data["proteins"])
        self.assertIn("swissprot", response.data["proteins"])
        # ids = [x["accession"] for x in response.data["proteins"]]
        # self.assertIn("A1CUJ5", ids)
        # self.assertNotIn("P16582", ids)

    def test_can_get_proteins_from_pfam_id(self):
        pfam = "PF02171"
        response = self.client.get("/api/entry/pfam/"+pfam+"/protein/uniprot")
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 1)
        ids = [x["accession"] for x in response.data["proteins"]]
        self.assertIn("A1CUJ5", ids)
        self.assertNotIn("P16582", ids)

    def test_can_get_proteins_from_unintegrated_pfam_id(self):
        pfam = "PF17180"
        response = self.client.get("/api/entry/unintegrated/pfam/"+pfam+"/protein/uniprot")
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 1)
        ids = [x["accession"] for x in response.data["proteins"]]
        self.assertIn("M5ADK6", ids)
        self.assertNotIn("P16582", ids)

    def test_gets_empty_protein_array_for_entry_with_no_matches(self):
        pfam = "SM00002"
        response = self.client.get("/api/entry/unintegrated/smart/"+pfam+"/protein/uniprot")
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self.assertEqual(len(response.data["proteins"]), 0)


class ProteinEntryRESTTest(APITransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def test_can_get_entries_from_protein_id(self):
        acc = "A1CUJ5"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self.assertIn("member_databases", response.data["entries"])
        self.assertIn("interpro", response.data["entries"])
        self.assertIn("unintegrated", response.data["entries"])

    def test_gets_empty_entries_array_for_protein_with_no_matches(self):
        acc = "A0A0A2L2G2"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self.assertIn("member_databases", response.data["entries"])
        self.assertIn("interpro", response.data["entries"])
        self.assertIn("unintegrated", response.data["entries"])
        self.assertDictEqual(response.data["entries"]["member_databases"], {},
                             "there should not be reports of member db")
        self.assertEqual(response.data["entries"]["interpro"], 0, "no interpro entries")
        self.assertEqual(response.data["entries"]["unintegrated"], 0, "no unintegrated entries")

    def test_can_get_entries_from_protein_id_unintegrated(self):
        acc = "M5ADK6"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/unintegrated")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self.assertEqual(len(response.data["entries"]), 1)
        self.assertEqual("PF17180", response.data["entries"][0]["accession"])

    def test_can_get_empty_entries_from_protein_id_unitegrated(self):
        acc = "P16582"
        prev = settings.DEBUG
        settings.DEBUG = False
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/unintegrated")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        settings.DEBUG = prev

    def test_can_get_entries_from_protein_id_interpro(self):
        acc = "A1CUJ5"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/interpro")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self.assertEqual(len(response.data["entries"]), 2)
        ids = [x["accession"] for x in response.data["entries"]]
        self.assertIn("IPR003165", ids)
        self.assertIn("IPR001165", ids)
        self.assertNotIn("PS50822", ids)

    def test_can_get_entries_from_protein_id_interpro_ids(self):
        acc = "A1CUJ5"
        ips = ["IPR001165","IPR003165"]
        for ip in ips:
            response = self.client.get("/api/protein/uniprot/"+acc+"/entry/interpro/"+ip)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("entries", response.data)
            self.assertEqual(len(response.data["entries"]), 1,
                             "only one entry should be included when the ID is specified")
            self.assertIn("entry", response.data["entries"][0])
            self.assertIn("entry_id", response.data["entries"][0]["entry"])
            # TODO: Check it contain details

    def test_can_get_entries_from_protein_id_pfam(self):
        acc = "A1CUJ5"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/pfam")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self.assertEqual(len(response.data["entries"]), 2)
        ids = [x["accession"] for x in response.data["entries"]]
        self.assertIn("PF02171", ids)
        self.assertIn("PF17176", ids)
        # TODO: Add fixture of an unintegrated pfam for this protein
