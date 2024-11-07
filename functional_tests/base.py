from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import time
import os
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


from webfront.tests.fixtures_reader import FixtureReader
from interpro.settings import SEARCHER_TEST_URL, SEARCHER_TEST_PASSWORD

@override_settings(SEARCHER_URL=SEARCHER_TEST_URL)
@override_settings(SEARCHER_PASSWORD=SEARCHER_TEST_PASSWORD)
@override_settings(SEARCHER_INDEX="test")
class FunctionalTest(StaticLiveServerTestCase):
    fixtures = [
        "webfront/tests/fixtures_entry.json",
        "webfront/tests/fixtures_protein.json",
        "webfront/tests/fixtures_structure.json",
        "webfront/tests/fixtures_organisms.json",
        "webfront/tests/fixtures_set.json",
        "webfront/tests/fixtures_database.json",
    ]
    links_fixtures = "webfront/tests/relationship_features.json"

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if "liveserver" in arg:
                cls.server_url = "http://" + arg.split("=")[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url
        cls.fr = FixtureReader(cls.fixtures + [cls.links_fixtures])
        docs = cls.fr.get_fixtures()
        cls.fr.add_to_search_engine(docs)

    @classmethod
    def tearDownClass(cls):
        # cls.fr.clear_search_engine()
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        try:
            if os.environ["BROWSER_TEST"] == "chrome":
                chrome_options = ChromeOptions()
                chrome_options.add_argument("--headless")

                if "BROWSER_TEST_PATH" in os.environ:
                    self.browser = webdriver.Chrome(
                        executable_path=os.environ["BROWSER_TEST_PATH"],
                        chrome_options=chrome_options,
                    )
                else:
                    self.browser = webdriver.Chrome(chrome_options=chrome_options)
            else:
                raise KeyError
        except KeyError:
            options = FirefoxOptions()
            options.add_argument("--headless")
            self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def click_link_and_wait(self, link):
        link.click()

        def link_has_gone_stale():
            try:
                # poll the link with an arbitrary call
                link.find_elements(By.ID, "doesnt-matter")
                return False
            except StaleElementReferenceException:
                return True

        self.wait_for(link_has_gone_stale)

    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + 3:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception("Timeout waiting for {}".format(condition_function.__name__))
