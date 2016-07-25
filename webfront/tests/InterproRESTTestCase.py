from interpro import settings
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

    def _check_entry_count_overview(self, main_obj):
        obj = main_obj["entries"]
        self.assertIn("member_databases", obj)
        self.assertIn("interpro", obj)
        self.assertIn("unintegrated", obj)

    def _check_is_list_of_metadata_objects(self, _list, msg=""):
        for obj in _list:
            self.assertIn("metadata", obj, msg)
            self.assertTrue(isinstance(obj, dict))
            self.assertIn("source_database", obj["metadata"], msg)
            self.assertIn("accession", obj["metadata"], msg)
            self.assertIn("name", obj["metadata"], msg)

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
    def _check_protein_count_overview(self, main_obj):
        obj = main_obj["proteins"]
        self.assertIn("uniprot", obj)
        self.assertTrue("trembl" in obj or "swissprot" in obj)

    def _check_protein_details(self, obj):
        self.assertIn("description", obj)
        self.assertIn("name", obj)
        self.assertIn("protein_evidence", obj)
        self.assertIn("source_organism", obj)
        self.assertIn("length", obj)
        self.assertIn("accession", obj)

    def _check_match(self, obj):
        self.assertIn("coordinates", obj)
        self.assertIsInstance(obj["coordinates"], list)
        self.assertIn("accession", obj)

    # methods to check structure related responses
    # TODO: Extend this tests
    def _check_structure_count_overview(self, main_obj):
        obj = main_obj["structures"]
        self.assertIn("pdb", obj)

    def _check_structure_details(self, obj):
        self.assertIn("chains", obj)
        self.assertIn("accession", obj)

    def _check_structure_chain_details(self, obj):
        self.assertIn("coordinates", obj)
        self.assertIn("length", obj)
        self.assertIn("organism", obj)

    def _check_entry_structure_details(self, obj):
        self.assertIn("coordinates", obj)
        self.assertIn("chain", obj)

    def _check_counter_by_endpoint(self, endpoint, obj):
        if "entry" == endpoint:
            self._check_entry_count_overview(obj)
        elif "protein" == endpoint:
            self._check_protein_count_overview(obj)
        elif "structure" == endpoint:
            self._check_structure_count_overview(obj)

    def _check_object_by_accesssion(self, obj):
        self.assertIn("metadata", obj)
        self.assertIn("source_database", obj["metadata"])
        self.assertIn("accession", obj["metadata"])
        self.assertIn("counters", obj["metadata"])
        self.assertIn("name", obj["metadata"])
