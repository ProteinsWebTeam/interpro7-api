from rest_framework import status

from webfront.models import Set
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class SetsFixturesTest(InterproRESTTestCase):
    def test_the_fixtures_are_loaded(self):
        sets = Set.objects.all()
        self.assertEqual(sets.count(), 2)
        names = [t.name for t in sets]
        self.assertIn("The Clan", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_set_count(self):
        response = self.client.get("/api/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sets", response.data)
        self.assertIn("pfam", response.data["sets"])
        self.assertNotIn("unicorn", response.data["sets"])
        self.assertNotIn("node", response.data["sets"])

    def test_can_read_set_list(self):
        response = self.client.get("/api/set/pfam")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_set_id(self):
        response = self.client.get("/api/set/pfam/CL0001")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_details(response.data["metadata"])


class EntrySetTest(InterproRESTTestCase):
    def test_can_get_the_set_count(self):
        response = self.client.get("/api/entry/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/pfam/set",
            "/api/entry/unintegrated/set",
            "/api/entry/interpro/pfam/set",
            "/api/entry/unintegrated/pfam/set",
            f"/api/entry/interpro/{acc}/pfam/set",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_entry_with_set_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/entry/pfam/{pfam}/set",
            f"/api/entry/pfam/{pfam_un}/set",
            f"/api/entry/interpro/{acc}/pfam/{pfam}/set",
            f"/api/entry/interpro/pfam/{pfam}/set",
            f"/api/entry/unintegrated/pfam/{pfam_un}/set",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn(
                "sets",
                response.data,
                "'sets' should be one of the keys in the response",
            )
            self._check_set_count_overview(response.data)

    def test_can_filter_entry_counter_with_set_db(self):
        urls = ["/api/entry/set/pfam"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn(
                "sets",
                response.data["entries"]["integrated"],
                "'sets' should be one of the keys in the response",
            )
            if response.data["entries"]["unintegrated"] != 0:
                self.assertIn(
                    "sets",
                    response.data["entries"]["unintegrated"],
                    "'sets' should be one of the keys in the response",
                )

    def test_can_get_the_set_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/pfam/set/pfam",
            "/api/entry/unintegrated/set/pfam",
            f"/api/entry/interpro/{acc}/pfam/set/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
            )

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/entry/pfam/PF02171/set/pfam",
            "/api/entry/unintegrated/pfam/PF17176/set/pfam",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
                check_metadata_fn=self._check_entry_details,
            )

    def test_can_filter_entry_counter_with_set_acc(self):
        urls = ["/api/entry/set/pfam/Cl0001", "/api/entry/set/pfam/Cl0002"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_count_overview(response.data)

    def test_can_get_the_set_object_on_a_list(self):
        urls = [
            "/api/entry/pfam/set/pfam/Cl0001",
            "/api/entry/unintegrated/set/pfam/Cl0001",
            "/api/entry/unintegrated/pfam/set/pfam/Cl0001",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for org in result["sets"]:
                    self._check_set_from_searcher(org)

    def test_can_get_the_object_on_an_object(self):
        urls = [
            "/api/entry/pfam/PF02171/set/pfam/CL0001",
            "/api/entry/unintegrated/pfam/PF17176/set/pfam/CL0002",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)

    def test_set_with_optional_fields(self):
        url = "/api/set/pfam/CL0001"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        metadata = response.data["metadata"]
        self._check_set_details(metadata)
        self.assertIn("authors", metadata)
        self.assertEqual(2, len(metadata["authors"]))
        self.assertEqual(str, type(metadata["authors"][0]))
        self.assertIn("literature", metadata)
        self.assertEqual(2, len(metadata["literature"]))
        self.assertEqual(dict, type(metadata["literature"][0]))
        self.assertIn("PMID", metadata["literature"][0])
        self.assertIn("wikipedia", metadata)
        self.assertEqual(1, len(metadata["wikipedia"]))
        self.assertEqual(dict, type(metadata["wikipedia"][0]))
        self.assertIn("title", metadata["wikipedia"][0])
        self.assertIn("extract", metadata["wikipedia"][0])
        self.assertIn("thumbnail", metadata["wikipedia"][0])

    def test_set_without_optional_fields(self):
        url = "/api/set/pfam/CL0002"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        metadata = response.data["metadata"]
        self._check_set_details(metadata)
        self.assertIn("authors", metadata)
        self.assertEqual([], metadata["authors"])
        self.assertIn("literature", metadata)
        self.assertEqual([], metadata["literature"])
        self.assertIn("wikipedia", metadata)
        self.assertEqual([], metadata["wikipedia"])


class ProteinSetTest(InterproRESTTestCase):
    def test_can_get_the_set_count(self):
        response = self.client.get("/api/protein/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        urls = ["/api/protein/reviewed/set/", "/api/protein/uniprot/set/"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_protein_with_set_count(self):
        reviewed = "A1CUJ5"
        urls = [
            f"/api/protein/uniprot/{reviewed}/set",
            f"/api/protein/reviewed/{reviewed}/set",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn(
                "sets",
                response.data,
                "'sets' should be one of the keys in the response",
            )
            self._check_set_count_overview(response.data)

    def test_can_filter_protein_counter_with_set_db(self):
        urls = ["/api/protein/set/pfam"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn(
                "proteins",
                response.data["proteins"]["uniprot"],
                "'proteins' should be one of the keys in the response",
            )
            self.assertIn(
                "sets",
                response.data["proteins"]["uniprot"],
                "'sets' should be one of the keys in the response",
            )
            if "reviewed" in response.data["proteins"]:
                self.assertIn(
                    "proteins",
                    response.data["proteins"]["reviewed"],
                    "'proteins' should be one of the keys in the response",
                )
                self.assertIn(
                    "sets",
                    response.data["proteins"]["reviewed"],
                    "'sets' should be one of the keys in the response",
                )
            if "unreviewed" in response.data["proteins"]:
                self.assertIn(
                    "proteins",
                    response.data["proteins"]["unreviewed"],
                    "'proteins' should be one of the keys in the response",
                )
                self.assertIn(
                    "sets",
                    response.data["proteins"]["unreviewed"],
                    "'sets' should be one of the keys in the response",
                )

    def test_can_get_the_set_list_on_a_list(self):
        urls = ["/api/protein/reviewed/set/pfam"]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
            )

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/protein/uniprot/M5ADK6/set/pfam",
            "/api/protein/reviewed/A1CUJ5/set/pfam",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
                check_metadata_fn=self._check_protein_details,
            )

    def test_can_filter_counter_with_set_acc(self):
        urls = ["/api/protein/set/pfam/Cl0001"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_count_overview(response.data)

    def test_can_get_the_set_object_on_a_list(self):
        urls = [
            "/api/protein/uniprot/set/pfam/Cl0001",
            "/api/protein/reviewed/set/pfam/Cl0001",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for org in result["sets"]:
                    self._check_set_from_searcher(org)

    def test_can_get_the_object_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A1CUJ5/set/pfam/Cl0001",
            "/api/protein/reviewed/A1CUJ5/set/pfam/Cl0001",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)


class StructureSetTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/structure/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        urls = ["/api/structure/pdb/set/"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_structure_with_set_count(self):
        urls = [f"/api/structure/pdb/{pdb}/set/" for pdb in ["1JM7", "2BKM"]]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn(
                "sets",
                response.data,
                "'sets' should be one of the keys in the response",
            )
            self._check_set_count_overview(response.data)

    def test_can_filter_structure_counter_with_organism_db(self):
        urls = ["/api/structure/set/pfam"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn(
                "structures",
                response.data["structures"]["pdb"],
                "'structures' should be one of the keys in the response",
            )
            self.assertIn(
                "sets",
                response.data["structures"]["pdb"],
                "'sets' should be one of the keys in the response",
            )

    def test_can_get_the_set_list_on_a_list(self):
        urls = ["/api/structure/pdb/set/pfam"]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
            )

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = ["/api/structure/pdb/1JM7/set/pfam"]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
                check_metadata_fn=self._check_structure_details,
            )

    def test_can_filter_counter_with_set_acc(self):
        urls = ["/api/structure/set/pfam/Cl0001"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_count_overview(response.data)

    def test_can_get_the_set_object_on_a_list(self):
        urls = ["/api/structure/pdb/set/pfam/Cl0001"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for org in result["sets"]:
                    self._check_set_from_searcher(org)

    def test_can_get_the_object_on_an_object(self):
        urls = ["/api/structure/pdb/1JM7/set/pfam/Cl0001"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)


class SetEntryTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_entry_count_on_a_list(self):
        urls = ["/api/set/pfam/entry"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_entry_count_overview(result)

    def test_can_get_the_entry_count_on_a_set(self):
        urls = ["/api/set/pfam/CL0001/entry"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn(
                "entries",
                response.data,
                "'entries' should be one of the keys in the response",
            )
            self._check_entry_count_overview(response.data)

    def test_can_filter_set_counter_with_entry_db(self):
        acc = "IPR003165"
        urls = [
            "/api/set/entry/pfam",
            "/api/set/entry/unintegrated",
            "/api/set/entry/unintegrated/pfam",
            "/api/set/entry/interpro/pfam",
            f"/api/set/entry/interpro/{acc}/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            if "pfam" in response.data["sets"]:
                self.assertIn(
                    "entries",
                    response.data["sets"]["pfam"],
                    "'entries' should be one of the keys in the response",
                )
                self.assertIn(
                    "sets",
                    response.data["sets"]["pfam"],
                    "'sets' should be one of the keys in the response",
                )

    def test_can_get_the_set_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/set/pfam/entry/pfam",
            "/api/set/pfam/entry/unintegrated",
            f"/api/set/pfam/entry/interpro/{acc}/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "entry",
                check_inner_subset_fn=self._check_entry_from_searcher,
            )

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/entry/pfam",
            "/api/set/pfam/CL0001/entry/unintegrated",
            "/api/set/pfam/CL0001/entry/unintegrated/pfam",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "entry",
                check_inner_subset_fn=self._check_entry_from_searcher,
                check_metadata_fn=self._check_set_details,
            )

    def test_can_filter_set_counter_with_acc(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/set/entry/pfam/{pfam}",
            f"/api/set/entry/pfam/{pfam_un}",
            f"/api/set/entry/interpro/{acc}/pfam/{pfam}",
            f"/api/set/entry/interpro/pfam/{pfam}",
            f"/api/set/entry/unintegrated/pfam/{pfam_un}",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_count_overview(response.data)

    def test_can_get_object_on_a_set_list(self):
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/set/pfam/entry/unintegrated/pfam/{pfam_un}",
            f"/api/set/pfam/entry/integrated/pfam/{pfam}",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_set_details(result["metadata"], False)
                for st in result["entries"]:
                    self._check_entry_from_searcher(st)

    def test_can_get_an_object_from_the_set_object(self):
        urls = [
            "/api/set/pfam/CL0001/entry/pfam/PF02171",
            "/api/set/pfam/CL0002/entry/unintegrated/pfam/PF17176",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn("entries", response.data)
            for s in response.data["entries"]:
                self._check_entry_from_searcher(s)


class SetProteinTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        urls = ["/api/set/pfam/protein"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteins"
            )
            for result in response.data["results"]:
                self._check_protein_count_overview(result)

    def test_can_get_the_protein_count_on_a_set(self):
        urls = ["/api/set/pfam/CL0001/protein"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn(
                "proteins",
                response.data,
                "'proteins' should be one of the keys in the response",
            )
            self._check_protein_count_overview(response.data)

    def test_can_filter_set_counter_with_protein_db(self):
        urls = ["/api/set/protein/uniprot", "/api/set/protein/reviewed"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            if "pfam" in response.data["sets"]:
                self.assertIn(
                    "proteins",
                    response.data["sets"]["pfam"],
                    "'proteins' should be one of the keys in the response",
                )
                self.assertIn(
                    "sets",
                    response.data["sets"]["pfam"],
                    "'sets' should be one of the keys in the response",
                )

    def test_can_get_the_set_list_on_a_list(self):
        urls = ["/api/set/pfam/protein/reviewed"]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda p: self._check_match(
                    p, include_coordinates=False
                ),
            )

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/protein/reviewed",
            "/api/set/pfam/CL0001/protein/uniprot",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda p: self._check_match(
                    p, include_coordinates=False
                ),
                check_metadata_fn=self._check_set_details,
            )

    # TODO: 📝 Replace the rest of tests like the 2 ones above

    def test_can_filter_set_counter_with_acc(self):
        urls = ["/api/set/protein/uniprot/M5ADK6", "/api/set/protein/reviewed/M5ADK6"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_count_overview(response.data)

    def test_can_get_object_on_a_set_list(self):
        urls = ["/api/set/pfam/protein/uniprot/a1cuj5"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteins"
            )
            for result in response.data["results"]:
                self._check_set_details(result["metadata"], False)
                for st in result["proteins"]:
                    self._check_match(st, include_coordinates=False)

    def test_can_get_an_object_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/protein/uniprot/A1CUJ5",
            "/api/set/pfam/Cl0001/protein/reviewed/A1CUJ5",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn("proteins", response.data)
            for s in response.data["proteins"]:
                self._check_match(s, include_coordinates=False)


class SetStructureTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_structure_count_on_a_list(self):
        urls = ["/api/set/pfam/structure"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "structures"
            )
            for result in response.data["results"]:
                self._check_structure_count_overview(result)

    def test_can_get_the_structure_count_on_a_set(self):
        urls = ["/api/set/pfam/CL0001/structure"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn(
                "structures",
                response.data,
                "'structures' should be one of the keys in the response",
            )
            self._check_structure_count_overview(response.data)

    def test_can_filter_set_counter_with_structure_db(self):
        urls = ["/api/set/structure/pdb"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            if "pfam" in response.data["sets"]:
                self.assertIn(
                    "structures",
                    response.data["sets"]["pfam"],
                    "'structures' should be one of the keys in the response",
                )
                self.assertIn(
                    "sets",
                    response.data["sets"]["pfam"],
                    "'sets' should be one of the keys in the response",
                )

    def test_can_get_the_set_list_on_a_list(self):
        urls = ["/api/set/pfam/structure/pdb"]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "structure",
                check_inner_subset_fn=self._check_structure_chain_details,
            )

    def test_can_get_a_list_from_the_set_object(self):
        urls = ["/api/set/pfam/Cl0001/structure/pdb"]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "structure",
                check_metadata_fn=lambda m: self._check_set_details(m, True),
                check_inner_subset_fn=self._check_structure_chain_details,
            )

    def test_can_filter_set_counter_with_acc(self):
        urls = ["/api/set/structure/pdb/1JM7", "/api/set/structure/pdb/2bkm"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_count_overview(response.data)

    def test_can_get_object_on_a_set_list(self):
        urls = ["/api/set/pfam/structure/pdb/1JM7"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "structures"
            )
            for result in response.data["results"]:
                self._check_set_details(result["metadata"], False)
                for st in result["structures"]:
                    self._check_structure_chain_details(st)

    def test_can_get_an_object_from_the_set_object(self):
        urls = ["/api/set/pfam/Cl0001/structure/pdb/1JM7"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn("structures", response.data)
            for s in response.data["structures"]:
                self._check_structure_chain_details(s)


class SetAlignmentTests(InterproRESTTestCase):
    def test_can_get_the_set_alignments(self):
        clan = "cl0001"
        response = self.client.get(f"/api/set/pfam/{clan}?alignments")
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_can_get_the_set_alignment(self):
        clan = "cl0001"
        pfam = "pf02171"
        response = self.client.get(f"/api/set/pfam/{clan}?alignments={pfam}")
        self.assertEqual(response.status_code, status.HTTP_410_GONE)
