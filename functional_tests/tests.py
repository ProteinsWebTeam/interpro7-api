from functional_tests.base import FunctionalTest
import json


class RESTRequestsTest(FunctionalTest):
    fixtures = ['webfront/tests/fixtures.json']

    def test_request_entry_endpoint(self):
        self.browser.get(self.server_url + "/api/entry/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), 3, "the output has exactly 3 keys")

        self.assertIn('"member_databases"', content)
        self.assertIn('"interpro"', content)
        self.assertIn('"unintegrated"', content)

        self.assertEqual(jsonp["interpro"], 1, "the fistres dataset only includes one interpro entry")
