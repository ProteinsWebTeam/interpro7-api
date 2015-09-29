from django.test import LiveServerTestCase
from selenium import webdriver


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_see_the_home(self):
        # check out its homepage
        self.browser.get(self.live_server_url)

        # the page title and header mention UniFam
        self.assertIn('UniFam', self.browser.title)

        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('UniFam', header_text)

