from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from webfront.searcher.elastic_controller import ElasticsearchController
from django.conf import settings


class ElasticContorllerTest(InterproRESTTestCase):
    def test_elastic_class_init(self):
        obj = {}
        elastic = ElasticsearchController(obj)
        self.assertEqual(obj, elastic.queryset_manager)
        self.assertIsNotNone(elastic.headers)
        if settings.SEARCHER_USER == "":
            self.assertNotIn("Authorization", elastic.headers)
        else:
            self.assertIn("Authorization", elastic.headers)


class EntryRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/entry/interpro/").json(),
            self.client.get("/api/entry/interpro/?search=").json(),
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get("/api/entry/interpro/?search=piwi").data["results"]
        unfiltered = self.client.get("/api/entry/interpro/").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get("/api/entry/interpro/?search=piwi").json()
        for othercase in ["PIWI", "Piwi", "pIWi"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/entry/interpro/?search={}".format(othercase)
                ).json(),
            )


class ProteinRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/protein/uniprot/").json(),
            self.client.get("/api/protein/uniprot/?search=").json(),
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get("/api/protein/uniprot/?search=carboxy").data[
            "results"
        ]
        unfiltered = self.client.get("/api/protein/uniprot/").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get("/api/protein/uniprot/?search=carboxy").json()
        for othercase in ["CARBOXY", "Carboxy", "cArBoXy"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/protein/uniprot/?search={}".format(othercase)
                ).json(),
            )


class StructureRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/structure/pdb/").json(),
            self.client.get("/api/structure/pdb/?search=").json(),
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get("/api/structure/pdb/?search=brca").data["results"]
        unfiltered = self.client.get("/api/structure/pdb/").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get("/api/structure/pdb/?search=brca").json()
        for othercase in ["BRCA", "Brca", "bRCa"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/structure/pdb/?search={}".format(othercase)
                ).json(),
            )


class TwoEndpointsRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/entry/interpro/protein").json(),
            self.client.get("/api/entry/interpro/protein?search=").json(),
        )
        self.assertEqual(
            self.client.get("/api/entry/interpro/structure").json(),
            self.client.get("/api/entry/interpro/structure?search=").json(),
        )
        self.assertEqual(
            self.client.get("/api/structure/pdb/entry").json(),
            self.client.get("/api/structure/pdb/entry?search=").json(),
        )
        self.assertEqual(
            self.client.get("/api/structure/pdb/protein").json(),
            self.client.get("/api/structure/pdb/protein?search=").json(),
        )
        self.assertEqual(
            self.client.get("/api/protein/uniprot/entry").json(),
            self.client.get("/api/protein/uniprot/entry?search=").json(),
        )
        self.assertEqual(
            self.client.get("/api/protein/uniprot/structure").json(),
            self.client.get("/api/protein/uniprot/structure?search=").json(),
        )

    def test_return_filtered_subset_of_unfiltered(self):
        urls = [
            ("/api/protein/reviewed/entry", "degradation"),
            ("/api/protein/reviewed/structure", "degradation"),
            ("/api/protein/reviewed/set", "degradation"),
            ("/api/protein/reviewed/taxonomy", "degradation"),
            ("/api/protein/reviewed/proteome", "degradation"),
            ("/api/entry/interpro/protein", "cleave"),
            ("/api/entry/interpro/structure", "cleave"),
            ("/api/entry/interpro/taxonomy", "cleave"),
            ("/api/entry/interpro/proteome", "cleave"),
            ("/api/structure/pdb/entry", "1t2v"),
            ("/api/structure/pdb/protein", "1t2v"),
            ("/api/set/pfam/taxonomy", "cl0002"),
            ("/api/set/pfam/proteome", "cl0002"),
            ("/api/set/pfam/protein", "cl0002"),
            ("/api/set/pfam/structure", "cl0002"),
            ("/api/set/pfam/taxonomy", "cl0002"),
            ("/api/set/pfam/proteome", "cl0002"),
            ("/api/taxonomy/uniprot/entry", "2579"),
            ("/api/taxonomy/uniprot/protein", "2579"),
            ("/api/taxonomy/uniprot/structure", "2579"),
            ("/api/taxonomy/uniprot/set", "2579"),
            ("/api/proteome/uniprot/entry", "penicillium"),
            ("/api/proteome/uniprot/protein", "penicillium"),
            ("/api/proteome/uniprot/structure", "penicillium"),
            ("/api/proteome/uniprot/set", "aspergillus"),
        ]
        for url in urls:
            filtered = self.client.get("{}?search={}".format(url[0], url[1])).data[
                "results"
            ]
            unfiltered = self.client.get(url[0]).data["results"]
            self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get(
            "/api/protein/reviewed/entry?search=degradation"
        ).json()
        for othercase in ["degradatioN", "DEGRADATION", "degRADAtion"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/protein/reviewed/entry?search={}".format(othercase)
                ).json(),
            )
