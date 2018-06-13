from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class UtilsTest(InterproRESTTestCase):

    def test_can_read_structure_overview(self):
        response = self.client.get("/api/utils")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
