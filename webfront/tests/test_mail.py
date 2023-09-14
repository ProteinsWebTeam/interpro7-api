from django.test import TestCase
from django.test import Client
from rest_framework import status


class TestMail(TestCase):
    def test_mail(self):
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
