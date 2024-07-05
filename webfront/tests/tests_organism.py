from rest_framework import status

from webfront.models import Taxonomy
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class TaxonomyFixturesTest(InterproRESTTestCase):
    def test_the_fixtures_are_loaded(self):
        taxa = Taxonomy.objects.all()
        self.assertEqual(taxa.count(), 7)
        names = [t.scientific_name for t in taxa]
        self.assertIn("ROOT", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("taxa", response.data)
        self.assertIn("uniprot", response.data["taxa"])
        # self.assertIn("proteome", response.data["taxa"])

    def test_can_read_taxonomy_list(self):
        response = self.client.get("/api/taxonomy/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 7)

    def test_can_read_taxonomy_id(self):
        response = self.client.get("/api/taxonomy/uniprot/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_details(response.data["metadata"])


class TaxonomyProteomeFixturesTest(InterproRESTTestCase):
    def test_can_read_taxonomy_with_proteome_list(self):
        response = self.client.get("/api/taxonomy/uniprot/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "proteomes")
        self.assertEqual(len(response.data["results"]), 4)

    def test_can_read_taxonomy_leaf_id_with_proteome_count(self):
        response = self.client.get("/api/taxonomy/uniprot/40296/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self.assertIn("proteomes", response.data)
        self.assertIn("uniprot", response.data["proteomes"])
        self.assertEqual(response.data["proteomes"]["uniprot"], 1)

    def test_can_read_taxonomy_leaf_id_with_proteomes(self):
        response = self.client.get("/api/taxonomy/uniprot/40296/proteome/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self.assertIn("proteomes_url", response.data)
        response = self.client.get(
            "/api/taxonomy/uniprot/40296/proteome/uniprot?show-subset"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("proteome_subset", response.data)
        self.assertEqual(len(response.data["proteome_subset"]), 1)

    def test_can_read_taxonomy_node_id_with_proteomes(self):
        response = self.client.get("/api/taxonomy/uniprot/2579/proteome/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self.assertIn("proteomes_url", response.data)
        response = self.client.get(
            "/api/taxonomy/uniprot/2579/proteome/uniprot?show-subset"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("proteome_subset", response.data)
        self.assertEqual(len(response.data["proteome_subset"]), 3)

    def test_can_read_proteome_id_including_tax_id(self):
        lineage = [1, 2, 40296]
        for taxon in lineage:
            response = self.client.get(
                f"/api/taxonomy/uniprot/{taxon}/proteome/uniprot/UP000030104"
            )
            self.assertEqual(
                response.status_code, status.HTTP_200_OK, f"failed at {str(taxon)}"
            )
            self.assertIn("proteomes", response.data)
            self.assertEqual(len(response.data["proteomes"]), 1)
            self.assertIn("accession", response.data["proteomes"][0])
            self.assertIn("taxonomy", response.data["proteomes"][0])


class EntryTaxonomyTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/entry/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_entry_count_overview(response.data)
        self._check_taxonomy_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/taxonomy/",
            "/api/entry/pfam/taxonomy/",
            "/api/entry/unintegrated/taxonomy/",
            "/api/entry/interpro/pfam/taxonomy/",
            "/api/entry/unintegrated/pfam/taxonomy/",
            f"/api/entry/interpro/{acc}/pfam/taxonomy",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                self._check_taxonomy_count_overview(result)

    def test_urls_that_return_entry_with_taxonomy_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/entry/interpro/{acc}/taxonomy",
            f"/api/entry/pfam/{pfam}/taxonomy",
            f"/api/entry/pfam/{pfam_un}/taxonomy",
            f"/api/entry/interpro/{acc}/pfam/{pfam}/taxonomy",
            f"/api/entry/interpro/pfam/{pfam}/taxonomy",
            f"/api/entry/unintegrated/pfam/{pfam_un}/taxonomy",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn(
                "taxa",
                response.data,
                "'taxa' should be one of the keys in the response",
            )
            self._check_taxonomy_count_overview(response.data)

    def test_can_filter_entry_counter_with_taxonomy_db(self):
        url = "/api/entry/taxonomy/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(
            "taxa",
            response.data["entries"]["integrated"],
            "'taxa' should be one of the keys in the response",
        )
        if response.data["entries"]["unintegrated"] != 0:
            self.assertIn(
                "taxa",
                response.data["entries"]["unintegrated"],
                "'taxa' should be one of the keys in the response",
            )

    def test_can_get_the_taxonomy_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/taxonomy/uniprot",
            "/api/entry/unintegrated/taxonomy/uniprot",
            f"/api/entry/interpro/{acc}/pfam/taxonomy/uniprot",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "taxonomy",
                check_inner_subset_fn=self._check_taxonomy_from_searcher,
            )

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/entry/interpro/IPR003165/taxonomy/uniprot",
            "/api/entry/pfam/PF02171/taxonomy/uniprot",
            "/api/entry/unintegrated/pfam/PF17176/taxonomy/uniprot",
            "/api/entry/interpro/IPR003165/pfam/PF02171/taxonomy/uniprot",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "taxonomy",
                check_inner_subset_fn=self._check_taxonomy_from_searcher,
                check_metadata_fn=self._check_entry_details,
            )

    def test_can_filter_entry_counter_with_taxonomy_acc(self):
        urls = ["/api/entry/taxonomy/uniprot/2579", "/api/entry/taxonomy/uniprot/40296"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_count_overview(response.data)

    def test_can_get_the_taxonomy_object_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/taxonomy/uniprot/2579",
            "/api/entry/unintegrated/taxonomy/uniprot/2579",
            "/api/entry/unintegrated/taxonomy/uniprot/344612",
            f"/api/entry/interpro/{acc}/pfam/taxonomy/uniprot/344612",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                for org in result["taxa"]:
                    self._check_taxonomy_from_searcher(org)

    def test_can_get_thetaxonomy_object_on_an_object(self):
        urls = [
            "/api/entry/interpro/IPR003165/taxonomy/uniprot/40296",
            "/api/entry/unintegrated/pfam/PF17176/taxonomy/uniprot/344612",
            "/api/entry/unintegrated/pfam/PF17176/taxonomy/uniprot/1",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_entry_details(response.data["metadata"])
            self.assertIn("taxa", response.data)
            for org in response.data["taxa"]:
                self._check_taxonomy_from_searcher(org)


class ProteinTaxonomyTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/protein/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        urls = [
            "/api/protein/reviewed/taxonomy/",
            "/api/protein/unreviewed/taxonomy/",
            "/api/protein/uniprot/taxonomy/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                self._check_taxonomy_count_overview(result)

    def test_urls_that_return_protein_with_taxonomy_count(self):
        reviewed = "A1CUJ5"
        unreviewed = "P16582"
        urls = [
            f"/api/protein/uniprot/{reviewed}/taxonomy/",
            f"/api/protein/uniprot/{unreviewed}/taxonomy/",
            f"/api/protein/reviewed/{reviewed}/taxonomy/",
            f"/api/protein/unreviewed/{unreviewed}/taxonomy/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn(
                "taxa",
                response.data,
                "'taxa' should be one of the keys in the response",
            )
            self._check_taxonomy_count_overview(response.data)

    def test_can_filter_protein_counter_with_taxonomy_db(self):
        url = "/api/protein/taxonomy/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(
            "proteins",
            response.data["proteins"]["uniprot"],
            "'proteins' should be one of the keys in the response",
        )
        self.assertIn(
            "taxa",
            response.data["proteins"]["uniprot"],
            "'taxa' should be one of the keys in the response",
        )
        if "reviewed" in response.data["proteins"]:
            self.assertIn(
                "proteins",
                response.data["proteins"]["reviewed"],
                "'proteins' should be one of the keys in the response",
            )
            self.assertIn(
                "taxa",
                response.data["proteins"]["reviewed"],
                "'taxa' should be one of the keys in the response",
            )
        if "unreviewed" in response.data["proteins"]:
            self.assertIn(
                "proteins",
                response.data["proteins"]["unreviewed"],
                "'proteins' should be one of the keys in the response",
            )
            self.assertIn(
                "taxa",
                response.data["proteins"]["unreviewed"],
                "'taxa' should be one of the keys in the response",
            )

    def test_can_get_the_taxonomy_list_on_a_list(self):
        urls = [
            "/api/protein/unreviewed/taxonomy/uniprot",
            "/api/protein/reviewed/taxonomy/uniprot",
            "/api/protein/uniprot/taxonomy/uniprot",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "taxonomy",
                check_inner_subset_fn=self._check_taxonomy_from_searcher,
            )

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/taxonomy/uniprot",
            "/api/protein/unreviewed/P16582/taxonomy/uniprot/",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "taxonomy",
                check_inner_subset_fn=self._check_taxonomy_from_searcher,
                check_metadata_fn=self._check_protein_details,
            )

    def test_can_filter_counter_with_taxonomy_acc(self):
        urls = [
            "/api/protein/taxonomy/uniprot/2579",
            "/api/protein/taxonomy/uniprot/40296",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_count_overview(response.data)

    def test_can_get_the_taxonomy_object_on_a_list(self):
        urls = [
            "/api/protein/reviewed/taxonomy/uniprot/2579",
            "/api/protein/uniprot/taxonomy/uniprot/344612",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                for org in result["taxa"]:
                    self._check_taxonomy_from_searcher(org)

    def test_can_get_the_taxonomy_object_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/taxonomy/uniprot/40296",
            "/api/protein/unreviewed/P16582/taxonomy/uniprot/40296",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/2579",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/344612",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_protein_details(response.data["metadata"])
            self.assertIn("taxa", response.data)
            for org in response.data["taxa"]:
                self._check_taxonomy_from_searcher(org)


class StructureTaxonomyTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/structure/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        url = "/api/structure/pdb/taxonomy/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
        for result in response.data["results"]:
            self._check_taxonomy_count_overview(result)

    def test_urls_that_return_structure_with_taxonomy_count(self):
        urls = [
            f"/api/structure/pdb/{pdb}/taxonomy/" for pdb in ["1JM7", "2BKM", "1T2V"]
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn(
                "taxa",
                response.data,
                "'taxa' should be one of the keys in the response",
            )
            self._check_taxonomy_count_overview(response.data)

    def test_can_filter_structure_counter_with_taxonomy_db(self):
        url = "/api/structure/taxonomy/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIn(
            "structures",
            response.data["structures"]["pdb"],
            "'structures' should be one of the keys in the response",
        )
        self.assertIn(
            "taxa",
            response.data["structures"]["pdb"],
            "'taxa' should be one of the keys in the response",
        )

    def test_can_get_the_taxonomy_list_on_a_list(self):
        url = "/api/structure/pdb/taxonomy/uniprot"
        self._check_list_url_with_and_without_subset(
            url,
            "taxonomy",
            check_inner_subset_fn=self._check_taxonomy_from_searcher,
        )

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/taxonomy/uniprot",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "taxonomy",
                check_inner_subset_fn=self._check_taxonomy_from_searcher,
                check_metadata_fn=self._check_structure_details,
            )

    def test_can_filter_counter_with_taxonomy_acc(self):
        urls = [
            "/api/structure/taxonomy/uniprot/2579",
            "/api/structure/taxonomy/uniprot/40296",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_count_overview(response.data)

    def test_can_get_the_taxonomy_object_on_a_list(self):
        urls = [
            "/api/structure/pdb/taxonomy/uniprot/2",
            "/api/structure/pdb/taxonomy/uniprot/2579",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                for org in result["taxa"]:
                    self._check_taxonomy_from_searcher(org)

    def test_can_get_the_taxonomy_object_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/taxonomy/uniprot/40296",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot/1",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot/40296",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_structure_details(response.data["metadata"])
            self.assertIn("taxa", response.data)
            for org in response.data["taxa"]:
                self._check_taxonomy_from_searcher(org)


class SetTaxonomyTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_taxonomy_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        urls = [
            "/api/set/pfam/taxonomy",
            #            "/api/set/kegg/taxonomy",
            #            "/api/set/kegg/KEGG01/node/taxonomy",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                self._check_taxonomy_count_overview(result)

    def test_can_get_the_taxonomy_count_on_a_set(self):
        urls = [
            "/api/set/pfam/CL0001/taxonomy",
            #            "/api/set/kegg/KEGG01/taxonomy",
            #            "/api/set/kegg/KEGG01/node/KEGG01-1/taxonomy",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn(
                "taxa",
                response.data,
                "'taxa' should be one of the keys in the response",
            )
            self._check_taxonomy_count_overview(response.data)

    def test_can_filter_set_counter_with_structure_db(self):
        url = "/api/set/taxonomy/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIsInstance(response.data, dict)
        # if "kegg" in response.data["sets"]:
        #     self.assertIn("taxa", response.data["sets"]["kegg"],
        #                   "'taxa' should be one of the keys in the response")
        #     self.assertIn("sets", response.data["sets"]["kegg"],
        #                   "'sets' should be one of the keys in the response")
        if "pfam" in response.data["sets"]:
            self.assertIn(
                "taxa",
                response.data["sets"]["pfam"],
                "'taxa' should be one of the keys in the response",
            )
            self.assertIn(
                "sets",
                response.data["sets"]["pfam"],
                "'sets' should be one of the keys in the response",
            )

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            #            "/api/set/kegg/taxonomy/uniprot",
            #            "/api/set/kegg/kegg01/node/taxonomy/uniprot",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                for s in result["taxa"]:
                    self._check_taxonomy_from_searcher(s)

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/taxonomy/uniprot",
            #            "/api/set/kegg/kegg01/node/KEGG01-1/taxonomy/uniprot/",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "taxonomy",
                check_inner_subset_fn=self._check_taxonomy_from_searcher,
                check_metadata_fn=self._check_set_details,
            )

    def test_can_filter_set_counter_with_acc(self):
        urls = [
            "/api/set/taxonomy/uniprot/1",
            "/api/set/taxonomy/uniprot/2579",
            "/api/set/taxonomy/uniprot/344612",
            "/api/set/taxonomy/uniprot/1001583",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_count_overview(response.data)

    #     def test_can_get_object_on_a_set_list(self):
    #         urls = [
    # #            "/api/set/kegg/taxonomy/uniprot/2579",
    # #            "/api/set/kegg/taxonomy/uniprot/344612",
    #             ]
    #         for url in urls:
    #             response = self.client.get(url)
    #             self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
    #             self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
    #             self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
    #             for result in response.data["results"]:
    #                 self._check_set_details(result["metadata"], False)
    #                 for st in result["taxa"]:
    #                     self._check_taxonomy_from_searcher(st)

    def test_can_get_an_object_from_the_set_object(self):
        urls = [
            #            "/api/set/kegg/kegg01/taxonomy/uniprot/2",
            #            "/api/set/kegg/kegg01/taxonomy/uniprot/40296",
            #            "/api/set/kegg/kegg01/node/kegg01-1/taxonomy/uniprot/40296",
            "/api/set/pfam/Cl0001/taxonomy/uniprot/344612"
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_set_details(response.data["metadata"])
            self.assertIn("taxa", response.data)
            for s in response.data["taxa"]:
                self._check_taxonomy_from_searcher(s)


class TaxonomyEntryTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/taxonomy/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_entry_count_on_a_list(self):
        url = "/api/taxonomy/uniprot/entry"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "entries")
        for result in response.data["results"]:
            self._check_entry_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/taxonomy/uniprot/2579/entry")
        response2 = self.client.get("/api/taxonomy/uniprot/1001583/entry")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(
            response1.data["entries"]["all"], response2.data["entries"]["all"]
        )

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = ["/api/taxonomy/uniprot/40296/entry", "/api/taxonomy/uniprot/2/entry"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn(
                "entries",
                response.data,
                "'entries' should be one of the keys in the response",
            )
            self._check_entry_count_overview(response.data)

    def test_can_filter_taxonomy_counter_with_entry_db(self):
        acc = "IPR003165"
        urls = [
            "/api/taxonomy/entry/interpro",
            "/api/taxonomy/entry/pfam",
            "/api/taxonomy/entry/unintegrated",
            "/api/taxonomy/entry/unintegrated/pfam",
            "/api/taxonomy/entry/interpro/pfam",
            f"/api/taxonomy/entry/interpro/{acc}/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            self.assertIn(
                "uniprot",
                response.data["taxa"],
                "'uniprot' should be one of the keys in the response",
            )
            self.assertIn(
                "taxa",
                response.data["taxa"]["uniprot"],
                "'proteome' should be one of the keys in the response",
            )
            self.assertIn(
                "entries",
                response.data["taxa"]["uniprot"],
                "'entries' should be one of the keys in the response",
            )

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/entry/interpro",
            "/api/taxonomy/uniprot/entry/unintegrated",
            "/api/taxonomy/uniprot/entry/interpro/pfam",
            "/api/taxonomy/uniprot/entry/unintegrated/pfam",
            "/api/taxonomy/uniprot/entry/interpro/IPR003165/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "entry",
                check_inner_subset_fn=self._check_entry_from_searcher,
                check_metadata_fn=lambda m: self._check_taxonomy_details(m, False),
            )

    def test_can_get_a_list_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/entry/interpro",
            "/api/taxonomy/uniprot/1/entry/interpro/pfam",
            "/api/taxonomy/uniprot/2579/entry/unintegrated/pfam",
            "/api/taxonomy/uniprot/344612/entry/unintegrated/pfam",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "entry",
                check_inner_subset_fn=self._check_entry_from_searcher,
                check_metadata_fn=self._check_taxonomy_details,
            )

    def test_can_filter_taxonomy_counter_with_acc(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/taxonomy/entry/interpro/{acc}",
            f"/api/taxonomy/entry/pfam/{pfam}",
            f"/api/taxonomy/entry/pfam/{pfam_un}",
            f"/api/taxonomy/entry/interpro/{acc}/pfam/{pfam}",
            f"/api/taxonomy/entry/interpro/pfam/{pfam}",
            f"/api/taxonomy/entry/unintegrated/pfam/{pfam_un}",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_count_overview(response.data)

    def test_can_get_object_on_a_taxonomy_list(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            f"/api/taxonomy/uniprot/entry/interpro/{acc}",
            f"/api/taxonomy/uniprot/entry/unintegrated/pfam/{pfam_un}",
            f"/api/taxonomy/uniprot/entry/interpro/pfam/{pfam}",
            f"/api/taxonomy/uniprot/entry/interpro/IPR003165/pfam/{pfam}",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_taxonomy_details(result["metadata"], False)
                for st in result["entries"]:
                    self._check_entry_from_searcher(st)

    def test_can_get_an_object_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/entry/interpro/ipr003165",
            "/api/taxonomy/uniprot/1/entry/interpro/pfam/pf02171",
            "/api/taxonomy/uniprot/2579/entry/unintegrated/pfam/pf17176",
            "/api/taxonomy/uniprot/344612/entry/unintegrated/pfam/pf17176",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("entries", response.data)
            for st in response.data["entries"]:
                self._check_entry_from_searcher(st)


class TaxonomyProteinTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/taxonomy/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        url = "/api/taxonomy/uniprot/protein"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
        for result in response.data["results"]:
            self._check_protein_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/taxonomy/uniprot/2579/protein")
        response2 = self.client.get("/api/taxonomy/uniprot/1001583/protein")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(
            response1.data["proteins"]["uniprot"], response2.data["proteins"]["uniprot"]
        )

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/taxonomy/uniprot/40296/protein",
            "/api/taxonomy/uniprot/2/protein",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn(
                "proteins",
                response.data,
                "'proteins' should be one of the keys in the response",
            )
            self._check_protein_count_overview(response.data)

    def test_can_filter_protein_counter_with_taxonomy_db(self):
        urls = [
            "/api/taxonomy/protein/uniprot",
            "/api/taxonomy/protein/reviewed",
            "/api/taxonomy/protein/unreviewed",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIsInstance(response.data, dict)
            self.assertIn(
                "uniprot",
                response.data["taxa"],
                "'uniprot' should be one of the keys in the response",
            )
            self.assertIn(
                "taxa",
                response.data["taxa"]["uniprot"],
                "'taxa' should be one of the keys in the response",
            )
            self.assertIn(
                "proteins",
                response.data["taxa"]["uniprot"],
                "'proteins' should be one of the keys in the response",
            )

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/protein/uniprot",
            "/api/taxonomy/uniprot/protein/unreviewed",
            "/api/taxonomy/uniprot/protein/reviewed",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda p: self._check_match(
                    p, include_coordinates=False
                ),
                check_metadata_fn=lambda m: self._check_taxonomy_details(m, False),
            )

    def test_can_get_a_list_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/protein/uniprot",
            "/api/taxonomy/uniprot/1/protein/unreviewed",
            "/api/taxonomy/uniprot/2579/protein/reviewed",
            "/api/taxonomy/uniprot/344612/protein/reviewed",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "protein",
                check_inner_subset_fn=lambda p: self._check_match(
                    p, include_coordinates=False
                ),
                check_metadata_fn=lambda m: self._check_taxonomy_details(m, False),
            )

    def test_can_filter_taxonomy_counter_with_acc(self):
        urls = [
            "/api/taxonomy/protein/uniprot/M5ADK6",
            "/api/taxonomy/protein/unreviewed/A0A0A2L2G2",
            "/api/taxonomy/protein/reviewed/M5ADK6",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_count_overview(response.data)

    def test_can_get_object_on_a_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/protein/uniprot/P16582",
            "/api/taxonomy/uniprot/protein/unreviewed/A0A0A2L2G2",
            "/api/taxonomy/uniprot/protein/reviewed/M5ADK6",
            "/api/taxonomy/uniprot/protein/reviewed/a1cuj5",
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
                self._check_taxonomy_details(result["metadata"], False)
                for st in result["proteins"]:
                    self._check_match(st, include_coordinates=False)

    def test_can_get_an_object_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/protein/uniprot/p16582",
            "/api/taxonomy/uniprot/1/protein/reviewed/a1cuj5",
            "/api/taxonomy/uniprot/2579/protein/reviewed/a1cuj5",
            "/api/taxonomy/uniprot/344612/protein/reviewed/a1cuj5",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("proteins", response.data)
            for st in response.data["proteins"]:
                self._check_match(st, include_coordinates=False)


class TaxonomyStructureTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/taxonomy/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        url = "/api/taxonomy/uniprot/structure"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "structures")
        for result in response.data["results"]:
            self._check_structure_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/taxonomy/uniprot/1/structure")
        response2 = self.client.get("/api/taxonomy/uniprot/1001583/structure")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(
            response1.data["structures"]["pdb"], response2.data["structures"]["pdb"]
        )

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/taxonomy/uniprot/40296/structure",
            "/api/taxonomy/uniprot/2/structure",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn(
                "structures",
                response.data,
                "'structures' should be one of the keys in the response",
            )
            self._check_structure_count_overview(response.data)

    def test_can_filter_structure_counter_with_taxonomy_db(self):
        url = "/api/taxonomy/structure/pdb"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self.assertIsInstance(response.data, dict)
        self.assertIn(
            "uniprot",
            response.data["taxa"],
            "'uniprot' should be one of the keys in the response",
        )
        self.assertIn(
            "structures",
            response.data["taxa"]["uniprot"],
            "'structures' should be one of the keys in the response",
        )
        self.assertIn(
            "taxa",
            response.data["taxa"]["uniprot"],
            "'taxa' should be one of the keys in the response",
        )

    def test_can_get_a_list_from_the_taxonomy_list(self):
        url = "/api/taxonomy/uniprot/structure/pdb"
        self._check_list_url_with_and_without_subset(
            url,
            "structure",
            check_metadata_fn=lambda m: self._check_taxonomy_details(m, False),
            check_inner_subset_fn=self._check_structure_chain_details,
        )

    def test_can_get_a_list_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/structure/pdb",
            "/api/taxonomy/uniprot/1/structure/pdb",
            "/api/taxonomy/uniprot/2579/structure/pdb",
            "/api/taxonomy/uniprot/344612/structure/pdb",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "structure",
                check_metadata_fn=lambda m: self._check_taxonomy_details(m, False),
                check_inner_subset_fn=self._check_structure_chain_details,
            )

    def test_can_filter_taxonomy_counter_with_acc(self):
        urls = ["/api/taxonomy/structure/pdb/1JM7", "/api/taxonomy/structure/pdb/1JZ8"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_count_overview(response.data)

    def test_can_get_object_on_a_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/structure/pdb/1JM7",
            "/api/taxonomy/uniprot/structure/pdb/1JZ8",
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
                self._check_taxonomy_details(result["metadata"], False)
                for st in result["structures"]:
                    self._check_structure_chain_details(st)

    def test_can_get_an_object_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/structure/pdb/1t2v",
            "/api/taxonomy/uniprot/1/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/2579/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/344612/structure/pdb/1jm7",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("structures", response.data)
            for st in response.data["structures"]:
                self._check_structure_chain_details(st)


class TaxonomySetTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/taxonomy/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_taxonomy_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        url = "/api/taxonomy/uniprot/set"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "sets")
        for result in response.data["results"]:
            self._check_set_count_overview(result)

    def test_urls_that_return_taxonomy_with_set_count(self):
        urls = ["/api/taxonomy/uniprot/1001583/set", "/api/taxonomy/uniprot/1/set"]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn(
                "sets",
                response.data,
                "'sets' should be one of the keys in the response",
            )
            self._check_set_count_overview(response.data)

    def test_can_filter_taxonomy_counter_with_taxonomy_db(self):
        urls = [
            "/api/taxonomy/set/pfam",
            #            "/api/taxonomy/set/kegg",
            #            "/api/taxonomy/set/kegg/kegg01/node",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self.assertIn(
                "uniprot",
                response.data["taxa"],
                "'uniprot' should be one of the keys in the response",
            )
            self.assertIn(
                "taxa",
                response.data["taxa"]["uniprot"],
                "'taxa' should be one of the keys in the response",
            )
            self.assertIn(
                "sets",
                response.data["taxa"]["uniprot"],
                "'sets' should be one of the keys in the response",
            )

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/taxonomy/uniprot/set/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
            )

    def test_can_get_the_set_list_on_a__tax_object(self):
        urls = [
            "/api/taxonomy/uniprot/2579/set/pfam",
        ]
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "set",
                check_inner_subset_fn=self._check_set_from_searcher,
                check_metadata_fn=self._check_taxonomy_details,
            )

    def test_can_filter_counter_with_set_acc(self):
        urls = [
            "/api/taxonomy/set/pfam/Cl0001",
            #            "/api/taxonomy/set/kegg/kegg01",
            #            "/api/taxonomy/set/kegg/kegg01/node/KEGG01-1",
            #            "/api/taxonomy/set/kegg/kegg01/node/KEGG01-2",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_count_overview(response.data)

    def test_can_get_the_set_object_on_a_list(self):
        urls = [
            #            "/api/taxonomy/uniprot/set/kegg/kegg01",
            #            "/api/taxonomy/uniprot/set/kegg/kegg01/node/kegg01-1",
            "/api/taxonomy/uniprot/set/pfam/Cl0001"
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
            #            "/api/taxonomy/uniprot/2/set/kegg/kegg01",
            #            "/api/taxonomy/uniprot/40296/set/kegg/kegg01",
            #            "/api/taxonomy/uniprot/40296/set/kegg/kegg01/node/kegg01-1",
            "/api/taxonomy/uniprot/344612/set/pfam/Cl0001"
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, f"URL : [{url}]")
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)


class TaxonomyPerEntryTest(InterproRESTTestCase):
    def test_can_get_the_root_per_interpro(self):
        response = self.client.get("/api/taxonomy/uniprot/1?filter_by_entry=IPR001165")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_details(response.data["metadata"])
        self.assertEqual(response.data["metadata"]["counters"]["proteins"], 2)
        self.assertIsInstance(response.data["children"], dict)

    def test_can_browse_lineage_with_children_key(self):
        entries = ["IPR001165", "PF17180", "SM00950"]
        for entry in entries:
            tax = "1"
            lineage = ""
            payload_lineage = ""
            while tax != "":
                lineage += f" {tax}"
                path = f"/api/taxonomy/uniprot/{tax}?filter_by_entry={entry}"
                response = self.client.get(path)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                children = list(response.data["children"].keys())
                tax = children[0] if len(children) > 0 else ""
                payload_lineage = response.data["metadata"]["lineage"]
            self.assertEqual(payload_lineage.strip(), lineage.strip())

    def test_error_query(self):
        response = self.client.get("/api/taxonomy/uniprot/1?filter_by_entry=XXX")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TaxonomyPerEntryDBTest(InterproRESTTestCase):
    def test_can_get_the_root_per_interpro(self):
        response = self.client.get(
            "/api/taxonomy/uniprot/1?filter_by_entry_db=interpro"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_details(response.data["metadata"])
        self.assertEqual(response.data["metadata"]["counters"]["entries"], 7)
        self.assertIsInstance(response.data["children"], dict)

    def test_can_browse_lineage_with_children_key(self):
        dbs = ["interpro", "pfam", "profile", "smart"]
        for db in dbs:
            tax = "1"
            lineage = ""
            payload_lineage = ""
            while tax != "":
                lineage += f" {tax}"
                path = f"/api/taxonomy/uniprot/{tax}?filter_by_entry_db={db}"
                response = self.client.get(path)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                children = list(response.data["children"].keys())
                tax = children[0] if len(children) > 0 else ""
                payload_lineage = response.data["metadata"]["lineage"]
            self.assertEqual(payload_lineage.strip(), lineage.strip())

    def test_error_query(self):
        response = self.client.get("/api/taxonomy/uniprot/1?filter_by_entry_db=XXX")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
