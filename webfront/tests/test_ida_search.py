from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from rest_framework import status


class IDASearchModifierTest(InterproRESTTestCase):
    def test_search_by_a_single_accession(self):
        response = self.client.get("/api/entry?ida_search=IPR003165")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertGreater(response.data["count"], 0)

    def test_search_by_ordered_search(self):
        response = self.client.get("/api/entry?ida_search=IPR003165,IPR003165&ordered")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertGreater(response.data["count"], 0)

    def test_search_by_non_existing_ipr(self):
        response = self.client.get("/api/entry?ida_search=IPR00XXXX")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertEqual(response.data["count"], 0)

    def test_search_with_ignoring_list(self):
        response = self.client.get("/api/entry?ida_search=IPR001175&ida_ignore=pf17176")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertEqual(response.data["count"], 0)
