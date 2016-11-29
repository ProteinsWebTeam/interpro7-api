import haystack
from django.test import override_settings

from interpro import settings
from rest_framework.test import APITransactionTestCase
from rest_framework import status

from webfront.tests.fixtures_reader import FixtureReader

chains = {
    "1JM7": ["A", "B"],
    "1T2V": ["A", "B", "C", "D", "E"],
    "2BKM": ["A", "B"],
    "1JZ8": ["A", "B"],
}

TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/interpro7',
    },
}


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class InterproRESTTestCase(APITransactionTestCase):
    fixtures = [
        'webfront/tests/fixtures.json',
        'webfront/tests/protein_fixtures.json',
        'webfront/tests/structure_fixtures.json'
    ]

    @classmethod
    def setUpClass(cls):
        super(InterproRESTTestCase, cls).setUpClass()
        haystack.connections.reload('default')
        fr = FixtureReader(cls.fixtures)
        fr.get_solr_fixtures()

    # @classmethod
    # def tearDownClass(cls):
    #     haystack.connections['default'].get_backend().clear()
    #     super(InterproRESTTestCase, cls).tearDownClass()

    # methods to check entry related responses
    def _check_single_entry_response(self, response, msg=""):
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)
        self.assertIn("entries", response.data, msg)
        self.assertEqual(len(response.data["entries"]), 1,
                         "only one entry should be included when the ID is specified" + msg)
        self.assertIn("entry", response.data["entries"][0], msg)
        self._check_entry_details(response.data["entries"][0]["entry"], msg)

    def _check_entry_details(self, obj, msg=""):
        self.assertIn("entry_id", obj, msg)
        self.assertIn("type", obj, msg)
        self.assertIn("literature", obj, msg)
        self.assertIn("integrated", obj, msg)
        self.assertIn("member_databases", obj, msg)
        self.assertIn("accession", obj, msg)

    def _check_entry_count_overview(self, main_obj, msg=""):
        obj = main_obj["entries"]
        self.assertIn("member_databases", obj, msg)
        self.assertIn("interpro", obj, msg)
        self.assertIn("unintegrated", obj, msg)

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

    def _check_HTTP_response_code(self, url, code=status.HTTP_204_NO_CONTENT, msg=""):
        prev = settings.DEBUG
        settings.DEBUG = False
        response = self.client.get(url)
        self.assertEqual(response.status_code, code, msg)
        settings.DEBUG = prev

    def _get_in_debug_mode(self, url):
        prev = settings.DEBUG
        settings.DEBUG = False
        response = self.client.get(url)
        settings.DEBUG = prev
        return response

    # methods to check protein related responses
    def _check_protein_count_overview(self, main_obj, msg=""):
        obj = main_obj["proteins"]
        self.assertIn("uniprot", obj, msg)
        if (isinstance(obj["uniprot"], int) and obj["uniprot"] > 0) or \
            (isinstance(obj["uniprot"], dict) and
             isinstance(obj["uniprot"]["proteins"], int) and
             obj["uniprot"]["proteins"] > 0):
            self.assertTrue("trembl" in obj or "swissprot" in obj, msg)

    def _check_protein_details(self, obj):
        self.assertIn("description", obj)
        self.assertIn("name", obj)
        self.assertIn("protein_evidence", obj)
        self.assertIn("source_organism", obj)
        self.assertIn("length", obj)
        self.assertIn("accession", obj)

    def _check_match(self, obj, msg=""):
        self.assertIn("coordinates", obj, msg)
        self.assertIsInstance(obj["coordinates"], list, msg)
        self.assertIn("accession", obj, msg)
        self.assertIn("source_database", obj, msg)

    def _check_list_of_matches(self, obj, msg=""):
        for match in obj:
            self._check_match(match, msg)

    # methods to check structure related responses
    # TODO: Extend this tests
    def _check_structure_count_overview(self, main_obj, msg=""):
        obj = main_obj["structures"]
        self.assertIn("pdb", obj, msg)

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

    def _check_counter_by_endpoint(self, endpoint, obj, msg=""):
        if "entry" == endpoint:
            self._check_entry_count_overview(obj, msg)
        elif "protein" == endpoint:
            self._check_protein_count_overview(obj, msg)
        elif "structure" == endpoint:
            self._check_structure_count_overview(obj, msg)

    def _check_object_by_accesssion(self, obj, msg=""):
        self.assertIn("metadata", obj, msg)
        self.assertIn("source_database", obj["metadata"], msg)
        self.assertIn("accession", obj["metadata"], msg)
        self.assertIn("counters", obj["metadata"], msg)
        self.assertIn("name", obj["metadata"], msg)

    def _check_count_overview_per_endpoints(self, obj, endpoints1, endpoints2, msg=""):
        for inner_obj in obj[endpoints2]:
            if inner_obj in ["interpro", "unintegrated", "uniprot", "swissprot", "trembl", "pdb"]:
                self.assertIn(endpoints1,
                              obj[endpoints2][inner_obj],
                              msg)
                self.assertIn(endpoints2,
                              obj[endpoints2][inner_obj],
                              msg)

    def _check_structure_and_chains(self, response, endpoint, db, acc, postfix="", key=None):
        urls = []
        if "structure" == endpoint:
            # _chains = [list(ch.keys())[0] for ch in chains[acc]]
            self.assertEqual(chains[acc], response.data["metadata"]["chains"])
            for chain in chains[acc]:
                current = "/api/"+endpoint+"/"+db+"/"+acc+"/"+chain+postfix
                urls.append(current)
                response_acc = self._get_in_debug_mode(current)
                if response_acc.status_code == status.HTTP_200_OK:
                    self.assertEqual(response_acc.status_code, status.HTTP_200_OK)
                    self._check_object_by_accesssion(response_acc.data)
                    self.assertEqual(len(response_acc.data["metadata"]["chains"]), 1)
                    if key is not None:
                        for ch2 in response_acc.data[key]:
                            self.assertEqual(ch2["chain"], chain)
                    self.assertIn(chain, response_acc.data["metadata"]["chains"])
                    self._check_match(response_acc.data["metadata"]["chains"][chain])
                elif response_acc.status_code != status.HTTP_204_NO_CONTENT:
                    self.client.get(current)
        return urls

    def _check_structure_chains_as_counter_filter(self, endpoint, db, acc, prefix="", postfix="", key1=None, key2=None):
        urls = []
        if "structure" == endpoint:
            for chain in chains[acc]:
                current = "/api/"+prefix+"/"+endpoint+"/"+db+"/"+acc+"/"+chain+postfix
                urls.append(current)
                response = self._get_in_debug_mode(current)
                if response.status_code == status.HTTP_200_OK:
                    self._check_counter_by_endpoint(prefix, response.data, "URL : [{}]".format(current))
                    self._check_count_overview_per_endpoints(response.data, key1, key2,
                                                             "URL : [{}]".format(current))
                elif response.status_code != status.HTTP_204_NO_CONTENT:
                    self.client.get(current)
        return urls

    def _check_structure_chains_as_filter(self, endpoint, db, acc, prefix="", postfix="", key1=None):
        urls = []
        if "structure" == endpoint:
            for chain in chains[acc]:
                current = "/api/"+prefix+"/"+endpoint+"/"+db+"/"+acc+"/"+chain+postfix
                urls.append(current)
                response = self._get_in_debug_mode(current)
                if response.status_code == status.HTTP_200_OK:
                    obj = [response.data] if "structures" in response.data else response.data["results"]
                    self._check_is_list_of_metadata_objects(obj)
                    for result in [x[key1] for x in obj if key1 in x]:
                        self._check_list_of_matches(result, "URL : [{}]".format(current))
                        self.assertGreaterEqual(len(result), 1)
                        for r in result:
                            self.assertEqual(r["chain"], chain)

                elif response.status_code != status.HTTP_204_NO_CONTENT:
                    self.client.get(current)
        return urls
    
    def assertSubset(self, subset, superset, proper=False):
        self.assertLessEqual(
            len(subset),
            len(superset),
            "Can't be subset if more elements in subset than in set"
        )
        for element in subset:
            self.assertIn(
                element,
                superset,
                "Element {} in subset but not in set".format(element)
            )
