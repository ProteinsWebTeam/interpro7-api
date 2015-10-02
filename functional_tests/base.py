from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from rest_framework.test import APIRequestFactory, APIClient
from selenium import webdriver
import sys
import time
from selenium.common.exceptions import StaleElementReferenceException

class FunctionalTest(StaticLiveServerTestCase):  #1
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        # self.browser.get(self.server_url+"?testing=create")
        # self.factory = APIRequestFactory()
        # self.client = APIClient()

    def tearDown(self):
        # self.browser.get(self.server_url+"?testing=remove")
        self.browser.quit()

    def click_link_and_wait(self, link):
        link.click()

        def link_has_gone_stale():
            try:
                # poll the link with an arbitrary call
                link.find_elements_by_id('doesnt-matter')
                return False
            except StaleElementReferenceException:
                return True

        self.wait_for(link_has_gone_stale)

