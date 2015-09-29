from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string

from webfront.views import home_page


class SmokeTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()  #1
        response = home_page(request)  #2
        expected_html = render_to_string('home.html')
        self.assertEqual(response.content.decode(), expected_html)