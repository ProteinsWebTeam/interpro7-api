from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
import ipdb


class EntryRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/entry/interpro/").json(),
            self.client.get("/api/entry/interpro/?search=").json()
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get(
            "/api/entry/interpro/?search=piwi"
        ).data["results"]
        unfiltered = self.client.get("/api/entry/interpro/").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get("/api/entry/interpro/?search=piwi").json()
        for othercase in ["PIWI", "Piwi", "pIWi"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/entry/interpro/?search={}".format(othercase)
                ).json()
            )


class ProteinRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/protein/uniprot/").json(),
            self.client.get("/api/protein/uniprot/?search=").json()
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get(
            "/api/protein/uniprot/?search=carboxy"
        ).data["results"]
        unfiltered = self.client.get("/api/protein/uniprot/").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get(
            "/api/protein/uniprot/?search=carboxy"
        ).json()
        for othercase in ["CARBOXY", "Carboxy", "cArBoXy"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/protein/uniprot/?search={}".format(othercase)
                ).json()
            )


class StructureRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/structure/pdb/").json(),
            self.client.get("/api/structure/pdb/?search=").json()
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get(
            "/api/structure/pdb/?search=brca"
        ).data["results"]
        unfiltered = self.client.get("/api/structure/pdb/").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get("/api/structure/pdb/?search=brca").json()
        for othercase in ["BRCA", "Brca", "bRCa"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/structure/pdb/?search={}".format(othercase)
                ).json()
            )


class TwoEndpointsRESTSearchTest(InterproRESTTestCase):
    def test_return_unfiltered_result_set_if_empty(self):
        self.assertEqual(
            self.client.get("/api/entry/interpro/protein").json(),
            self.client.get("/api/entry/interpro/protein?search=").json()
        )
        self.assertEqual(
            self.client.get("/api/entry/interpro/structure").json(),
            self.client.get("/api/entry/interpro/structure?search=").json()
        )
        self.assertEqual(
            self.client.get("/api/structure/pdb/entry").json(),
            self.client.get("/api/structure/pdb/entry?search=").json()
        )
        self.assertEqual(
            self.client.get("/api/structure/pdb/protein").json(),
            self.client.get("/api/structure/pdb/protein?search=").json()
        )
        self.assertEqual(
            self.client.get("/api/protein/uniprot/entry").json(),
            self.client.get("/api/protein/uniprot/entry?search=").json()
        )
        self.assertEqual(
            self.client.get("/api/protein/uniprot/structure").json(),
            self.client.get("/api/protein/uniprot/structure?search=").json()
        )

    def test_return_filtered_subset_of_unfiltered(self):
        filtered = self.client.get(
            "/api/structure/pdb/entry?search=adk"
        ).data["results"]
        unfiltered = self.client.get("/api/structure/pdb/entry").data["results"]
        self.assertSubset(subset=filtered, superset=unfiltered, proper=True)

    def test_return_same_case_insensitive(self):
        response = self.client.get("/api/structure/pdb/entry?search=adk").json()
        for othercase in ["ADK", "aDk", "AdK"]:
            self.assertEqual(
                response,
                self.client.get(
                    "/api/structure/pdb/entry?search={}".format(othercase)
                ).json()
            )
