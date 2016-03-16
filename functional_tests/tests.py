from functional_tests.base import FunctionalTest
import json


class RESTRequestsTest(FunctionalTest):
    fixtures = ['webfront/tests/fixtures.json', 'webfront/tests/protein_fixtures.json']

    def test_request_entry_endpoint(self):
        self.browser.get(self.server_url + "/api/entry/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), 3, "the output has exactly 3 keys")

        self.assertIn('"member_databases"', content)
        self.assertIn('"interpro"', content)
        self.assertIn('"unintegrated"', content)

        num_interpro = jsonp["interpro"]
        self.assertEqual(num_interpro, 1, "the fistres dataset only includes one interpro entry")

        self.browser.get(self.server_url + "/api/entry/interpro?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), num_interpro, "The response should have as many entries as reported in /entry ")
        self.assertIn("metadata", jsonp[0].keys(), "'metadata' should be one of the keys in the response")
        self.assertIn("molecular_function", jsonp[0]["metadata"]["go_terms"],
                      "the key is part of the go_terms and has been parsed OK")

        acc = jsonp[0]["metadata"]["accession"]
        self.browser.get(self.server_url + "/api/entry/interpro/"+acc+"?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)
        self.assertEqual(acc, jsonp["metadata"]["accession"],
                         "The accession in the response object should be the same as reequested")

    def test_request_protein_endpoint(self):
        self.browser.get(self.server_url + "/api/protein/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), 1, "the output has exactly 1 keys")

        self.assertIn('"uniprot"', content)

        num_uniprot = jsonp["uniprot"]
        self.assertEqual(num_uniprot, 4, "the TEST dataset only includes 4 uniprot entries")

        self.browser.get(self.server_url + "/api/protein/uniprot?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), num_uniprot, "The response should have as many entries as reported in /entry ")
        acc = jsonp[0]["accession"]

        self.browser.get(self.server_url + "/api/protein/uniprot/"+acc+"?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)
        self.assertEqual(acc, jsonp["metadata"]["accession"],
                         "The accession in the response object should be the same as reequested")
        self.assertIn("molecular_function", jsonp["metadata"]["go_terms"],
                      "the key is part of the go_terms and has been parsed OK")
