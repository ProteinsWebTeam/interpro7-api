from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from rest_framework import status


class IDASearchModifierTest(InterproRESTTestCase):
    def _assertSearch(self, response, count):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertEqual(response.data["count"], count)

    def test_search_by_a_single_accession(self):
        response = self.client.get("/api/entry?ida_search=IPR003165")
        self._assertSearch(response, 2)

    def test_search_by_ordered_search(self):
        response = self.client.get("/api/entry?ida_search=IPR003165,IPR003165&ordered")
        self._assertSearch(response, 2)

    def test_search_by_non_existing_ipr(self):
        response = self.client.get("/api/entry?ida_search=IPR00XXXX")
        self._assertSearch(response, 0)

    def test_search_with_ignoring_list(self):
        response = self.client.get("/api/entry?ida_search=IPR001175&ida_ignore=pf17176")
        self._assertSearch(response, 0)

    def test_search_exact_single(self):
        response = self.client.get("/api/entry?ida_search=pf17180&ordered&exact")
        self._assertSearch(response, 1)

    def test_search_exact_vs_ordered(self):
        response = self.client.get("/api/entry?ida_search=PF02171,PF02171&exact")
        self._assertSearch(response, 1)
        response = self.client.get("/api/entry?ida_search=PF02171,PF02171&ordered")
        self._assertSearch(response, 2)

    def test_search_pfam_vs_interpro_accession(self):
        response = self.client.get("/api/entry?ida_search=PF02171,PF02171&exact")
        self._assertSearch(response, 1)
        response = self.client.get("/api/entry?ida_search=IPR003165,PF02171&exact")
        self._assertSearch(response, 1)
        response = self.client.get("/api/entry?ida_search=PF02171,IPR003165&exact")
        self._assertSearch(response, 1)
        response = self.client.get("/api/entry?ida_search=IPR003165,IPR003165&exact")
        self._assertSearch(response, 1)
