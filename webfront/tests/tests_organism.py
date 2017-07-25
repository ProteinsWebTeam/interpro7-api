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
