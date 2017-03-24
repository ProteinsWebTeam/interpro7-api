from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from rest_framework import status


class GroupByModifierTest(InterproRESTTestCase):

    def test_can_get_the_entry_type_groups(self):
        response = self.client.get("/api/entry?group_by=type")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("domain", response.data)
        self.assertIn("family", response.data)

    def test_can_get_the_entry_type_groups_of_entries_with_proteins(self):
        response = self.client.get("/api/entry/protein?group_by=type")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("domain", response.data)
        self.assertNotIn("family", response.data)

    def test_wrong_field_fro_group_by_should_fail(self):
        self._check_HTTP_response_code("/api/entry?group_by=entry_type", code=status.HTTP_404_NOT_FOUND)
