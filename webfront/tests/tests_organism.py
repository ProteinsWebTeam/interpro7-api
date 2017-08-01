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
        # self.assertIn("proteome", response.data)

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
            "/api/organism/taxonomy/2/proteome/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_entry_count_overview(result)
    #
    # def test_urls_that_return_entry_with_organism_count(self):
    #     acc = "IPR003165"
    #     pfam = "PF02171"
    #     pfam_un = "PF17176"
    #     urls = [
    #         "/api/entry/interpro/"+acc+"/organism",
    #         "/api/entry/pfam/"+pfam+"/organism",
    #         "/api/entry/pfam/"+pfam_un+"/organism",
    #         "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/organism",
    #         "/api/entry/interpro/pfam/"+pfam+"/organism",
    #         "/api/entry/unintegrated/pfam/"+pfam_un+"/organism",
    #         ]
    #     for url in urls:
    #         response = self.client.get(url)
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self._check_entry_details(response.data["metadata"])
    #         self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
    #         self._check_organism_count_overview(response.data)
    #

class OrganismProteinTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_protein_count_overview(response.data)

class OrganismStructureTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_structure_count_overview(response.data)
