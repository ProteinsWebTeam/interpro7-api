from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from rest_framework import status


class GroupByModifierTest(InterproRESTTestCase):

    def test_can_get_the_entry_type_groups(self):
        response = self.client.get("/api/entry?group_by=type")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("domain", response.data)
        self.assertIn("family", response.data)

    def test_can_get_the_entry_type_groups_of_entries_with_proteins(self):
        response = self.client.get("/api/entry/protein?group_by=type")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("domain", response.data)
        self.assertNotIn("family", response.data)

    def test_can_group_interpro_entries_with_member_databases(self):
        response = self.client.get("/api/entry/interpro?group_by=member_databases")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pfam", response.data)
        self.assertIn("smart", response.data)
        self.assertIn("prosite_profiles", response.data)

    def test_wrong_field_fro_group_by_should_fail(self):
        self._check_HTTP_response_code("/api/entry?group_by=entry_type", code=status.HTTP_404_NOT_FOUND)


class FilterByFieldModifierTest(InterproRESTTestCase):

    def test_can_filter_pfam_by_integrated(self):
        acc = "IPR003165"
        response = self.client.get("/api/entry/pfam?integrated="+acc)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        for result in response.data["results"]:
            self.assertEqual(result["metadata"]["integrated"], acc)

    def test_fails_filtering_interpro_by_integrated(self):
        self._check_HTTP_response_code("/api/entry/interpro?integrated=IPR003165", code=status.HTTP_404_NOT_FOUND)

    def test_can_filter_smart_by_type(self):
        entry_types = ["family", "domain"]
        for entry_type in entry_types:
            response = self.client.get("/api/entry/smart?type="+entry_type)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("count", response.data)
            self.assertEqual(response.data["count"], 1)
            self.assertIn("results", response.data)
            for result in response.data["results"]:
                self.assertEqual(result["metadata"]["type"], entry_type)


class FilterByContainsFieldModifierTest(InterproRESTTestCase):

    def test_can_filter_pfam_by_signature_in(self):
        db = "pfam"
        response = self.client.get("/api/entry/interpro?signature_in="+db)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        for result in response.data["results"]:
            self.assertIn(db, result["metadata"]["member_databases"])

    # def test_fails_filtering_pfam_by_signature_in(self):
    #     self._check_HTTP_response_code("/api/entry/pfam?signature_in=pfam", code=status.HTTP_404_NOT_FOUND)


class SortByModifierTest(InterproRESTTestCase):

    def test_can_sort_pfam_by_accession(self):
        response = self.client.get("/api/entry/pfam?sort_by=accession")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        payload_accs = [r["metadata"]["accession"] for r in response.data["results"]]
        self.assertEqual(payload_accs, sorted(payload_accs))

    def test_can_sort_pfam_by_integrated_and_reverse_sorting(self):
        response = self.client.get("/api/entry/pfam?sort_by=integrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        payload_accs = [r["metadata"]["accession"] for r in response.data["results"]]
        response = self.client.get("/api/entry/pfam?sort_by=-integrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        payload_accs_rev = [r["metadata"]["accession"] for r in response.data["results"]]
        self.assertEqual(payload_accs_rev, list(reversed(payload_accs)))


class InterProStatusModifierTest(InterproRESTTestCase):

    def test_can_apply_interpro_status(self):
        mdbs = ["prosite_profiles", "smart", "pfam"]
        for db in mdbs:
            response = self.client.get("/api/entry/"+db)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            unintegrated = len([r["metadata"]["integrated"]
                            for r in response.data["results"]
                            if r["metadata"]["integrated"] is None
                            ])
            response2 = self.client.get("/api/entry/"+db+"?interpro_status")
            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertEqual(response2.data["unintegrated"], unintegrated)
            self.assertEqual(response2.data["integrated"],
                             len(response.data["results"]) - unintegrated)

