from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest

from webfront.views import home_page


class SmokeTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()  #1
        response = home_page(request)  #2
        self.assertTrue(response.content.startswith(b'<html>'))  #3
        self.assertIn(b'<title>UniFam</title>', response.content)  #4
        self.assertTrue(response.content.endswith(b'</html>'))  #5