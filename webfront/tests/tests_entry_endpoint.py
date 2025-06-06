from webfront.models import Entry
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from rest_framework import status
from webfront.views.common import map_url_to_levels


class ModelTest(InterproRESTTestCase):
    def test_dummy_dataset_is_loaded(self):
        self.assertGreater(
            Entry.objects.all().count(), 0, "The dataset has to have at least one Entry"
        )
        self.assertIn(
            Entry.objects.filter(source_database="interpro").first().accession.upper(),
            ["IPR003165", "IPR001165", "IPR000005"],
        )

    def test_content_of_a_json_attribute(self):
        entry = Entry.objects.get(accession__iexact="ipr003165")
        self.assertTrue("pfam" in entry.member_databases)
        self.assertTrue("PF02171" in entry.member_databases["pfam"])
        self.assertTrue("Piwi domain" in entry.member_databases["pfam"]["PF02171"])

    def test_url_mapper(self):
        urls = {
            "entry/protein/structure": "entry/structure/protein",
            "/entry/protein/structure": "entry/structure/protein",
            "entry/protein/uniprot/M5ADK6/structure": "entry/structure/protein/uniprot/M5ADK6",
            "entry/protein/structure/pdb": "entry/protein/structure/pdb",
            "entry/interpro/protein/structure": "entry/interpro/structure/protein",
            "entry/interpro/protein/uniprot/structure": "entry/interpro/structure/protein/uniprot",
        }
        for url in urls:
            self.assertEqual(urls[url].split("/"), map_url_to_levels(url))


class EntryRESTTest(InterproRESTTestCase):
    db_members = {"pfam": 3, "smart": 2, "profile": 2}

    def test_can_read_entry_overview(self):
        response = self.client.get("/api/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)

    def test_can_read_entry_interpro(self):
        response = self.client.get("/api/entry/interpro")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 2)

    def test_check_interpro_llm_as_extra_field(self):
        def _check_llm_flags(obj):
            self.assertIn("extra_fields", obj.keys())
            self.assertIn("is_llm", obj["extra_fields"])
            self.assertIn("is_reviewed_llm", obj["extra_fields"])
            self.assertIn("is_updated_llm", obj["extra_fields"])
            # the only entry in the fixtures with these values as true
            is_llm = obj["metadata"]["accession"] == "IPR003165"
            self.assertEqual(
                obj["extra_fields"]["is_llm"],
                is_llm,
            )
            self.assertEqual(
                obj["extra_fields"]["is_reviewed_llm"],
                is_llm,
            )
            self.assertEqual(
                obj["extra_fields"]["is_updated_llm"],
                is_llm,
            )

        response = self.client.get(
            "/api/entry/interpro?extra_fields=is_llm,is_reviewed_llm,is_updated_llm"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(
            response.data["results"], "metadata", extra_checks_fn=_check_llm_flags
        )
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_entry_unintegrated(self):
        response = self.client.get("/api/entry/unintegrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 8)

    def test_can_read_entry_interpro_id(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/" + acc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_details(response.data["metadata"])

    def test_fail_entry_interpro_unknown_id(self):
        self._check_HTTP_response_code(
            "/api/entry/interpro/IPR999999", code=status.HTTP_204_NO_CONTENT
        )

    def test_deleted_entry(self):
        url = "/api/entry/interpro/IPR000005"
        self._check_HTTP_response_code(url, code=status.HTTP_410_GONE)
        response = self.client.get(url)
        self.assertIn("history", response.data)

    def test_bad_entry_point(self):
        self._check_HTTP_response_code(
            "/api/bad_entry_point", code=status.HTTP_404_NOT_FOUND
        )

    def test_can_read_entry_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/" + member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), self.db_members[member])
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )

    def test_can_read_entry_interpro_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/interpro/" + member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                len(response.data["results"]),
                1,
                "The testdataset only has one interpro entry with 1 member entry",
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            # self._check_is_list_of_objects_with_key(response.data["results"], "proteins")

    def test_can_read_entry_unintegrated_member(self):
        for member in self.db_members:
            response = self.client.get("/api/entry/unintegrated/" + member)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), self.db_members[member] - 1)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )

    def test_can_read_entry_interpro_id_member(self):
        acc = "IPR003165"
        for member in self.db_members:
            current = "/api/entry/interpro/" + acc + "/" + member
            response = self.client.get(current)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                "OK NOT OK: {}".format(current),
            )
            self.assertEqual(len(response.data["results"]), 1)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )

    def test_can_read_entry_interpro_id_pfam_id(self):
        acc = "IPR003165"
        pfam = "PF02171"
        response = self.client.get("/api/entry/interpro/" + acc + "/pfam/" + pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(acc.lower(), response.data["metadata"]["integrated"].lower())
        self._check_entry_details(response.data["metadata"])

    def test_cant_read_entry_interpro_id_pfam_id_not_in_entry(self):
        acc = "IPR003165"
        pfam = "PF17180"
        self._check_HTTP_response_code(
            "/api/entry/interpro/" + acc + "/pfam/" + pfam,
            code=status.HTTP_204_NO_CONTENT,
        )

    def test_can_read_entry_pfam_id(self):
        pfam = "PF17180"
        response = self.client.get("/api/entry/pfam/" + pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data.keys())
        self.assertIn("counters", response.data["metadata"].keys())
        self.assertIn("proteins", response.data["metadata"]["counters"].keys())
        self.assertIn("entry_annotations", response.data["metadata"].keys())
        self.assertIsInstance(response.data["metadata"]["entry_annotations"], dict)
        for k, v in response.data["metadata"]["entry_annotations"].items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, int)
        self._check_entry_details(response.data["metadata"])

    def test_can_read_entry_unintegrated_pfam_id(self):
        pfam = "PF17180"
        response = self.client.get("/api/entry/unintegrated/pfam/" + pfam)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data.keys())
        self.assertIn("counters", response.data["metadata"].keys())
        self.assertIn("proteins", response.data["metadata"]["counters"].keys())
        self._check_entry_details(response.data["metadata"])

    def test_cant_read_entry_unintegrated_pfam_id_integrated(self):
        pfam = "PF02171"
        self._check_HTTP_response_code(
            "/api/entry/unintegrated/pfam/" + pfam, code=status.HTTP_204_NO_CONTENT
        )

    def test_can_get_protein_amount_from_interpro_id(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/interpro/" + acc)
        self.assertIn(
            "counters",
            response.data["metadata"],
            "'proteins' should be one of the keys in the response",
        )
        self.assertEqual(response.data["metadata"]["counters"]["proteins"], 2)

    def test_can_get_protein_amount_from_interpro_id_pfam_id(self):
        acc = "IPR003165"
        pf = "PF02171"
        response = self.client.get("/api/entry/interpro/" + acc + "/pfam/" + pf)
        self.assertIn(
            "counters",
            response.data["metadata"],
            "'proteins' should be one of the keys in the response",
        )
        self.assertEqual(response.data["metadata"]["counters"]["proteins"], 1)

    def test_entry_llm_description_removed(self):
        response = self.client.get("/api/entry/panther/PTHR10000/")
        meta = response.data["metadata"]
        self.assertTrue("llm_description" not in meta)


class ReplaceTIGRFamsTest(InterproRESTTestCase):
    def test_can_read_ncbifam(self):
        urls = [
            "/api/entry/ncbifam",
            "/api/entry/ncbifam/nf000004",
            "/api/protein/uniprot/entry/ncbifam/nf000004",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_redirect_db(self):
        urls = [
            "/api/entry/tigrfams",
            "/api/entry/tigrfams/nf000004",
            "/api/protein/uniprot/entry/tigrfams/nf000004",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertRedirects(
                response,
                url.replace("tigrfams", "ncbifam"),
                status_code=302,
                target_status_code=200,
                fetch_redirect_response=True,
            )
