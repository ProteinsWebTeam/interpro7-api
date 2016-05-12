from unifam import settings
from webfront.models import Entry
from rest_framework import status
from rest_framework.test import APITransactionTestCase


class InterproRESTTestCase(APITransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def _check_single_entry_response(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("entries", response.data)
        self.assertEqual(len(response.data["entries"]), 1,
                         "only one entry should be included when the ID is specified")
        self.assertIn("entry", response.data["entries"][0])
        self._check_entry_details(response.data["entries"][0]["entry"])

    def _check_entry_details(self, obj):
        self.assertIn("entry_id", obj)
        self.assertIn("type", obj)
        self.assertIn("literature", obj)
        self.assertIn("integrated", obj)
        self.assertIn("member_databases", obj)
        self.assertIn("accession", obj)

    def _check_entry_count_overview(self, obj):
        self.assertIn("member_databases", obj)
        self.assertIn("interpro", obj)
        self.assertIn("unintegrated", obj)

    def _check_is_list_of_objects_with_key(self, _list, key, msg=""):
        for obj in _list:
            self.assertIn(key, obj, msg)

    def _check_is_list_of_objects_with_accession(self, _list, msg=""):
        self._check_is_list_of_objects_with_key(_list, "accession", msg)

    def _check_HTTP_response_code(self, url, code=status.HTTP_404_NOT_FOUND, msg=""):
        prev = settings.DEBUG
        settings.DEBUG = False
        response = self.client.get(url)
        self.assertEqual(response.status_code, code, msg)
        settings.DEBUG = prev

    def _check_protein_count_overview(self, obj):
        self.assertIn("uniprot", obj)
        if obj["uniprot"] > 0:
            self.assertTrue("trembl" in obj or "swissprot" in obj,
                            "If there is a uniprot protein then it should either be reported in swissprot or trembl")

    def _check_protein_details(self, obj):
        self.assertIn("description", obj)
        self.assertIn("name", obj)
        self.assertIn("proteinEvidence", obj)
        self.assertIn("sourceOrganism", obj)
        self.assertIn("length", obj)
        self.assertIn("accession", obj)

    def _check_match(self, obj):
        self.assertIn("match_start", obj)
        self.assertIn("match_end", obj)
        self.assertIn("accession", obj)


class ModelTest(InterproRESTTestCase):

    def test_dummy_dataset_is_loaded(self):
        self.assertGreater(Entry.objects.all().count(), 0, "The dataset has to have at least one Entry")
        self.assertIn(Entry.objects.filter(source_database="interpro").first().accession, ["IPR003165", "IPR001165"])

    def test_content_of_a_json_attribute(self):
        entry = Entry.objects.get(accession="IPR003165")
        self.assertEqual(entry.member_databases["pfam"][0], "PF02171")


class EntryRESTTest(InterproRESTTestCase):
    db_members = {
        "pfam": 3,
        "smart": 2,
        "prosite_profiles": 2,
    }

    def test_can_read_entry_overview(self):
        response = self.client.get("/api/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)

    def test_can_read_entry_interpro(self):
        response = self.client.get("/api/entry/interpro")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_accession(response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_entry_unintegrated(self):
        response = self.client.get("/api/entry/unintegrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_accession(response.data["results"])
        self.assertEqual(len(response.data["results"]), 4)

    def test_can_read_entry_interpro_id(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/"+acc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_details(response.data["metadata"])

    def test_fail_entry_interpro_unknown_id(self):
        self._check_HTTP_response_code("/api/entry/interpro/IPR999999")

    def test_bad_entry_point(self):
        self._check_HTTP_response_code("/api/bad_entry_point")

    def test_can_read_entry_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), self.db_members[member])
            self._check_is_list_of_objects_with_accession(response.data["results"])

    def test_can_read_entry_interpro_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 1,
                             "The testdataset only has one interpro entry with 1 member entry")
            self._check_is_list_of_objects_with_accession(response.data["results"])
            # self._check_is_list_of_objects_with_key(response.data["results"], "proteins")

    def test_can_read_entry_unintegrated_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/unintegrated/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), self.db_members[member]-1)
            self._check_is_list_of_objects_with_accession(response.data["results"])

    def test_can_read_entry_interpro_id_member(self):
        acc = "IPR003165"
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/"+acc+"/"+member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 1)
            self._check_is_list_of_objects_with_accession(response.data["results"])

    def test_can_read_entry_interpro_id_pfam_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        response = self.client.get("/api/entry/interpro/"+acc+"/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(acc, response.data["metadata"]["integrated"])
        self._check_entry_details(response.data["metadata"])

    def test_cant_read_entry_interpro_id_pfam_id_not_in_entry(self):
        acc = "IPR003165"
        pfam = "PF17180"
        self._check_HTTP_response_code("/api/entry/interpro/"+acc+"/pfam/"+pfam)

    def test_can_read_entry_pfam_id(self):
        pfam = "PF17180"
        response = self.client.get("/api/entry/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data.keys())
        self.assertIn("proteins", response.data.keys())
        self._check_entry_details(response.data["metadata"])

    def test_can_read_entry_unintegrated_pfam_id(self):
        pfam = "PF17180"
        response = self.client.get("/api/entry/unintegrated/pfam/"+pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data.keys())
        self.assertIn("proteins", response.data.keys())
        self._check_entry_details(response.data["metadata"])

    def test_cant_read_entry_unintegrated_pfam_id_integrated(self):
        pfam = "PF02171"
        self._check_HTTP_response_code("/api/entry/unintegrated/pfam/"+pfam)

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


class ProteinRESTTest(InterproRESTTestCase):

    def test_can_read_protein_overview(self):
        response = self.client.get("/api/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_protein_count_overview(response.data)

    def test_can_read_protein_uniprot(self):
        response = self.client.get("/api/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_accession(response.data["results"])
        self.assertEqual(len(response.data["results"]), 4)

    def test_can_read_protein_uniprot_accession(self):
        response = self.client.get("/api/protein/uniprot/P16582")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self._check_protein_details(response.data["metadata"])

    def test_can_read_protein_id(self):
        url_id = "/api/protein/uniprot/CBPYA_ASPCL"
        response = self.client.get(url_id)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn("A1CUJ5", response.url)

    def test_can_read_protein_swissprot(self):
        response = self.client.get("/api/protein/swissprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_accession(response.data["results"])
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_protein_swissprot_accession(self):
        response = self.client.get("/api/protein/swissprot/A1CUJ5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self._check_protein_details(response.data["metadata"])

    def test_cant_read_protein_bad_db(self):
        self._check_HTTP_response_code("/api/protein/bad_db")

    def test_cant_read_protein_uniprot_bad_id(self):
        self._check_HTTP_response_code("/api/protein/uniprot/bad_id")


class EntryWithFilterProteinRESTTest(InterproRESTTestCase):

    def test_can_get_protein_overview_from_entry(self):
        response = self.client.get("/api/entry/protein/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        self._check_protein_count_overview(response.data["proteins"])

    def test_urls_that_return_list_of_accessions_and_proteins(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/protein/",
            "/api/entry/pfam/protein/",
            "/api/entry/unintegrated/protein/",
            "/api/entry/interpro/pfam/protein/",
            "/api/entry/unintegrated/pfam/protein/",
            "/api/entry/interpro/"+acc+"/pfam/protein",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_accession(response.data["results"])
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")

    def test_urls_that_return_entry_with_protein_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/entry/interpro/"+acc+"/protein",
            "/api/entry/pfam/"+pfam+"/protein/",
            "/api/entry/pfam/"+pfam_un+"/protein/",
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/",
            "/api/entry/unintegrated/pfam/"+pfam_un+"/protein/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_details(response.data["metadata"])
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self._check_protein_count_overview(response.data["proteins"])


class EntryWithFilterProteinUniprotRESTTest(InterproRESTTestCase):

    def test_can_get_protein_match_from_entry(self):
        response = self.client.get("/api/entry/protein/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
        uniprots = response.data["proteins"]
        response = self.client.get("/api/entry/protein/swissprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        swissprots = response.data["proteins"]
        response = self.client.get("/api/entry/protein/trembl")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        trembls = response.data["proteins"]
        self.assertEqual(uniprots, swissprots+trembls, "uniprot proteins should be equal to swissprot + trembl")

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
            for match in result["proteins"]:
                self._check_match(match)

        self.assertTrue(has_one and has_two,
                        "One of the entries should have one protein and the other one should have two")

    def test_can_get_swissprot_from_interpro_protein(self):
        response = self.client.get("/api/entry/interpro/protein/swissprot")
        self.assertEqual(len(response.data["results"]), 2)
        has_one = False
        has_two = False
        for result in response.data["results"]:
            if len(result["proteins"]) == 1:
                has_one = True
            elif len(result["proteins"]) == 2:
                has_two = True
            for match in result["proteins"]:
                self._check_match(match)
        self.assertTrue(has_one and not has_two,
                        "One of the entries should have one protein and the other one should have two")

    def test_can_get_matches_from_entries(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        smart = "SM00002"
        tests = {
            "/api/entry/interpro/"+acc+"/protein/uniprot": ["A1CUJ5", "P16582"],
            "/api/entry/interpro/"+acc+"/protein/swissprot": ["A1CUJ5"],
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/uniprot": ["A1CUJ5"],
            "/api/entry/pfam/"+pfam+"/protein/uniprot": ["A1CUJ5"],
            "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/uniprot": ["M5ADK6"],
            "/api/entry/unintegrated/smart/"+smart+"/protein/uniprot": []
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self.assertEqual(len(response.data["proteins"]), len(tests[url]))
            for match in response.data["proteins"]:
                self._check_match(match)
            ids = [x["accession"] for x in response.data["proteins"]]
            self.assertEqual(tests[url], ids)


class EntryWithFilterProteinUniprotAccessionRESTTest(InterproRESTTestCase):
    def test_can_get_proteins_from_interpro_id_protein_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        prot = "A1CUJ5"
        prot_u = "M5ADK6"

        tests = {
            "/api/entry/interpro/"+acc+"/protein/uniprot/"+prot: ["A1CUJ5"],
            "/api/entry/interpro/"+acc+"/protein/swissprot/"+prot: ["A1CUJ5"],
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/uniprot/"+prot: ["A1CUJ5"],
            "/api/entry/pfam/"+pfam+"/protein/uniprot/"+prot: ["A1CUJ5"],
            "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/uniprot/"+prot_u: ["M5ADK6"],
        }
        for url in tests:
            response = self.client.get(url)
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self.assertEqual(len(response.data["proteins"]), len(tests[url]))
            for match in response.data["proteins"]:
                self._check_match(match)
                self._check_protein_details(match["protein"])
            ids = [x["accession"] for x in response.data["proteins"]]
            self.assertEqual(tests[url], ids)

    def test_urls_that_should_fails(self):
        acc = "IPR003165"
        pfam = "PF02171"
        prot = "A1CUJ5"
        pfam_u = "PF17180"
        prot_u = "M5ADK6"
        tests = [
            "/api/entry/protein/uniprot/"+prot,
            "/api/entry/interpro/protein/uniprot/"+prot,
            "/api/entry/interpro/"+acc+"/protein/trembl/"+prot,
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/protein/trembl/"+prot,
            "/api/entry/interpro/"+acc+"/smart/"+pfam+"/protein/trembl/"+prot,
            "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/uniprot/"+prot,
            "/api/entry/unintegrated/pfam/"+pfam+"/protein/trembl/"+prot,
            "/api/entry/unintegrated/pfam/"+pfam_u+"/protein/trembl/"+prot_u,
        ]
        for url in tests:
            self._check_HTTP_response_code(url, msg="The URL ["+url+"] should've failed.")


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
            self._check_is_list_of_objects_with_accession(response.data["results"])
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")

    def test_urls_that_return_list_of_matches(self):
        urls = [
            "/api/protein/uniprot/entry/interpro",
            "/api/protein/swissprot/entry/interpro",
            "/api/protein/trembl/entry/interpro",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_accession(response.data["results"])
            self._check_is_list_of_objects_with_key(response.data["results"], "entries",
                                                    "It should have the key 'entries' for the URL ["+url+"]")
            for protein in response.data["results"]:
                for match in protein["entries"]:
                    self._check_match(match)



class ProteinEntryRESTTest(InterproRESTTestCase):
    # TODO: Organise as in the ENtry Filter Protein testcase

    def test_can_get_entries_from_protein_id(self):
        acc = "A1CUJ5"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self._check_entry_count_overview(response.data["entries"])

    def test_gets_empty_entries_array_for_protein_with_no_matches(self):
        acc = "A0A0A2L2G2"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self._check_entry_count_overview(response.data["entries"])
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
        ips = ["IPR001165", "IPR003165"]
        for ip in ips:
            response = self.client.get("/api/protein/uniprot/"+acc+"/entry/interpro/"+ip)
            self._check_single_entry_response(response)

    def test_can_get_entries_from_protein_id_pfam(self):
        acc = "A1CUJ5"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/pfam")
        self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
        self.assertEqual(len(response.data["entries"]), 2)
        ids = [x["accession"] for x in response.data["entries"]]
        self.assertIn("PF02171", ids)
        self.assertIn("PF17176", ids)

    def test_can_get_entries_from_protein_id_pfam_id(self):
        acc = "A1CUJ5"
        pfam = "PF02171"
        response = self.client.get("/api/protein/uniprot/"+acc+"/entry/pfam/"+pfam)
        self._check_single_entry_response(response)
