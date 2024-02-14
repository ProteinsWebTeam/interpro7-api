import time

from django.test import TestCase
from django.test import Client
from rest_framework import status


class TestMail(TestCase):
    def test_mail(self, sleep=60):
        self.client = Client()
        response = self.client.post(
            "/api/mail/",
            {
                "path": "echo",
                "subject": "Add annotation test from API",
                "message": "Test",
                "from_email": "swaathik@ebi.ac.uk",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["from"], "swaathik@ebi.ac.uk")
        time.sleep(sleep)

    def test_spam(self):
        self.test_mail(sleep=0)
        self.client = Client()
        response = self.client.post(
            "/api/mail/",
            {
                "path": "echo",
                "subject": "Add annotation test from API",
                "message": "Test",
                "from_email": "swaathik@ebi.ac.uk",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        time.sleep(60)

    def test_mail_invalid_queue(self):
        self.client = Client()
        response = self.client.post(
            "/api/mail/",
            {
                "path": "echo",
                "subject": "Add annotation test from API",
                "message": "Test",
                "queue": "uniprot",
                "from_email": "swaathik@ebi.ac.uk",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        time.sleep(60)
