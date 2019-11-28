from django.test import TestCase
from django.test import Client


class TestMail(TestCase):
    def test_mail(self):
        self.client = Client()
        response = self.client.post('/mail/',
                          {
                              'path': 'echo',
                              'subject': 'Add annotation test from API',
                              'message': 'Test',
                              'from_email': 'swaathik@ebi.ac.uk'
                           })
        self.assertEqual(response.json()['from'], 'swaathik@ebi.ac.uk')
