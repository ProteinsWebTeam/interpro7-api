from django.test import TestCase

from webfront.views.common import map_url_to_levels
from webfront.views.cache import (
    canonical,
    get_timeout_from_path,
    SHOULD_NO_CACHE,
    FIVE_DAYS,
)
from webfront.serializers.content_serializers import reverse_url


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
            canonical("/api/entry//InterPro/IPR000001/"),
        )
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/",
            canonical("/api///entry//////InterPro//IPR000001/"),
        )
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/",
            canonical("/api///entry//////InterPro//IPR000001"),
        )
        self.assertEqual(
            "/api/entry/InterPro/IPR000001/", canonical("/api/entry/InterPro/IPR000001")
        )

    def test_with_query_reorder_urls(self):
        self.assertEqual(
            "/api/entry/InterPro/?integrated=pfam&page=2",
            canonical("/api/entry/InterPro/?page=2&integrated=pfam"),
        )

    def with_query_remove_unneeded_urls(self):
        self.assertEqual(
            "/api/entry/InterPro/?integrated=pfam",
            canonical("/api/entry/InterPro/?page=1&integrated=pfam"),
        )
        self.assertEqual(
            "/api/entry/InterPro/",
            canonical("/api/entry/InterPro/?page=1&page_size=20"),
        )
        self.assertEqual(
            "/api/entry/InterPro/?integrated=pfam",
            canonical("/api/entry/InterPro/?integrated=pfam&page_size=20"),
        )


class CacheLifespanTestCase(TestCase):
    def test_urls_no_cacheable(self):
        urls = [
            "/entry/InterPro/IPR000001/",
            "/protein/uniprot/p99999/?extra_features",
            "/entry/InterPro/?page",
        ]
        for url in urls:
            levels = map_url_to_levels(url.split("?")[0])
            self.assertEqual(SHOULD_NO_CACHE, get_timeout_from_path(url, levels))

    def test_urls_short_life(self):
        urls = [
            "/entry/InterPro/?page=33",
            "/entry/InterPro/?page_size=33",
            "/entry/InterPro/?format",
        ]
        for url in urls:
            levels = map_url_to_levels(url.split("?")[0])
            self.assertEqual(FIVE_DAYS, get_timeout_from_path(url, levels))

    def test_urls_long_life(self):
        urls = [
            "/entry/",
            "/entry/InterPro/",
            "/entry/InterPro/protein",
            "/entry/InterPro/IPR000001/protein",
            "/protein/uniprot/p99999/?conservation",
        ]
        for url in urls:
            levels = map_url_to_levels(url.split("?")[0])
            self.assertIsNone(get_timeout_from_path(url, levels))


class TestReverseURL(TestCase):
    def test_reverse_to_entry(self):
        urls = [
            [
                "/protein/uniprot/p99999/entry/InterPro/",
                "/entry/InterPro/protein/uniprot/p99999/",
            ],
            [  # Modifiers are removed
                "/protein/uniprot/p99999/entry/InterPro/?some-modifier",
                "/entry/InterPro/protein/uniprot/p99999/",
            ],
            [  # 3 endpoints -endpoint
                "/protein/uniprot/p99999/entry/InterPro/structure",
                "/entry/InterPro/protein/uniprot/p99999/structure/",
            ],
            [  # 3 endpoints - db
                "/protein/uniprot/p99999/entry/InterPro/structure/pdb",
                "/entry/InterPro/protein/uniprot/p99999/structure/pdb",
            ],
            [  # 3 endpoints - accession
                "/protein/uniprot/p99999/entry/InterPro/structure/pdb/1cuk",
                "/entry/InterPro/protein/uniprot/p99999/structure/pdb/1cuk",
            ],
        ]
        for url in urls:
            self.assertEqual(reverse_url(url[0], "entry"), url[1])

    def test_reverse_to_protein(self):
        urls = [
            [
                "/entry/InterPro/ipr000001/protein/uniprot/",
                "/protein/uniprot/entry/InterPro/ipr000001/",
            ],
            [  # Modifiers are removed
                "/entry/InterPro/ipr000001/protein/uniprot/?some-modifier",
                "/protein/uniprot/entry/InterPro/ipr000001/",
            ],
            [  # 3 endpoints -endpoint
                "/entry/InterPro/ipr000001/protein/uniprot/structure",
                "/protein/uniprot/entry/InterPro/ipr000001/structure/",
            ],
            [  # 3 endpoints - db
                "/entry/InterPro/ipr000001/protein/uniprot/structure/pdb",
                "/protein/uniprot/entry/InterPro/ipr000001/structure/pdb",
            ],
            [  # 3 endpoints - accession
                "/entry/InterPro/ipr000001/protein/uniprot/structure/pdb/1cuk",
                "/protein/uniprot/entry/InterPro/ipr000001/structure/pdb/1cuk",
            ],
        ]
        for url in urls:
            self.assertEqual(reverse_url(url[0], "protein"), url[1])
