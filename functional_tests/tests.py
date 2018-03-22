from functional_tests.base import FunctionalTest
import json
import re
import time

class RESTRequestsTest(FunctionalTest):
    def test_request_entry_endpoint(self):
        self.browser.get(self.server_url + "/api/entry/?format=json")
        content = self.browser.find_element_by_tag_name('body').text
        jsonp = json.loads(content)

        self.assertEqual(len(jsonp["entries"]), 5, "the output has exactly 3 keys")
        self.assertIn('"member_databases"', content)
        self.assertIn('"interpro"', content)
        self.assertIn('"unintegrated"', content)

        num_interpro = jsonp["entries"]["interpro"]
        self.assertEqual(num_interpro, 2, "the fixtures dataset only includes two interpro entry")

        self.browser.get(self.server_url + "/api/entry/interpro?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp["results"]), num_interpro,
                         "The response should have as many entries as reported in /entry ")

        acc = jsonp["results"][0]["metadata"]["accession"]
        self.assertEqual(acc, "IPR001165")
        self.browser.get(self.server_url + "/api/entry/interpro/"+acc+"?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)
        self.assertEqual(acc, jsonp["metadata"]["accession"],
                         "The accession in the response object should be the same as reequested")
        self.assertIn("metadata", jsonp.keys(), "'metadata' should be one of the keys in the response")
        self.assertTrue(isinstance(jsonp["metadata"]["go_terms"], list), "go_terms should be a list")

        self.assertEqual(jsonp["metadata"]["counters"]["proteins"], 1)

    def test_request_protein_endpoint(self):
        self.browser.get(self.server_url + "/api/protein/?format=json")
        time.sleep(10)
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp["proteins"]), 3, "the output has exactly 1 keys")

        self.assertIn('"uniprot"', content)

        num_uniprot = jsonp["proteins"]["uniprot"]
        self.assertEqual(num_uniprot, 4, "the TEST dataset only includes 4 uniprot entries")

        self.browser.get(self.server_url + "/api/protein/uniprot?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp["results"]), num_uniprot,
                         "The response should have as many entries as reported in /entry ")
        acc = jsonp["results"][0]["metadata"]["accession"]

        self.browser.get(self.server_url + "/api/protein/uniprot/"+acc+"?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)
        self.assertEqual(acc, jsonp["metadata"]["accession"],
                         "The accession in the response object should be the same as reequested")
        self.assertIn("category", jsonp["metadata"]["go_terms"][0],
                      "the key is part of the go_terms and has been parsed OK")

        self.browser.get(self.server_url + "/api/protein/uniprot/"+jsonp["metadata"]["id"]+"?format=json")
        content2 = self.browser.find_element_by_tag_name('body').text

        jsonp2 = json.loads(content2)
        self.assertEqual(jsonp, jsonp2,
                         "The recovered JSON object when quierying by accession should be the same than the "
                         "correspondent search by ID")

    def test_request_to_api_frontend(self):
        url = "/api/entry/"
        self.browser.get(self.server_url + url)
        time.sleep(10)

        req_info = self.browser.find_element_by_css_selector(".request-info").text

        self.assertIn("GET", req_info)
        self.assertIn(url, req_info)

        response = self.browser.find_element_by_css_selector(".response-info").text
        match = re.search("[\{\[]", response)
        json_frontend = json.loads(response[match.start():])

        self.browser.find_element_by_css_selector(".format-selection button").click()
        self.click_link_and_wait(self.browser.find_element_by_css_selector(".js-tooltip.format-option"))

        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(json_frontend, jsonp)
