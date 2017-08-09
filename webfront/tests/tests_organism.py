from rest_framework import status

from webfront.models import Taxonomy
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class OrganismFixturesTest(InterproRESTTestCase):

    def test_the_fixtures_are_loaded(self):
        taxa = Taxonomy.objects.all()
        self.assertEqual(taxa.count(), 6)
        names = [t.scientific_name for t in taxa]
        self.assertIn("ROOT", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("organisms", response.data)
        self.assertIn("taxa", response.data["organisms"])
        self.assertIn("proteomes", response.data["organisms"])

    def test_can_read_taxonomy_list(self):
        response = self.client.get("/api/organism/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 6)

    def test_can_read_taxonomy_id(self):
        response = self.client.get("/api/organism/taxonomy/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_details(response.data["metadata"])

    def test_can_read_proteome_list(self):
        response = self.client.get("/api/organism/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 3)

    def test_can_read_proteome_id(self):
        response = self.client.get("/api/organism/proteome/UP000012042")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_details(response.data["metadata"])

    def test_can_read_taxonomy_with_proteome_list(self):
        response = self.client.get("/api/organism/taxonomy/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 3)

    def test_can_read_taxonomy_leaf_id_with_proteomes(self):
        response = self.client.get("/api/organism/taxonomy/40296/proteome")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_can_read_taxonomy_node_id_with_proteomes(self):
        response = self.client.get("/api/organism/taxonomy/2579/proteome")
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_proteome_id_including_tax_id(self):
        lineage = [1, 2, 40296]
        for taxon in lineage:
            response = self.client.get("/api/organism/taxonomy/{}/proteome/UP000030104".format(taxon))
            self.assertEqual(response.status_code, status.HTTP_200_OK, "failed at "+str(taxon))
            self._check_proteome_details(response.data["metadata"])


class EntryOrganismTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/entry/organism")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/organism/",
            "/api/entry/pfam/organism/",
            "/api/entry/unintegrated/organism/",
            "/api/entry/interpro/pfam/organism/",
            "/api/entry/unintegrated/pfam/organism/",
            "/api/entry/interpro/"+acc+"/pfam/organism",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                self._check_organism_count_overview(result)

    def test_urls_that_return_entry_with_organism_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/entry/interpro/"+acc+"/organism",
            "/api/entry/pfam/"+pfam+"/organism",
            "/api/entry/pfam/"+pfam_un+"/organism",
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/organism",
            "/api/entry/interpro/pfam/"+pfam+"/organism",
            "/api/entry/unintegrated/pfam/"+pfam_un+"/organism",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_details(response.data["metadata"])
            self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
            self._check_organism_count_overview(response.data)

    def test_can_filter_entry_counter_with_organism_db(self):
        urls = [
            "/api/entry/organism/taxonomy",
            "/api/entry/organism/proteome",
            "/api/entry/organism/taxonomy/proteome",
            "/api/entry/organism/taxonomy/2579/proteome",
            "/api/entry/organism/taxonomy/40296/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("organisms", response.data["entries"]["integrated"],
                          "'organisms' should be one of the keys in the response")
            if response.data["entries"]["unintegrated"] != 0:
                self.assertIn("organisms", response.data["entries"]["unintegrated"],
                              "'organisms' should be one of the keys in the response")

    def test_can_get_the_taxonomy_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/organism/taxonomy",
            "/api/entry/pfam/organism/proteome",
            "/api/entry/unintegrated/organism/taxonomy",
            "/api/entry/interpro/pfam/organism/taxonomy/proteome",
            "/api/entry/unintegrated/pfam/organism/taxonomy/2579/proteome",
            "/api/entry/interpro/"+acc+"/pfam/organism/taxonomy/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/entry/interpro/IPR003165/organism/taxonomy",
            "/api/entry/pfam/PF02171/organism/proteome",
            "/api/entry/interpro/IPR003165/organism/taxonomy/2579/proteome",
            "/api/entry/unintegrated/pfam/PF17176/organism/taxonomy",
            "/api/entry/interpro/pfam/PF02171/organism/taxonomy/proteome",
            "/api/entry/interpro/IPR003165/pfam/PF02171/organism/taxonomy/2579/proteome",
            "/api/entry/interpro/IPR003165/pfam/PF02171/organism/taxonomy/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_entry_details(response.data["metadata"])
            self.assertIn("organisms", response.data)
            for org in response.data["organisms"]:
                self._check_organism_from_searcher(org)


class ProteinOrganismTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/protein/organism")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        urls = [
            "/api/protein/reviewed/organism/",
            "/api/protein/unreviewed/organism/",
            "/api/protein/uniprot/organism/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                self._check_organism_count_overview(result)

    def test_urls_that_return_protein_with_organism_count(self):
        reviewed = "A1CUJ5"
        unreviewed = "P16582"
        urls = [
            "/api/protein/uniprot/"+reviewed+"/organism/",
            "/api/protein/uniprot/"+unreviewed+"/organism/",
            "/api/protein/reviewed/"+reviewed+"/organism/",
            "/api/protein/unreviewed/"+unreviewed+"/organism/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_protein_details(response.data["metadata"])
            self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
            self._check_organism_count_overview(response.data)

    def test_can_filter_protein_counter_with_organism_db(self):
        urls = [
            "/api/protein/organism/taxonomy",
            "/api/protein/organism/proteome",
            "/api/protein/organism/taxonomy/proteome",
            "/api/protein/organism/taxonomy/2579/proteome",
            "/api/protein/organism/taxonomy/40296/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("proteins", response.data["proteins"]["uniprot"],
                          "'proteins' should be one of the keys in the response")
            if "reviewed" in response.data["proteins"]:
                self.assertIn("proteins", response.data["proteins"]["reviewed"],
                              "'proteins' should be one of the keys in the response")
            if "unreviewed" in response.data["proteins"]:
                self.assertIn("proteins", response.data["proteins"]["unreviewed"],
                              "'proteins' should be one of the keys in the response")

    def test_can_get_the_taxonomy_list_on_a_list(self):
        urls = [
            "/api/protein/reviewed/organism/taxonomy",
            "/api/protein/unreviewed/organism/proteome",
            "/api/protein/uniprot/organism/taxonomy/proteome",
            "/api/protein/reviewed/organism/taxonomy/2579/proteome",
            "/api/protein/reviewed/organism/taxonomy/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/organism/taxonomy",
            "/api/protein/uniprot/A0A0A2L2G2/organism/proteome",
            "/api/protein/unreviewed/P16582/organism/taxonomy/2/proteome",
            "/api/protein/unreviewed/P16582/organism/taxonomy",
            "/api/protein/reviewed/A1CUJ5/organism/taxonomy/proteome",
            "/api/protein/reviewed/A1CUJ5/organism/taxonomy/2579/proteome",
            "/api/protein/reviewed/A1CUJ5/organism/taxonomy/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_protein_details(response.data["metadata"])
            self.assertIn("organisms", response.data)
            for org in response.data["organisms"]:
                self._check_organism_from_searcher(org)


class StructureOrganismTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/structure/organism")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_taxonomy_count_on_a_list(self):
        urls = [
            "/api/structure/pdb/organism/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                self._check_organism_count_overview(result)

    def test_urls_that_return_structure_with_organism_count(self):
        urls = ["/api/structure/pdb/"+pdb+"/organism/" for pdb in ["1JM7", "2BKM", "1T2V"]]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_structure_details(response.data["metadata"])
            self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
            self._check_organism_count_overview(response.data)

    def test_can_filter_structure_counter_with_organism_db(self):
        urls = [
            "/api/structure/organism/taxonomy",
            "/api/structure/organism/proteome",
            "/api/structure/organism/taxonomy/proteome",
            "/api/structure/organism/taxonomy/2579/proteome",
            "/api/structure/organism/taxonomy/40296/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("structures", response.data["structures"]["pdb"],
                          "'structures' should be one of the keys in the response")

    def test_can_get_the_taxonomy_list_on_a_list(self):
        urls = [
            "/api/structure/pdb/organism/taxonomy",
            "/api/structure/pdb/organism/proteome",
            "/api/structure/pdb/organism/taxonomy/proteome",
            "/api/structure/pdb/organism/taxonomy/2579/proteome",
            "/api/structure/pdb/organism/taxonomy/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/organism/taxonomy",
            "/api/structure/pdb/1T2V/organism/proteome",
            "/api/structure/pdb/1JZ8/organism/taxonomy/2/proteome",
            "/api/structure/pdb/1JZ8/organism/taxonomy",
            "/api/structure/pdb/1JM7/organism/taxonomy/proteome",
            "/api/structure/pdb/1JM7/organism/taxonomy/2579/proteome",
            "/api/structure/pdb/1JM7/organism/taxonomy/344612/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_structure_details(response.data["metadata"])
            self.assertIn("organisms", response.data)
            for org in response.data["organisms"]:
                self._check_organism_from_searcher(org)


class OrganismEntryTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_entry_count_on_a_list(self):
        urls = [
            "/api/organism/taxonomy/entry",
            "/api/organism/proteome/entry",
            "/api/organism/taxonomy/proteome/entry",
            "/api/organism/taxonomy/2/proteome/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_entry_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/organism/taxonomy/2579/proteome/entry")
        response2 = self.client.get("/api/organism/taxonomy/1001583/proteome/entry")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response1.data["results"]), len(response2.data["results"]))

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/organism/taxonomy/40296/entry",
            "/api/organism/taxonomy/2/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self._check_entry_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/organism/proteome/UP000012042/entry",
            "/api/organism/taxonomy/proteome/UP000006701/entry",
            "/api/organism/taxonomy/2/proteome/UP000030104/entry",
            "/api/organism/taxonomy/40296/proteome/UP000030104/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self._check_entry_count_overview(response.data)

    def test_can_filter_entry_counter_with_organism_db(self):
        acc = "IPR003165"
        urls = [
            "/api/organism/entry/interpro",
            "/api/organism/entry/pfam",
            "/api/organism/entry/unintegrated",
            "/api/organism/entry/unintegrated/pfam",
            "/api/organism/entry/interpro/pfam",
            "/api/organism/entry/interpro/"+acc+"/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)
            self.assertIn("entries", response.data["organisms"],
                          "'entries' should be one of the keys in the response")
            self.assertIn("taxa", response.data["organisms"],
                          "'taxa' should be one of the keys in the response")
            self.assertIn("proteomes", response.data["organisms"],
                          "'entproteomesries' should be one of the keys in the response")

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/organism/taxonomy/entry/interpro",
            "/api/organism/proteome/entry/pfam",
            "/api/organism/taxonomy/proteome/entry/unintegrated",
            "/api/organism/taxonomy/proteome/entry/interpro/pfam",
            "/api/organism/taxonomy/2579/proteome/entry/unintegrated/pfam",
            "/api/organism/taxonomy/344612/proteome/entry/unintegrated/pfam",
            "/api/organism/proteome/entry/interpro/IPR003165/pfam",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["entries"]:
                    self._check_entry_from_searcher(st)

class OrganismProteinTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        urls = [
            "/api/organism/taxonomy/protein",
            "/api/organism/proteome/protein",
            "/api/organism/taxonomy/proteome/protein",
            "/api/organism/taxonomy/2/proteome/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                self._check_protein_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/organism/taxonomy/2579/proteome/protein")
        response2 = self.client.get("/api/organism/taxonomy/1001583/proteome/protein")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response1.data["results"]), len(response2.data["results"]))

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/organism/taxonomy/40296/protein",
            "/api/organism/taxonomy/2/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self._check_protein_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/organism/proteome/UP000012042/protein",
            "/api/organism/taxonomy/proteome/UP000006701/protein",
            "/api/organism/taxonomy/2/proteome/UP000030104/protein",
            "/api/organism/taxonomy/40296/proteome/UP000030104/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self._check_protein_count_overview(response.data)

    def test_can_filter_protein_counter_with_organism_db(self):
        urls = [
            "/api/organism/protein/uniprot",
            "/api/organism/protein/reviewed",
            "/api/organism/protein/unreviewed",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)
            self.assertIn("proteins", response.data["organisms"],
                          "'entries' should be one of the keys in the response")
            self.assertIn("taxa", response.data["organisms"],
                          "'taxa' should be one of the keys in the response")
            self.assertIn("proteomes", response.data["organisms"],
                          "'entproteomesries' should be one of the keys in the response")

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/organism/taxonomy/protein/uniprot",
            "/api/organism/proteome/protein/uniprot",
            "/api/organism/taxonomy/proteome/protein/unreviewed",
            "/api/organism/taxonomy/2579/proteome/protein/reviewed",
            "/api/organism/taxonomy/344612/proteome/protein/reviewed",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["proteins"]:
                    self._check_match(st)

class OrganismStructureTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        urls = [
            "/api/organism/taxonomy/structure",
            "/api/organism/proteome/structure",
            "/api/organism/taxonomy/proteome/structure",
            "/api/organism/taxonomy/2/proteome/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                self._check_structure_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/organism/taxonomy/2579/proteome/structure")
        response2 = self.client.get("/api/organism/taxonomy/1001583/proteome/structure")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response1.data["results"]), len(response2.data["results"]))

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/organism/taxonomy/40296/structure",
            "/api/organism/taxonomy/2/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_structure_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/organism/proteome/UP000012042/structure",
            "/api/organism/taxonomy/proteome/UP000006701/structure",
            "/api/organism/taxonomy/2/proteome/UP000030104/structure",
            "/api/organism/taxonomy/40296/proteome/UP000030104/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_structure_count_overview(response.data)

    def test_can_filter_structure_counter_with_organism_db(self):
        urls = [
            "/api/organism/structure/pdb",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)
            self.assertIn("structures", response.data["organisms"],
                          "'structures' should be one of the keys in the response")
            self.assertIn("taxa", response.data["organisms"],
                          "'taxa' should be one of the keys in the response")
            self.assertIn("proteomes", response.data["organisms"],
                          "'entproteomesries' should be one of the keys in the response")

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/organism/taxonomy/structure/pdb",
            "/api/organism/proteome/structure/pdb",
            "/api/organism/taxonomy/proteome/structure/pdb",
            "/api/organism/taxonomy/2579/proteome/structure/pdb",
            "/api/organism/taxonomy/344612/proteome/structure/pdb",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["structures"]:
                    self._check_structure_chain_details(st)
