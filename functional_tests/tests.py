import time
from functional_tests.base import FunctionalTest
import json

class NewVisitorTest(FunctionalTest):
    fixtures = ['functional_tests/dummy_data.json']

    def test_can_navigate_clans(self):
        # check out its homepage
        self.browser.get(self.server_url)

        # the page title and header mention UniFam
        self.assertIn('UniFam', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('UNIFAM', header_text)

        # The page has a link for clans and the user clicks on it
        self.browser.find_element_by_css_selector('a.clans_link').click()

        # The clans page opens and has a title
        self.assertIn('UniFam - Clans', self.browser.title)

        # The user will have a way to choose a clan from the  DB
        clan_li =self.browser.find_element_by_css_selector('li.clan')
        clan_header =clan_li.find_element_by_tag_name('a').text
        # The user chooses a clan
        clan_li.find_element_by_tag_name("a").click()

        # The user will go to the page of the clan
        self.assertIn('UniFam - Clan: '+clan_header, self.browser.title)

        # The clan page displays the details of the clan

        # The clan page displays a list of the  families of the clan

        # the clan page also displays a table of the relationships

    def test_uses_the_REST_for_clan(self):
        # Test that the server returns JSON
        self.browser.get(self.server_url+"/api/clans/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        try:
            jsonp = json.loads(content)
        except ValueError:
            self.fail("The content is not a json")

        self.assertEqual(jsonp["count"],2)
        self.assertEqual(len(jsonp["results"]), jsonp["count"])

        self.assertIn('"TEST_ACC"', content)
        self.assertIn('"TEST_ACC_2"', content)

        self.browser.get(self.server_url+"/api/pfama/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        try:
            jsonp = json.loads(content)
        except ValueError:
            self.fail("The content is not a json")

        self.assertEqual(jsonp["count"],2)
        self.assertEqual(len(jsonp["results"]),jsonp["count"])

        self.assertIn('"TEST_PFAM_ACC"', content)
        self.assertIn('"TEST_PFAM_ACC_2"', content)

        self.browser.get(self.server_url+"/api/clans/TEST_ACC/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        try:
            jsonp = json.loads(content)
        except ValueError:
            self.fail("The content is not a json")

        self.assertEqual(jsonp["clan_acc"], "TEST_ACC")
        self.assertEqual(sum([x["num_full"] for x in jsonp["members"]]), jsonp["total_occurrences"])


