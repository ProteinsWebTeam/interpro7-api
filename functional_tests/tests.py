from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from functional_tests.base import FunctionalTest
import json
import unittest
import os


class NewVisitorTest(FunctionalTest):
    fixtures = ['functional_tests/dummy_data.json']

    def test_can_navigate_clans(self):
        # check out its homepage
        self.browser.get(self.server_url)

        # the page title and header mention UniFam
        self.assertIn('UniFam', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('UNIFAM', header_text)

        # The User navigates trough the website until it finds the clans page
        self.click_link_and_wait(self.browser.find_element_by_css_selector('a.entries_link'))
        self.click_link_and_wait(self.browser.find_element_by_css_selector('a.interpro_link'))
        self.click_link_and_wait(self.browser.find_element_by_css_selector('a.interpro_all_link'))
        self.click_link_and_wait(self.browser.find_element_by_css_selector('a.member_db_link.pfam'))
        self.click_link_and_wait(self.browser.find_element_by_css_selector('a.interpro_member_option_link.clans'))

        # The clans page opens and has a title
        self.assertIn('UniFam - Clans', self.browser.title)
        content = self.browser.find_element_by_tag_name("body").text
        self.assertIn("CL9999", content)

        # The user will have a way to choose a clan from the  DB
        clan_li = self.browser.find_element_by_css_selector('li.clan.CL9999')
        # clan_header = clan_li.find_element_by_tag_name('a').text

        # The user chooses a clan
        self.click_link_and_wait(clan_li.find_element_by_tag_name("a"))

        # The user will go to the page of the clan
        self.assertIn('UniFam - Clan: ', self.browser.title)

        # The clan page displays the details of the clan

        # The clan page displays a list of the  families of the clan

        # the clan page also displays an SVG
        svg = self.browser.find_element_by_tag_name("svg")
        self.assertEqual("clanviewer", svg.get_attribute("class"))

        try:
            node = WebDriverWait(self.browser, 10).until(
                expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".node")))
        finally:
            content = svg.get_attribute('innerHTML')
            self.assertIn("node_", node.get_attribute("id"))
            self.assertIn("circle", content)

    def test_uses_the_REST_for_clan(self):
        # Test that the server returns JSON
        self.browser.get(self.server_url + "/api/entry/interpro/all/pfam/clan/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), 2)

        self.assertIn('"CL9999"', content)
        self.assertIn('"CL9998"', content)

        self.browser.get(self.server_url + "/api/entry/interpro/all/pfam/clan/CL9999/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(jsonp["clan_acc"], "CL9999")
        self.assertEqual(sum([x["num_full"] for x in jsonp["members"]]), jsonp["total_occurrences"])

        self.browser.get(self.server_url + "/api/entry/interpro/all/pfam/?format=json")
        content = self.browser.find_element_by_tag_name('body').text

        jsonp = json.loads(content)

        self.assertEqual(len(jsonp), 2)

        self.assertIn('"TEST_PFAM_ACC"', content)
        self.assertIn('"TEST_PFAM_ACC_2"', content)

    # skipping this test in travis because there the hmmer binaries are not there
    @unittest.skipIf("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", "Skipping this test on Travis CI.")
    def test_can_navigate_active_sites(self):
        test_family = "TEST_PFAM_ACC"

        # check out its homepage
        self.browser.get(self.server_url + "/entry/interpro/all/pfam/" + test_family)

        # The page has a link for active sites and the user clicks on it
        self.click_link_and_wait(
            self.browser.find_element_by_css_selector('a.interpro_member_option_link.active_sites'))

        # The active sites page opens and has a title
        self.assertIn('Active Sites', self.browser.title)
        self.assertIn(test_family, self.browser.title)

        # The user will have to input  a protein family accession
        content = self.browser.find_element_by_css_selector('.active_sites').text

        self.assertIn("TEST_SEQ_ACC_1", content)
        self.assertNotIn("TEST_SEQ_ACC_3", content)
