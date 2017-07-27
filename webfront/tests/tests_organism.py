from rest_framework import status

from webfront.models import Taxonomy
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class OrganismFixturesTest(InterproRESTTestCase):

    def test_the_fixtures_are_loaded(self):
        taxa = Taxonomy.objects.all()
        self.assertEqual(taxa.count(), 6)
        names = [t.scientific_name for t in taxa]
        self.assertIn("ROOT", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("taxonomy", response.data)
        # self.assertIn("proteome", response.data)

    def test_can_read_taxonomy_list(self):
        response = self.client.get("/api/organism/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 6)

    def test_can_read_taxonomy_id(self):
        response = self.client.get("/api/organism/taxonomy/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_details(response.data["metadata"])

    def test_can_read_proteome_list(self):
        response = self.client.get("/api/organism/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 3)

    def test_can_read_proteome_id(self):
        response = self.client.get("/api/organism/proteome/UP000012042")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_details(response.data["metadata"])

    def test_can_read_taxonomy_with_proteome_list(self):
        response = self.client.get("/api/organism/taxonomy/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 3)

    def test_can_read_taxonomy_leaf_id_with_proteomes(self):
        response = self.client.get("/api/organism/taxonomy/40296/proteome")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_can_read_taxonomy_node_id_with_proteomes(self):
        response = self.client.get("/api/organism/taxonomy/2579/proteome")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_proteome_id_including_tax_id(self):
        lineage = [1, 2, 40296]
        for taxon in lineage:
            response = self.client.get("/api/organism/taxonomy/{}/proteome/UP000030104".format(taxon))
            self.assertEqual(response.status_code, status.HTTP_200_OK, "failed at "+str(taxon))
            self._check_proteome_details(response.data["metadata"])
