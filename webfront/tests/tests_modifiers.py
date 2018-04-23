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

    def test_can_get_the_entry_type_groups_proteins_by_tax_id(self):
        response = self.client.get("/api/protein?group_by=tax_id")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({}, response.data)

    def test_can_group_interpro_entries_with_member_databases(self):
        response = self.client.get("/api/entry/interpro?group_by=member_databases")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pfam", response.data)
        self.assertIn("smart", response.data)
        self.assertIn("profile", response.data)

    def test_wrong_field_for_group_by_should_fail(self):
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
            self.assertEqual(result["metadata"]["integrated"].lower(), acc.lower())

    def test_fails_filtering_interpro_by_integrated(self):
        self._check_HTTP_response_code(
            "/api/entry/interpro?integrated=IPR003165", code=status.HTTP_204_NO_CONTENT
        )

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
        payload_accs = [r["metadata"]["integrated"] for r in response.data["results"]]
        response = self.client.get("/api/entry/pfam?sort_by=-integrated")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        payload_accs_rev = [r["metadata"]["integrated"] for r in response.data["results"]]
        self.assertEqual(payload_accs_rev, list(reversed(payload_accs)))


class InterProStatusModifierTest(InterproRESTTestCase):

    def test_can_apply_interpro_status(self):
        mdbs = ["profile", "smart", "pfam"]
        for db in mdbs:
            response = self.client.get("/api/entry/"+db)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            unintegrated = len([
                r["metadata"]["integrated"]
                for r in response.data["results"]
                if r["metadata"]["integrated"] is None
            ])
            response2 = self.client.get("/api/entry/"+db+"?interpro_status")
            self.assertEqual(response2.status_code, status.HTTP_200_OK)
            self.assertEqual(response2.data["unintegrated"], unintegrated)
            self.assertEqual(response2.data["integrated"],
                             len(response.data["results"]) - unintegrated)


class IDAModifiersTest(InterproRESTTestCase):

    def test_ida_modifier(self):
        response = self.client.get("/api/entry/interpro/IPR001165?ida")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], len(response.data["results"]))

    def test_ida_modifier_paginated(self):
        response = self.client.get("/api/entry/interpro/IPR003165?ida&page_size=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertGreater(response.data["count"], len(response.data["results"]))
        first_ida_fk = response.data["results"][0]["IDA_FK"]
        response = self.client.get("/api/entry/interpro/IPR003165?ida&page_size=1&page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(first_ida_fk, response.data["results"][0]["IDA_FK"])

    def test_filter_by_ida_modifier(self):
        response = self.client.get("/api/protein/uniprot?ida=50134")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual("a1cuj5", response.data["results"][0]["metadata"]["accession"].lower())


class ExtraFieldsModifierTest(InterproRESTTestCase):
    fields = {
        "entry": [
          'entry_id', 'accession', 'type', 'name', 'short_name', 'source_database', 'member_databases', 'go_terms',
          'description', 'wikipedia', 'literature', 'hierarchy', 'cross_references', 'entry_date', 'is_featured'
        ],
        "protein": [
          'accession', 'identifier', 'organism', 'name', 'other_names', 'description', 'sequence', 'length', 'proteomes', 'gene', 'go_terms',
          'evidence_code', 'source_database', 'residues', 'structure', 'fragment', 'tax_id'
        ],
        'structure': [
            'accession', 'name', 'short_name', 'other_names', 'experiment_type', 'release_date', 'literature', 'chains',
            'source_database', 'resolution'
        ],
        'organism': [
            'accession', 'scientific_name', 'full_name', 'lineage', 'rank', 'children', 'left_number', 'right_number'
        ],
        'set': [
            'accession', 'name', 'description', 'source_database', 'integrated', 'relationships'
        ],
    }
    list_url = {
        "entry": "/entry/interpro",
        "protein": "/protein/uniprot",
        "structure": "/structure/pdb",
        "organism": "/organism/taxonomy",
        "set": "/set/pfam",
    }

    def test_extra_fields(self):
        for endpoint in self.fields:
            for field in self.fields[endpoint]:
                url = "/api{}?extra_fields={}".format(self.list_url[endpoint], field)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK, url)
                self.assertIn("results", response.data)
                for result in response.data["results"]:
                    self.assertIn("extra_fields", result)
                    self.assertIn(field, result["extra_fields"])
            url = "/api{}?extra_fields=ERROR".format(self.list_url[endpoint])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_extra_fields_together(self):
        for endpoint in self.fields:
            url = "/api{}?extra_fields={}".format(self.list_url[endpoint], ",".join(self.fields[endpoint]))
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, url)
            self.assertIn("results", response.data)
            for field in self.fields[endpoint]:
                for result in response.data["results"]:
                    self.assertIn("extra_fields", result)
                    self.assertIn(field, result["extra_fields"])
            url = "/api{}?extra_fields=name,ERROR".format(self.list_url[endpoint])
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_extra_fields_with_other_endpoint(self):
        for endpoint in self.fields:
            other_ep = [ep for ep in self.fields if ep != endpoint]
            for ep in other_ep:
                for field in self.fields[endpoint]:
                    url = "/api{}/{}?extra_fields={}".format(self.list_url[endpoint], ep, field)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status.HTTP_200_OK, url)
                    self.assertIn("results", response.data)
                    for result in response.data["results"]:
                        self.assertIn("extra_fields", result)
                        self.assertIn(field, result["extra_fields"])
                url = "/api{}/{}?extra_fields=name,ERROR".format(self.list_url[endpoint], ep)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
