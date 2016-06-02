from unifam import settings
from rest_framework.test import APITransactionTestCase
from rest_framework import status


class InterproRESTTestCase(APITransactionTestCase):
    fixtures = [
        'webfront/tests/fixtures.json',
        'webfront/tests/protein_fixtures.json',
        'webfront/tests/structure_fixtures.json'
    ]

    # methods to check entry related responses
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

    # methods to check protein related responses
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
        self.assertIn("match", obj)
        self.assertIsInstance(obj["match"], list)
        self.assertIn("accession", obj)

    # methods to check structure related responses
    # TODO: Extend this tests
    def _check_structure_count_overview(self, obj):
        self.assertIn("pdb", obj)

    def _check_structure_details(self, obj):
        self.assertIn("chains", obj)
        self.assertIn("accession", obj)

    def _check_structure_chain_details(self, obj):
        self.assertIn("start_residue", obj)
        self.assertIn("stop_residue", obj)
        self.assertIn("length", obj)
        self.assertIn("organism", obj)
