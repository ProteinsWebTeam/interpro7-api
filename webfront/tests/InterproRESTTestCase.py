from django.test import override_settings

from django.conf import settings
from rest_framework.test import APITransactionTestCase
from rest_framework import status

from webfront.models import TaxonomyPerEntry
from webfront.serializers.content_serializers import ModelContentSerializer
from webfront.tests.fixtures_reader import FixtureReader
from django.core.validators import URLValidator

plurals = ModelContentSerializer.plurals

validateURL = URLValidator()

chains = {
    "1JM7": ["A", "B"],
    "1T2V": ["A", "B", "C", "D", "E"],
    "2BKM": ["A", "B"],
    "1JZ8": ["A", "B"],
}


@override_settings(SEARCHER_URL=settings.SEARCHER_TEST_URL)
@override_settings(SEARCHER_PASSWORD=settings.SEARCHER_TEST_PASSWORD)
@override_settings(SEARCHER_INDEX="test")
class InterproRESTTestCase(APITransactionTestCase):
    fixtures = [
        "webfront/tests/fixtures_entry.json",
        "webfront/tests/fixtures_protein.json",
        "webfront/tests/fixtures_structure.json",
        "webfront/tests/fixtures_organisms.json",
        "webfront/tests/fixtures_set.json",
        "webfront/tests/fixtures_database.json",
        "webfront/tests/fixtures_entryannotation.json",
    ]
    links_fixtures = "webfront/tests/relationship_features.json"

    @classmethod
    def setUpClass(cls):
        super(InterproRESTTestCase, cls).setUpClass()
        cls.fr = FixtureReader(cls.fixtures + [cls.links_fixtures])
        cls.docs = cls.fr.get_fixtures()
        cls.fr.add_to_search_engine(cls.docs)

    @classmethod
    def tearDownClass(cls):
        # cls.fr.clear_search_engine()
        super(InterproRESTTestCase, cls).tearDownClass()

    def setUp(self):
        if TaxonomyPerEntry.objects.all().count() == 0:
            self.fr.generate_tax_per_entry_fixtures(self.docs)
            self.fr.generate_proteom_per_entry_fixtures(self.docs)

    # methods to check entry related responses
    def _check_single_entry_response(self, response, msg=""):
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)
        self.assertIn("entries", response.data, msg)
        self.assertEqual(
            len(response.data["entries"]),
            1,
            f"only one entry should be included when the ID is specified{msg}",
        )
        # self.assertIn("entry", response.data["entries"][0], msg)
        # self._check_entry_details(response.data["entries"][0]["entry"], msg)

    def _check_entry_details(self, obj, msg=""):
        self.assertIn("entry_id", obj, msg)
        self.assertIn("type", obj, msg)
        self.assertIn("literature", obj, msg)
        self.assertIn("integrated", obj, msg)
        self.assertIn("member_databases", obj, msg)
        self.assertIn("accession", obj, msg)
        self.assertIn("counters", obj, msg)

    def _check_entry_from_searcher(self, obj, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("entry_protein_locations", obj, msg)
        self.assertIn("protein_length", obj, msg)
        self.assertIn("source_database", obj, msg)
        self.assertIn("entry_type", obj, msg)
        self.assertIn("entry_integrated", obj, msg)

    def _check_entry_count_overview(self, main_obj, msg=""):
        obj = main_obj["entries"]
        self.assertIn("member_databases", obj, msg)
        self.assertIn("interpro", obj, msg)
        self.assertIn("unintegrated", obj, msg)

    def _check_is_list_of_metadata_objects(self, _list, msg=""):
        for obj in _list:
            self.assertIn("metadata", obj, msg)
            self.assertTrue(isinstance(obj, dict))
            if (
                "children" not in obj["metadata"]
                and "is_reference" not in obj["metadata"]
            ):
                self.assertIn("source_database", obj["metadata"], msg)
            self.assertIn("accession", obj["metadata"], msg)
            self.assertIn("name", obj["metadata"], msg)

    def _check_is_list_of_objects_with_key(
        self, _list, key, msg="", extra_checks_fn=None
    ):
        for obj in _list:
            self.assertIn(key, obj, msg)
            if extra_checks_fn is not None:
                extra_checks_fn(obj)

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
        if (isinstance(obj["uniprot"], int) and obj["uniprot"] > 0) or (
            isinstance(obj["uniprot"], dict)
            and isinstance(obj["uniprot"]["proteins"], int)
            and obj["uniprot"]["proteins"] > 0
        ):
            self.assertTrue("unreviewed" in obj or "reviewed" in obj, msg)

    def _check_protein_details(self, obj):
        self.assertIn("description", obj)
        self.assertIn("name", obj)
        self.assertIn("protein_evidence", obj)
        self.assertIn("source_organism", obj)
        self.assertIn("length", obj)
        self.assertIn("accession", obj)
        self.assertIn("counters", obj)

    def _check_match(self, obj, msg="", include_coordinates=True):
        if include_coordinates:
            try:
                self.assertIn("entry_protein_locations", obj, msg)
            except Exception:
                self.assertIn("structure_protein_locations", obj, msg)

        # self.assertIsInstance(obj["coordinates"], list, msg)
        # TODO: Find a way to check JSON from elasticsearch
        try:
            self.assertIn("accession", obj, msg)
        except Exception:
            self.assertIn("chain", obj, msg)
        self.assertIn("source_database", obj, msg)

    def _check__organism_match(self, obj, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("lineage", obj, msg)
        self.assertIn("source_database", obj, msg)

    def _check__proteome_match(self, obj, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("taxonomy", obj, msg)
        self.assertIn("source_database", obj, msg)

    def _check_list_of_matches(self, obj, msg="", check_coordinates=True):
        for match in obj:
            if "taxonomy" in match:
                self._check__proteome_match(match, msg)
            elif "tax_lineage" in match:
                self._check__organism_match(match, msg)
            else:
                self._check_match(match, msg, include_coordinates=check_coordinates)

    # methods to check structure related responses
    # TODO: Extend this tests
    def _check_structure_count_overview(self, main_obj, msg=""):
        obj = main_obj["structures"]
        self.assertIn("pdb", obj, msg)

    def _check_structure_details(self, obj):
        self.assertIn("chains", obj)
        self.assertIn("accession", obj)
        self.assertIn("counters", obj)

    def _check_structure_chain_details(self, obj):
        self.assertIn("structure_protein_locations", obj)
        self.assertIn("organism", obj)

    def _check_entry_structure_details(self, obj):
        self.assertIn("entry_structure_locations", obj)
        self.assertIn("chain", obj)

    def _check_counter_by_endpoint(self, endpoint, obj, msg=""):
        if "entry" == endpoint:
            self._check_entry_count_overview(obj, msg)
        elif "protein" == endpoint:
            self._check_protein_count_overview(obj, msg)
        elif "structure" == endpoint:
            self._check_structure_count_overview(obj, msg)
        elif "organism" == endpoint:
            self._check_organism_count_overview(obj, msg)

    def _check_object_by_accesssion(self, obj, msg=""):
        self.assertIn("metadata", obj, msg)
        if "children" not in obj["metadata"] and "is_reference" not in obj["metadata"]:
            self.assertIn("source_database", obj["metadata"], msg)
            self.assertIn("counters", obj["metadata"], msg)
            # TODO: do we need counters for organism
        self.assertIn("accession", obj["metadata"], msg)
        self.assertIn("name", obj["metadata"], msg)

    def _check_count_overview_per_endpoints(self, obj, endpoints1, endpoints2, msg=""):
        for inner_obj in obj[endpoints2]:
            if inner_obj in [
                "interpro",
                "unintegrated",
                "uniprot",
                "reviewed",
                "unreviewed",
                "pdb",
            ] and not (
                inner_obj in ["unintegrated", "interpro"]
                and obj[endpoints2][inner_obj] == 0
            ):
                self.assertIn(endpoints1, obj[endpoints2][inner_obj], msg)
                self.assertIn(endpoints2, obj[endpoints2][inner_obj], msg)

    def _check_structure_and_chains(
        self, response, endpoint, db, acc, postfix="", key=None, msg=""
    ):
        urls = []
        if "structure" == endpoint:
            # _chains = [list(ch.keys())[0] for ch in chains[acc]]
            self.assertEqual(chains[acc], response.data["metadata"]["chains"], msg)
            for chain in chains[acc]:
                current = f"/api/{endpoint}/{db}/{acc}/{chain}{postfix}"
                urls.append(current)
                response_acc = self._get_in_debug_mode(current)
                if response_acc.status_code == status.HTTP_200_OK:
                    self.assertEqual(response_acc.status_code, status.HTTP_200_OK, msg)
                    self._check_object_by_accesssion(response_acc.data, msg)
                    self.assertEqual(
                        len(response_acc.data["metadata"]["chains"]), 1, msg
                    )
                    if key is not None:
                        for ch2 in response_acc.data[key]:
                            if "lineage" not in ch2 and "taxonomy" not in ch2:
                                self.assertEqual(ch2["chain"].upper(), chain, msg)
                    self.assertIn(chain, response_acc.data["metadata"]["chains"], msg)
                    self._check_match(
                        response_acc.data["metadata"]["chains"][chain], msg
                    )
                elif response_acc.status_code != status.HTTP_204_NO_CONTENT:
                    self.client.get(current)
        return urls

    def _check_structure_chains_as_counter_filter(
        self, endpoint, db, acc, prefix="", postfix="", key1=None, key2=None
    ):
        urls = []
        if "structure" == endpoint:
            for chain in chains[acc]:
                current = f"/api/{prefix}/{endpoint}/{db}/{acc}/{chain}{postfix}"
                urls.append(current)
                response = self._get_in_debug_mode(current)
                if response.status_code == status.HTTP_200_OK:
                    self._check_counter_by_endpoint(
                        prefix, response.data, f"URL : [{current}]"
                    )
                    # self._check_count_overview_per_endpoints(response.data, key1, key2,
                    #                                          "URL : [{}]".format(current))
                elif response.status_code != status.HTTP_204_NO_CONTENT:
                    self.client.get(current)
        return urls

    def _check_structure_chains_as_filter(
        self, endpoint, db, acc, prefix="", postfix="", key1=None
    ):
        urls = []
        if "structure" == endpoint:
            for chain in chains[acc]:
                current = f"/api/{prefix}/{endpoint}/{db}/{acc}/{chain}{postfix}"
                urls.append(current)
                response = self._get_in_debug_mode(current)
                if response.status_code == status.HTTP_200_OK:
                    obj = (
                        [response.data]
                        if "structures" in response.data
                        else response.data["results"]
                    )
                    self._check_is_list_of_metadata_objects(obj)
                    for result in [x[key1] for x in obj if key1 in x]:
                        self._check_list_of_matches(result, f"URL : [{current}]")
                        self.assertGreaterEqual(len(result), 1)
                        for r in result:
                            self.assertEqual(r["chain"].upper(), chain)

                elif response.status_code != status.HTTP_204_NO_CONTENT:
                    self.client.get(current)
        return urls

    def assertSubset(self, subset, superset, proper=False):
        self.assertLessEqual(
            len(subset),
            len(superset),
            "Can't be subset if more elements in subset than in set",
        )
        for element in subset:
            self.assertIn(
                element, superset, f"Element {element} in subset but not in set"
            )

    def _check_details_url_with_and_without_subset(
        self,
        url,
        endpoint,
        check_metadata_fn=None,
        check_subset_fn=None,
        check_inner_subset_fn=None,
    ):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        if check_metadata_fn is not None:
            check_metadata_fn(response.data["metadata"])
        self.assertIn(f"{plurals[endpoint]}_url", response.data)
        self.assertURL(response.data[f"{plurals[endpoint]}_url"])
        response = self.client.get(url + "?show-subset")
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(f"{endpoint}_subset", response.data)
        if check_subset_fn is not None:
            check_subset_fn(response.data[f"{endpoint}_subset"])
        if check_inner_subset_fn is not None:
            for st in response.data[f"{endpoint}_subset"]:
                check_inner_subset_fn(st)

    def _check_list_url_with_and_without_subset(
        self,
        url,
        endpoint,
        check_results_fn=None,
        check_result_fn=None,
        check_metadata_fn=None,
        check_subset_fn=None,
        check_inner_subset_fn=None,
    ):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        if check_results_fn is not None:
            check_results_fn(response.data["results"])
        self._check_is_list_of_objects_with_key(
            response.data["results"], f"{plurals[endpoint]}_url"
        )
        for result in response.data["results"]:
            self.assertURL(result[f"{plurals[endpoint]}_url"])

        response = self.client.get(url + "?show-subset")
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(
            response.data["results"], f"{endpoint}_subset"
        )
        for result in response.data["results"]:
            if check_result_fn is not None:
                check_result_fn(result)
            if check_metadata_fn is not None:
                check_metadata_fn(result["metadata"])
            if check_subset_fn is not None:
                check_subset_fn(result[f"{endpoint}_subset"])
            for s in result[f"{endpoint}_subset"]:
                if check_inner_subset_fn is not None:
                    check_inner_subset_fn(s)

    def assertURL(self, url, msg=None):
        try:
            validateURL(url)
        except:
            raise self.failureException(msg)

    def _check_taxonomy_details(self, obj, is_complete=True, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("name", obj, msg)
        self.assertIn("children", obj, msg)
        self.assertIn("parent", obj, msg)
        if is_complete:
            self.assertIn("lineage", obj, msg)
            self.assertIn("rank", obj, msg)

    def _check_taxonomy_from_searcher(self, obj, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("lineage", obj, msg)
        self.assertIn("source_database", obj, msg)

    def _check_proteome_from_searcher(self, obj, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("taxonomy", obj, msg)
        self.assertIn("source_database", obj, msg)

    def _check_proteome_details(self, obj, is_complete=True, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("taxonomy", obj, msg)
        self.assertIn("name", obj, msg)
        if is_complete:
            self.assertIn("strain", obj, msg)
            self.assertIn("assembly", obj, msg)

    def _check_taxonomy_count_overview(self, main_obj, msg=""):
        self.assertIn("taxa", main_obj, msg)
        self.assertIn("uniprot", main_obj["taxa"], msg)

    def _check_proteome_count_overview(self, main_obj, msg=""):
        self.assertIn("proteomes", main_obj, msg)
        self.assertIn("uniprot", main_obj["proteomes"], msg)

    def _check_set_details(self, obj, is_complete=True, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("name", obj, msg)
        self.assertIn("source_database", obj, msg)
        if is_complete:
            self.assertIn("relationships", obj, msg)
            self.assertIn("description", obj, msg)

    def _check_set_count_overview(self, main_obj, msg=""):
        self.assertIn("sets", main_obj, msg)
        for s in main_obj["sets"]:
            self.assertIn(s, list(settings.ENTRY_SETS.keys()) + ["all"], msg)

    def _check_set_from_searcher(self, obj, msg=""):
        self.assertIn("accession", obj, msg)
        self.assertIn("source_database", obj, msg)
