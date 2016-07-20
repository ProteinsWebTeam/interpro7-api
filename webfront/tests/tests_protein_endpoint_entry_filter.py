from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class ProteinWithFilterEntryRESTTest(InterproRESTTestCase):

    def test_can_get_protein_amount_from_entry(self):
        response = self.client.get("/api/protein/entry")
        self._check_protein_count_overview(response.data)
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self._check_entry_count_overview(response.data["entries"])

    def test_urls_that_return_list_of_accessions_and_entries(self):
        urls = [
            "/api/protein/uniprot/entry/",
            "/api/protein/swissprot/entry/",
            "/api/protein/trembl/entry/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            # self._check_is_list_of_objects_with_key(response.data["results"], "entries")

    def test_can_get_entries_from_protein_id(self):
        swissprot = "A1CUJ5"
        trembl = "P16582"
        urls = [
            "/api/protein/uniprot/"+swissprot+"/entry/",
            "/api/protein/uniprot/"+trembl+"/entry/",
            "/api/protein/swissprot/"+swissprot+"/entry/",
            "/api/protein/trembl/"+trembl+"/entry/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self._check_protein_details(response.data["metadata"])
            self._check_entry_count_overview(response.data["entries"])

    def test_gets_empty_entries_array_for_protein_with_no_matches(self):
        acc = "A0A0A2L2G2"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self._check_protein_details(response.data["metadata"])
        self._check_entry_count_overview(response.data["entries"])
        self.assertDictEqual(response.data["entries"]["member_databases"], {},
                             "there should not be reports of member db")
        self.assertEqual(response.data["entries"]["interpro"], 0, "no interpro entries")
        self.assertEqual(response.data["entries"]["unintegrated"], 0, "no unintegrated entries")

    def test_urls_that_should_fails(self):
        swissprot = "A1CUJ5"
        trembl = "P16582"
        tests = [
            "/api/protein/bad_db/entry/",
            "/api/protein/swissprot/"+trembl+"/entry/",
            "/api/protein/trembl/"+swissprot+"/entry/",
            ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")


class ProteinWithFilterEntryDatabaseRESTTest(InterproRESTTestCase):

    def test_urls_that_return_object_of_protein_and_entry_counts(self):
        acc = "IPR003165"
        urls = [
            "/api/protein/entry/interpro",
            "/api/protein/entry/pfam",
            "/api/protein/entry/unintegrated",
            "/api/protein/entry/unintegrated/pfam",
            "/api/protein/entry/unintegrated/smart",
            "/api/protein/entry/interpro/pfam",
            "/api/protein/entry/interpro/"+acc+"/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)
            for prot_db in response.data:
                self.assertIn(prot_db, ["uniprot", "swissprot", "trembl"])
                self.assertIn("proteins", response.data[prot_db])
                self.assertIn("entries", response.data[prot_db])

    def test_urls_that_return_list_of_protein_accessions_with_matches(self):
        acc = "IPR003165"
        urls = [
            "/api/protein/uniprot/entry/interpro",
            "/api/protein/swissprot/entry/interpro",
            "/api/protein/trembl/entry/interpro",
            "/api/protein/uniprot/entry/pfam",
            "/api/protein/uniprot/entry/unintegrated",
            "/api/protein/uniprot/entry/unintegrated/pfam",
            "/api/protein/uniprot/entry/unintegrated/smart",
            "/api/protein/uniprot/entry/interpro/pfam",
            "/api/protein/uniprot/entry/interpro/"+acc+"/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries",
                                                    "It should have the key 'entries' for the URL ["+url+"]")
            for protein in response.data["results"]:
                for match in protein["entries"]:
                    self._check_match(match)

    def test_urls_that_return_a_protein_details_with_matches(self):
        sp_1 = "M5ADK6"
        sp_2 = "A1CUJ5"
        acc = "IPR003165"
        urls = {
            "/api/protein/uniprot/"+sp_1+"/entry/unintegrated": ["PF17180"],
            "/api/protein/uniprot/"+sp_2+"/entry/interpro": ["IPR003165", "IPR001165"],
            "/api/protein/uniprot/"+sp_2+"/entry/pfam": ["PF17176", "PF02171"],
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/pfam": ["PF02171"],
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/smart": ["SM00950"],
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/"+acc+"/smart": ["SM00950"],
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/"+acc+"/pfam": ["PF02171"],
            "/api/protein/uniprot/"+sp_1+"/entry/unintegrated/pfam": ["PF17180"],
        }
        for url in urls:
            response = self.client.get(url)
            self._check_protein_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self.assertEqual(len(response.data["entries"]), len(urls[url]),
                             "The nember of entries dhould be the sem URL: [{}]".format(url))
            self.assertIn(response.data["entries"][0]["accession"], urls[url])

    def test_urls_that_should_fails(self):
        tr_1 = "P16582"
        sp_1 = "M5ADK6"
        tests = [
            "/api/protein/uniprot/"+tr_1+"/entry/unintegrated",
            "/api/protein/swissprot/"+tr_1+"/entry/unintegrated",
            "/api/protein/trembl/"+sp_1+"/entry/unintegrated",
            ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")


class ProteinWithFilterEntryDatabaseAccessionRESTTest(InterproRESTTestCase):

    def test_urls_that_return_object_of_protein_and_entry_counts(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        urls = [
            "/api/protein/entry/unintegrated/pfam/"+pfam_u,
            "/api/protein/entry/interpro/pfam/"+pfam,
            "/api/protein/entry/pfam/"+pfam,
            "/api/protein/entry/interpro/"+acc+"/pfam/"+pfam,
            "/api/protein/entry/interpro/"+acc,
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)
            for prot_db in response.data:
                self.assertIn(prot_db, ["uniprot", "swissprot", "trembl"])
                self.assertIn("proteins", response.data[prot_db])
                self.assertIn("entries", response.data[prot_db])

    def test_can_get_entries_from_protein_id_interpro_ids(self):
        acc = "A1CUJ5"
        ips = ["IPR001165", "IPR003165"]
        for ip in ips:
            response = self.client.get("/api/protein/uniprot/"+acc+"/entry/interpro/"+ip)
            self._check_single_entry_response(response)

    def test_urls_that_return_list_of_protein_accessions_with_matches_and_detailed_entries(self):
        acc = "IPR003165"
        pfam = "PF02171"
        smart = "SM00950"
        urls = [
            "/api/protein/uniprot/entry/interpro/"+acc,
            "/api/protein/swissprot/entry/interpro/"+acc,
            "/api/protein/trembl/entry/interpro/"+acc,
            "/api/protein/uniprot/entry/pfam/"+pfam,
            "/api/protein/uniprot/entry/unintegrated/pfam/"+pfam,
            "/api/protein/uniprot/entry/interpro/smart/"+smart,
            "/api/protein/uniprot/entry/interpro/pfam/"+pfam,
            "/api/protein/uniprot/entry/interpro/"+acc+"/pfam/"+pfam,
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries",
                                                    "It should have the key 'entries' for the URL ["+url+"]")
            for protein in response.data["results"]:
                for match in protein["entries"]:
                    self._check_match(match)
                    self._check_entry_details(match["entry"])

    def test_urls_that_return_a_protein_details_with_matches(self):
        sp_1 = "M5ADK6"
        sp_2 = "A1CUJ5"
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        smart = "SM00950"
        urls = [
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/"+acc,
            "/api/protein/uniprot/"+sp_2+"/entry/pfam/"+pfam,
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/pfam/"+pfam,
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/smart/"+smart,
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/"+acc+"/smart/"+smart,
            "/api/protein/uniprot/"+sp_2+"/entry/interpro/"+acc+"/pfam/"+pfam,
            "/api/protein/uniprot/"+sp_1+"/entry/unintegrated/pfam/"+pfam_u,
        ]
        for url in urls:
            response = self.client.get(url)
            self._check_protein_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            # self.assertEqual(len(response.data["entries"]), 1,
            #                  "The number of entries should be 1. URL: [{}]".format(url))
            self._check_match(response.data["entries"][0])
            self._check_entry_details(response.data["entries"][0]["entry"])

    def test_can_get_entries_from_protein_id_pfam_id(self):
        acc = "A1CUJ5"
        pfam = "PF02171"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO: it is returning 2 entries. FIX!!
        # self._check_single_entry_response(response)

    def test_urls_that_should_fails(self):
        tr_1 = "P16582"
        sp_1 = "M5ADK6"
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        tests = [
            "/api/protein/uniprot/"+tr_1+"/entry/unintegrated/pfam/"+pfam_u,
            "/api/protein/swissprot/"+tr_1+"/entry/unintegrated/pfam/"+pfam_u,
            "/api/protein/trembl/"+sp_1+"/entry/unintegrated/pfam/"+pfam_u,
            "/api/protein/uniprot/"+sp_1+"/entry/interpro/"+acc,
            "/api/protein/uniprot/"+sp_1+"/entry/interpro/"+acc+"/pfam/"+pfam,
            ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")
