from django.test import TransactionTestCase
from webfront.models import Entry


class ModelTest(TransactionTestCase):
    fixtures = ['webfront/tests/fixtures.json']

    def test_dummy_dataset_is_loaded(self):
        self.assertGreater(Entry.objects.all().count(),0,"The dataset has to have at least one Entry")
        self.assertEqual(Entry.objects.filter(source_database="interpro").first().accession,"IPR003165")

    def test_content_of_a_json_attribute(self):
        entry = Entry.objects.get(id="id1")
        self.assertEqual(entry.member_databases["pfam"][0], "PF02171")
