from django.test import TestCase

from webfront.views.cache import canonical


class CanonicalTestCase(TestCase):
    def test_basic_unchanged_urls(self):
        url = "/api/entry/InterPro/IPR000001/"
        self.assertEqual(url, canonical(url))
        url = "/api/PrOtEiN/ReViEwEd/"
        self.assertEqual(url, canonical(url))

    def test_with_query_unchanged_urls(self):
        url = "/api/protein/reviewed/?length=1-100"
        self.assertEqual(url, canonical(url))
        url = "/api/protein/reviewed/?length=1-100&page=2"
        self.assertEqual(url, canonical(url))
        url = "/api/protein/reviewed/?length=1-100&page=2&page_size=50"
        self.assertEqual(url, canonical(url))

    def test_basic_incorrect_slash_urls(self):
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/",
            canonical("/api/entry//InterPro/IPR000001/")
        )
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/",
            canonical("/api///entry//////InterPro//IPR000001/")
        )
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/",
            canonical("/api///entry//////InterPro//IPR000001")
        )
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/",
            canonical("/api/entry/InterPro/IPR000001")
        )


    def test_with_query_reorder_urls(self):
        self.assertEqual(
            "/api/entry/InterPro/?integrated=pfam&page=2",
            canonical("/api/entry/InterPro/?page=2&integrated=pfam")
        )


    def with_query_remove_unneeded_urls(self):
        self.assertEqual(
            "/api/entry/InterPro/?integrated=pfam",
            canonical("/api/entry/InterPro/?page=1&integrated=pfam")
        )
        self.assertEqual(
            "/api/entry/InterPro/",
            canonical("/api/entry/InterPro/?page=1&page_size=20")
        )
        self.assertEqual(
            "/api/entry/InterPro/?integrated=pfam",
            canonical("/api/entry/InterPro/?integrated=pfam&page_size=20")
        )
