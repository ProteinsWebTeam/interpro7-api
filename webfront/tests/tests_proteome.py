from rest_framework import status

from webfront.models import Proteome
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class ProteomeFixturesTest(InterproRESTTestCase):
    def test_the_fixtures_are_loaded(self):
        proteomes = Proteome.objects.all()
        self.assertEqual(proteomes.count(), 4)
        names = [t.name for t in proteomes]
        self.assertIn("Lactobacillus brevis KB290", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("proteomes", response.data)
        self.assertIn("uniprot", response.data["proteomes"])

    def test_can_read_proteome_list(self):
        response = self.client.get("/api/proteome/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 4)

    def test_can_read_proteome_id(self):
        response = self.client.get("/api/proteome/uniprot/UP000012042")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_details(response.data["metadata"])

    def test_can_filter_by_is_reference_false(self):
        response = self.client.get("/api/proteome/uniprot/?is_reference=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        for result in response.data["results"]:
            self.assertIn("metadata", result)
            self.assertIn("is_reference", result["metadata"])
            self.assertEqual(result["metadata"]["is_reference"], False)

    def test_can_filter_by_entry_and_is_reference_true(self):
        response = self.client.get(
            "/api/proteome/uniprot/entry/InterPro/?is_reference=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)
        for result in response.data["results"]:
            self.assertIn("metadata", result)
            self.assertIn("is_reference", result["metadata"])
            self.assertEqual(result["metadata"]["is_reference"], True)

    def test_can_filter_by_is_reference_false(self):
        response = self.client.get(
            "/api/proteome/uniprot/entry/InterPro/?is_reference=false"
        )
        # Should consider adding a fixture to return some results for this query
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class EntryProteomeTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/entry/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)
        self._check_proteome_count_overview(response.data)

    def test_can_get_the_proteome_count_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/proteome/",
            "/api/entry/pfam/proteome/",
            "/api/entry/unintegrated/proteome/",
            "/api/entry/interpro/pfam/proteome/",
            "/api/entry/unintegrated/pfam/proteome/",
            f"/api/entry/interpro/{acc}/pfam/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                self._check_proteome_count_overview(result)

    def test_urls_that_return_entry_with_proteome_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/entry/interpro/{acc}/proteome",
            f"/api/entry/pfam/{pfam}/proteome",
            f"/api/entry/pfam/{pfam_un}/proteome",
            f"/api/entry/interpro/{acc}/pfam/{pfam}/proteome",
            f"/api/entry/interpro/pfam/{pfam}/proteome",
            f"/api/entry/unintegrated/pfam/{pfam_un}/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn(
                "proteomes",
                response.data,
                "'proteomes' should be one of the keys in the response",
            )
            self._check_proteome_count_overview(response.data)

    def test_can_filter_entry_counter_with_proteome_db(self):
        url = "/api/entry/proteome/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(
            "proteomes",
            response.data["entries"]["integrated"],
            "'proteomes' should be one of the keys in the response",
        )
        if response.data["entries"]["unintegrated"] != 0:
            self.assertIn(
                "proteomes",
                response.data["entries"]["unintegrated"],
                "'proteomes' should be one of the keys in the response",
            )

    def test_can_get_the_proteome_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/pfam/proteome/uniprot",
            "/api/entry/interpro/pfam/proteome/uniprot",
            "/api/entry/unintegrated/pfam/proteome/uniprot",
            f"/api/entry/interpro/{acc}/pfam/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes_url"
            )
            response = self.client.get(url + "?show-subset")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteome_subset"
            )
            for result in response.data["results"]:
                for org in result["proteome_subset"]:
                    self._check_proteome_from_searcher(org)

    def test_can_get_the_proteome_list_on_an_object(self):
        urls = [
            "/api/entry/interpro/IPR003165/proteome/uniprot",
            "/api/entry/pfam/PF02171/proteome/uniprot",
            "/api/entry/unintegrated/pfam/PF17176/proteome/uniprot",
            "/api/entry/interpro/IPR003165/pfam/PF02171/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn("proteomes_url", response.data)
            response = self.client.get(url + "?show-subset")
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn("proteome_subset", response.data)
            for org in response.data["proteome_subset"]:
                self._check_proteome_from_searcher(org)

    def test_can_filter_entry_counter_with_proteome_acc(self):
        urls = [
            "/api/entry/proteome/uniprot/UP000006701",
            "/api/entry/proteome/uniprot/up000012042",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_count_overview(response.data)

    def test_can_get_the_proteome_object_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/pfam/proteome/uniprot/UP000006701",
            "/api/entry/interpro/pfam/proteome/uniprot/UP000006701",
            f"/api/entry/interpro/{acc}/pfam/proteome/uniprot/UP000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                for org in result["proteomes"]:
                    self._check_proteome_from_searcher(org)

    def test_can_get_the_proteome_object_on_an_object(self):
        urls = [
            "/api/entry/pfam/PF02171/proteome/uniprot/up000006701",
            "/api/entry/interpro/IPR003165/proteome/uniprot/up000006701",
            "/api/entry/interpro/pfam/PF02171/proteome/uniprot/up000006701",
            "/api/entry/interpro/IPR003165/pfam/PF02171/proteome/uniprot/up000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn("proteomes", response.data)
            for org in response.data["proteomes"]:
                self._check_proteome_from_searcher(org)


class ProteinProteomeTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/protein/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_proteome_count_on_a_list(self):
        urls = [
            "/api/protein/reviewed/proteome/",
            "/api/protein/unreviewed/proteome/",
            "/api/protein/uniprot/proteome/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                self._check_proteome_count_overview(result)

    def test_urls_that_return_protein_with_proteome_count(self):
        reviewed = "A1CUJ5"
        unreviewed = "P16582"
        urls = [
            f"/api/protein/uniprot/{reviewed}/proteome/",
            f"/api/protein/uniprot/{unreviewed}/proteome/",
            f"/api/protein/reviewed/{reviewed}/proteome/",
            f"/api/protein/unreviewed/{unreviewed}/proteome/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn(
                "proteomes",
                response.data,
                "'proteomes' should be one of the keys in the response",
            )
            self._check_proteome_count_overview(response.data)

    def test_can_filter_protein_counter_with_proteome_db(self):
        url = "/api/protein/proteome/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(
            "proteins",
            response.data["proteins"]["uniprot"],
            "'proteins' should be one of the keys in the response",
        )
        self.assertIn(
            "proteomes",
            response.data["proteins"]["uniprot"],
            "'proteomes' should be one of the keys in the response",
        )
        if "reviewed" in response.data["proteins"]:
            self.assertIn(
                "proteins",
                response.data["proteins"]["reviewed"],
                "'proteins' should be one of the keys in the response",
            )
            self.assertIn(
                "proteomes",
                response.data["proteins"]["reviewed"],
                "'proteomes' should be one of the keys in the response",
            )
        if "unreviewed" in response.data["proteins"]:
            self.assertIn(
                "proteins",
                response.data["proteins"]["unreviewed"],
                "'proteins' should be one of the keys in the response",
            )
            self.assertIn(
                "proteomes",
                response.data["proteins"]["unreviewed"],
                "'proteomes' should be one of the keys in the response",
            )

    def test_can_get_the_proteome_list_on_a_list(self):
        urls = [
            "/api/protein/unreviewed/proteome/uniprot",
            "/api/protein/uniprot/proteome/uniprot",
            "/api/protein/reviewed/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes_url"
            )
            response = self.client.get(url + "?show-subset")
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteome_subset"
            )
            for result in response.data["results"]:
                for org in result["proteome_subset"]:
                    self._check_proteome_from_searcher(org)

    def test_can_get_the_proteome_list_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/proteome/uniprot",
            "/api/protein/unreviewed/P16582/proteome/uniprot/",
            "/api/protein/reviewed/A1CUJ5/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn("proteomes_url", response.data)
            response = self.client.get(url + "?show-subset")
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn("proteome_subset", response.data)
            for org in response.data["proteome_subset"]:
                self._check_proteome_from_searcher(org)

    def test_can_filter_counter_with_proteome_acc(self):
        urls = [
            "/api/protein/proteome/uniprot/UP000006701",
            "/api/protein/proteome/uniprot/up000030104",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_count_overview(response.data)

    def test_can_get_the_proteome_object_on_a_list(self):
        urls = [
            "/api/protein/unreviewed/proteome/uniprot/up000030104",
            "/api/protein/uniprot/proteome/uniprot/UP000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                for org in result["proteomes"]:
                    self._check_proteome_from_searcher(org)

    def test_can_get_the_proteome_object_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/proteome/uniprot/up000030104",
            "/api/protein/reviewed/A1CUJ5/proteome/uniprot/up000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn("proteomes", response.data)
            for org in response.data["proteomes"]:
                self._check_proteome_from_searcher(org)


class StructureProteomeTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/structure/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_proteome_count_on_a_list(self):
        url = "/api/structure/pdb/proteome/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "proteomes")
        for result in response.data["results"]:
            self._check_proteome_count_overview(result)

    def test_urls_that_return_structure_with_proteome_count(self):
        urls = [
            f"/api/structure/pdb/{pdb}/proteome/" for pdb in ["1JM7", "2BKM", "1T2V"]
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn(
                "proteomes",
                response.data,
                "'proteomes' should be one of the keys in the response",
            )
            self._check_proteome_count_overview(response.data)

    def test_can_filter_structure_counter_with_proteome_db(self):
        url = "/api/structure/proteome/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(
            "structures",
            response.data["structures"]["pdb"],
            "'structures' should be one of the keys in the response",
        )
        self.assertIn(
            "proteomes",
            response.data["structures"]["pdb"],
            "'proteomes' should be one of the keys in the response",
        )

    def test_can_get_the_proteome_list_on_a_list(self):
        url = "/api/structure/pdb/proteome/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(
            response.data["results"], "proteomes_url"
        )
        response = self.client.get(url + "?show-subset")
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(
            response.data["results"], "proteome_subset"
        )
        for result in response.data["results"]:
            for org in result["proteome_subset"]:
                self._check_proteome_from_searcher(org)

    def test_can_get_the_proteome_list_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/proteome/uniprot",
            "/api/structure/pdb/1JZ8/proteome/uniprot",
            "/api/structure/pdb/1JM7/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn("proteomes_url", response.data)
            response = self.client.get(url + "?show-subset")
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn("proteome_subset", response.data)
            for org in response.data["proteome_subset"]:
                self._check_proteome_from_searcher(org)

    def test_can_filter_counter_with_proteome_acc(self):
        urls = [
            "/api/structure/proteome/uniprot/UP000006701",
            "/api/structure/proteome/uniprot/up000030104",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_count_overview(response.data)

    def test_can_get_the_proteome_object_on_a_list(self):
        urls = [
            "/api/structure/pdb/proteome/uniprot/up000030104",
            "/api/structure/pdb/proteome/uniprot/UP000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                for org in result["proteomes"]:
                    self._check_proteome_from_searcher(org)

    def test_can_get_the_proteome_object_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/proteome/uniprot/up000030104",
            "/api/structure/pdb/1JM7/proteome/uniprot/up000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn("proteomes", response.data)
            for org in response.data["proteomes"]:
                self._check_proteome_from_searcher(org)


class SetProteomeTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/set/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_proteome_count_overview(response.data)

    def test_can_get_the_proteome_count_on_a_list(self):
        urls = [
            "/api/set/pfam/proteome",
            #            "/api/set/kegg/proteome",
            #            "/api/set/kegg/KEGG01/node/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                self._check_proteome_count_overview(result)

    def test_can_get_the_proteome_count_on_a_set(self):
        urls = [
            "/api/set/pfam/CL0001/proteome",
            #            "/api/set/kegg/KEGG01/proteome",
            #            "/api/set/kegg/KEGG01/node/KEGG01-1/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn(
                "proteomes",
                response.data,
                "'proteomes' should be one of the keys in the response",
            )
            self._check_proteome_count_overview(response.data)

    def test_can_filter_set_counter_with_structure_db(self):
        url = "/api/set/proteome/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIsInstance(response.data, dict)
        # if "kegg" in response.data["sets"]:
        #     self.assertIn("proteomes", response.data["sets"]["kegg"],
        #                   "'proteomes' should be one of the keys in the response")
        #     self.assertIn("sets", response.data["sets"]["kegg"],
        #                   "'sets' should be one of the keys in the response")
        if "pfam" in response.data["sets"]:
            self.assertIn(
                "proteomes",
                response.data["sets"]["pfam"],
                "'proteomes' should be one of the keys in the response",
            )
            self.assertIn(
                "sets",
                response.data["sets"]["pfam"],
                "'sets' should be one of the keys in the response",
            )

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/set/pfam/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes_url"
            )
            response = self.client.get(url + "?show-subset")
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteome_subset"
            )
            for result in response.data["results"]:
                for s in result["proteome_subset"]:
                    self._check_proteome_from_searcher(s)

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/proteome/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"], True)
            self.assertIn("proteomes_url", response.data)
            response = self.client.get(url + "?show-subset")
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn("proteome_subset", response.data)
            for st in response.data["proteome_subset"]:
                self._check_proteome_from_searcher(st)

    def test_can_filter_set_counter_with_acc(self):
        urls = [
            "/api/set/proteome/uniprot/UP000012042",
            "/api/set/proteome/uniprot/UP000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_count_overview(response.data)

    def test_can_get_object_on_a_set_list(self):
        urls = [
            #            "/api/set/kegg/proteome/uniprot/up000030104",
            #            "/api/set/kegg/proteome/uniprot/up000006701",
            "/api/set/pfam/proteome/uniprot/UP000012042",
            #            "/api/set/kegg/kegg01/node/proteome/uniprot/up000030104",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"], "proteomes"
            )
            for result in response.data["results"]:
                self._check_set_details(result["metadata"], False)
                for st in result["proteomes"]:
                    self._check_proteome_from_searcher(st)

    def test_can_get_an_object_from_the_set_object(self):
        urls = [
            #            "/api/set/kegg/kegg01/proteome/uniprot/UP000006701",
            #            "/api/set/kegg/kegg01/node/kegg01-1/proteome/uniprot/UP000006701",
            "/api/set/pfam/Cl0001/proteome/uniprot/UP000006701"
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn("proteomes", response.data)
            for s in response.data["proteomes"]:
                self._check_proteome_from_searcher(s)


class ProteomeEntryTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/proteome/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_entry_count_on_a_list(self):
        url = "/api/proteome/uniprot/entry"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "entries")
        for result in response.data["results"]:
            self._check_entry_count_overview(result)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/entry",
            "/api/proteome/uniprot/UP000006701/entry",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"])
            self.assertIn(
                "entries",
                response.data,
                "'entries' should be one of the keys in the response",
            )
            self._check_entry_count_overview(response.data)

    def test_can_filter_proteomecounter_with_entry_db(self):
        acc = "IPR003165"
        urls = [
            "/api/proteome/entry/interpro",
            "/api/proteome/entry/pfam",
            "/api/proteome/entry/unintegrated",
            "/api/proteome/entry/unintegrated/pfam",
            "/api/proteome/entry/interpro/pfam",
            f"/api/proteome/entry/interpro/{acc}/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            self.assertIn(
                "uniprot",
                response.data["proteomes"],
                "'uniprot' should be one of the keys in the response",
            )
            self.assertIn(
                "proteomes",
                response.data["proteomes"]["uniprot"],
                "'proteome' should be one of the keys in the response",
            )
            self.assertIn(
                "entries",
                response.data["proteomes"]["uniprot"],
                "'entries' should be one of the keys in the response",
            )

    def test_can_get_a_list_from_the_proteome_list(self):
        urls = [
            "/api/proteome/uniprot/entry/interpro",
            "/api/proteome/uniprot/entry/pfam",
            "/api/proteome/uniprot/entry/unintegrated",
            "/api/proteome/uniprot/entry/interpro/pfam",
            "/api/proteome/uniprot/entry/interpro/IPR003165/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "entry",
                check_inner_subset_fn=self._check_entry_from_searcher,
                check_metadata_fn=lambda metadata: self._check_proteome_details(
                    metadata, False
                ),
            )

    def test_can_get_a_list_from_the_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/entry/pfam",
            "/api/proteome/uniprot/UP000006701/entry/unintegrated",
            "/api/proteome/uniprot/UP000006701/entry/interpro/pfam",
            "/api/proteome/uniprot/UP000006701/entry/unintegrated/pfam",
            "/api/proteome/uniprot/UP000006701/entry/interpro/IPR003165/smart",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "entry",
                check_inner_subset_fn=self._check_entry_from_searcher,
                check_metadata_fn=self._check_proteome_details,
            )

    def test_can_filter_proteome_counter_with_acc(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/proteome/entry/interpro/{acc}",
            f"/api/proteome/entry/pfam/{pfam}",
            f"/api/proteome/entry/pfam/{pfam_un}",
            f"/api/proteome/entry/interpro/{acc}/pfam/{pfam}",
            f"/api/proteome/entry/interpro/pfam/{pfam}",
            f"/api/proteome/entry/unintegrated/pfam/{pfam_un}",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_count_overview(response.data)

    def test_can_get_object_on_a_proteome_list(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/proteome/uniprot/entry/interpro/{acc}",
            f"/api/proteome/uniprot/entry/pfam/{pfam}",
            f"/api/proteome/uniprot/entry/unintegrated/pfam/{pfam_un}",
            f"/api/proteome/uniprot/entry/unintegrated/pfam/{pfam_un}",
            f"/api/proteome/uniprot/entry/interpro/pfam/{pfam}",
            f"/api/proteome/uniprot/entry/unintegrated/pfam/{pfam_un}",
            f"/api/proteome/uniprot/entry/interpro/IPR003165/pfam/{pfam}",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_proteome_details(result["metadata"], False)
                for st in result["entries"]:
                    self._check_entry_from_searcher(st)

    def test_can_get_an_object_from_the_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/entry/pfam/pf02171",
            "/api/proteome/uniprot/UP000006701/entry/unintegrated/pfam/pf17176",
            "/api/proteome/uniprot/UP000006701/entry/interpro/pfam/pf02171",
            "/api/proteome/uniprot/UP000006701/entry/unintegrated/pfam/pf17176",
            "/api/proteome/uniprot/UP000006701/entry/interpro/IPR003165/smart/sm00950",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"], False)
            self.assertIn("entries", response.data)
            for st in response.data["entries"]:
                self._check_entry_from_searcher(st)


class ProteomeProteinTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/proteome/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        url = "/api/proteome/uniprot/protein"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
        for result in response.data["results"]:
            self._check_protein_count_overview(result)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/protein",
            "/api/proteome/uniprot/UP000006701/protein",
            "/api/proteome/uniprot/UP000030104/protein",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"])
            self.assertIn(
                "proteins",
                response.data,
                "'proteins' should be one of the keys in the response",
            )
            self._check_protein_count_overview(response.data)

    def test_can_filter_protein_counter_with_proteome_db(self):
        urls = [
            "/api/proteome/protein/uniprot",
            "/api/proteome/protein/reviewed",
            "/api/proteome/protein/unreviewed",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            self.assertIn(
                "uniprot",
                response.data["proteomes"],
                "'proteuniprotome' should be one of the keys in the response",
            )
            self.assertIn(
                "proteomes",
                response.data["proteomes"]["uniprot"],
                "'proteomes' should be one of the keys in the response",
            )
            self.assertIn(
                "proteins",
                response.data["proteomes"]["uniprot"],
                "'entries' should be one of the keys in the response",
            )

    def test_can_get_a_list_from_the_proteome_list(self):
        urls = [
            "/api/proteome/uniprot/protein/uniprot",
            "/api/proteome/uniprot/protein/unreviewed",
            "/api/proteome/uniprot/protein/reviewed",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda p: self._check_match(
                    p, include_coordinates=False
                ),
                check_metadata_fn=lambda m: self._check_proteome_details(m, False),
            )

    def test_can_get_a_list_from_the_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/protein/uniprot",
            "/api/proteome/uniprot/UP000030104/protein/unreviewed",
            "/api/proteome/uniprot/UP000006701/protein/reviewed",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda p: self._check_match(
                    p, include_coordinates=False
                ),
                check_metadata_fn=lambda m: self._check_proteome_details(m, False),
            )

    def test_can_filter_proteome_counter_with_acc(self):
        urls = [
            "/api/proteome/protein/uniprot/M5ADK6",
            "/api/proteome/protein/unreviewed/A0A0A2L2G2",
            "/api/proteome/protein/reviewed/M5ADK6",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_count_overview(response.data)

    def test_can_get_object_on_a_proteome_list(self):
        urls = [
            "/api/proteome/uniprot/protein/uniprot/P16582",
            "/api/proteome/uniprot/protein/unreviewed/A0A0A2L2G2",
            "/api/proteome/uniprot/protein/reviewed/M5ADK6",
            "/api/proteome/uniprot/protein/reviewed/a1cuj5",
        ]
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
                self._check_proteome_details(result["metadata"], False)
                for st in result["proteins"]:
                    self._check_match(st, include_coordinates=False)

    def test_can_get_an_object_from_the_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/protein/uniprot/a1cuj5",
            "/api/proteome/uniprot/UP000030104/protein/unreviewed/A0A0A2L2G2",
            "/api/proteome/uniprot/UP000030104/protein/unreviewed/A0A0A2L2G2",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"], False)
            self.assertIn("proteins", response.data)
            for st in response.data["proteins"]:
                self._check_match(st, include_coordinates=False)


class ProteomeStructureTest(InterproRESTTestCase):
    def test_can_get_the_proteome_count(self):
        response = self.client.get("/api/proteome/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        url = "/api/proteome/uniprot/structure"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "structures")
        for result in response.data["results"]:
            self._check_structure_count_overview(result)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/40296/structure",
            "/api/proteome/uniprot/2/structure",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"])
            self.assertIn(
                "structures",
                response.data,
                "'structures' should be one of the keys in the response",
            )
            self._check_structure_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/structure",
            "/api/proteome/uniprot/UP000006701/structure",
            "/api/proteome/uniprot/UP000030104/structure",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"])
            self.assertIn(
                "structures",
                response.data,
                "'structures' should be one of the keys in the response",
            )
            self._check_structure_count_overview(response.data)

    def test_can_filter_structure_counter_with_proteome_db(self):
        url = "/api/proteome/structure/pdb"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIsInstance(response.data, dict)
        self.assertIn(
            "uniprot",
            response.data["proteomes"],
            "'uniprot' should be one of the keys in the response",
        )
        self.assertIn(
            "proteomes",
            response.data["proteomes"]["uniprot"],
            "'proteomes' should be one of the keys in the response",
        )
        self.assertIn(
            "structures",
            response.data["proteomes"]["uniprot"],
            "'structures' should be one of the keys in the response",
        )

    def test_can_get_a_list_from_the_proteome_list(self):
        url = "/api/proteome/uniprot/structure/pdb"
        self._check_list_url_with_and_without_subset(
            url,
            "structure",
            check_metadata_fn=lambda m: self._check_proteome_details(m, False),
            check_inner_subset_fn=self._check_structure_chain_details,
        )

    def test_can_get_a_list_from_the_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/structure/pdb",
            "/api/proteome/uniprot/UP000030104/structure/pdb",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "structure",
                check_metadata_fn=lambda m: self._check_proteome_details(m, False),
                check_inner_subset_fn=self._check_structure_chain_details,
            )

    def test_can_filter_proteome_counter_with_acc(self):
        urls = ["/api/proteome/structure/pdb/1JM7", "/api/proteome/structure/pdb/1JZ8"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_count_overview(response.data)

    def test_can_get_object_on_a_proteome_list(self):
        urls = [
            "/api/proteome/uniprot/structure/pdb/1JM7",
            "/api/proteome/uniprot/structure/pdb/1JZ8",
        ]
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
                self._check_proteome_details(result["metadata"], False)
                for st in result["structures"]:
                    self._check_structure_chain_details(st)

    def test_can_get_an_object_from_the_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/structure/pdb/1jm7",
            "/api/proteome/uniprot/UP000030104/structure/pdb/1t2v",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"], False)
            self.assertIn("structures", response.data)
            for st in response.data["structures"]:
                self._check_structure_chain_details(st)


class ProteomeSetTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/proteome/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_proteome_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        url = "/api/proteome/uniprot/set"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "sets")
        for result in response.data["results"]:
            self._check_set_count_overview(result)

    def test_urls_that_return_proteome_with_set_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/set",
            "/api/proteome/uniprot/UP000006701/set",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"])
            self.assertIn(
                "sets",
                response.data,
                "'sets' should be one of the keys in the response",
            )
            self._check_set_count_overview(response.data)

    def test_can_filter_proteome_counter_with_proteome_db(self):
        urls = [
            "/api/proteome/set/pfam",
            #            "/api/proteome/set/kegg",
            #            "/api/proteome/set/kegg/kegg01/node",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn(
                "uniprot",
                response.data["proteomes"],
                "'uniprot' should be one of the keys in the response",
            )
            self.assertIn(
                "sets",
                response.data["proteomes"]["uniprot"],
                "'sets' should be one of the keys in the response",
            )
            self.assertIn(
                "proteomes",
                response.data["proteomes"]["uniprot"],
                "'proteomes' should be one of the keys in the response",
            )

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/proteome/uniprot/set/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
            )

    def test_can_get_the_set_list_on_a_proteome_object(self):
        urls = [
            "/api/proteome/uniprot/UP000006701/set/pfam",
            #            "/api/proteome/uniprot/UP000006701/set/kegg",
            #            "/api/proteome/uniprot/UP000006701/set/kegg/kegg01/node",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
                check_metadata_fn=self._check_proteome_details,
            )

    def test_can_filter_counter_with_set_acc(self):
        urls = [
            "/api/proteome/set/pfam/Cl0001",
            #            "/api/proteome/set/kegg/kegg01",
            #            "/api/proteome/set/kegg/kegg01/node/KEGG01-1",
            #            "/api/proteome/set/kegg/kegg01/node/KEGG01-2",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_count_overview(response.data)

    def test_can_get_the_set_object_on_a_list(self):
        urls = [
            #            "/api/proteome/uniprot/set/kegg/kegg01",
            #            "/api/proteome/uniprot/set/kegg/kegg01/node/kegg01-1",
            "/api/proteome/uniprot/set/pfam/Cl0001"
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
            #            "/api/proteome/uniprot/UP000006701/set/kegg/kegg01",
            #            "/api/proteome/uniprot/UP000006701/set/kegg/kegg01/node/kegg01-1",
            "/api/proteome/uniprot/UP000006701/set/pfam/Cl0001"
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)
