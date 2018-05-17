from rest_framework import status

from webfront.models import Taxonomy, Proteome
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class TaxonomyFixturesTest(InterproRESTTestCase):
    def test_the_fixtures_are_loaded(self):
        taxa = Taxonomy.objects.all()
        self.assertEqual(taxa.count(), 6)
        names = [t.scientific_name for t in taxa]
        self.assertIn("ROOT", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/taxonomy")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("taxa", response.data)
        self.assertIn("uniprot", response.data["taxa"])
        # self.assertIn("proteome", response.data["organisms"])

    def test_can_read_taxonomy_list(self):
        response = self.client.get("/api/taxonomy/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 6)

    def test_can_read_taxonomy_id(self):
        response = self.client.get("/api/taxonomy/uniprot/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_taxonomy_details(response.data["metadata"])


class ProteomeFixturesTest(InterproRESTTestCase):
    def test_the_fixtures_are_loaded(self):
        proteomes = Proteome.objects.all()
        self.assertEqual(proteomes.count(), 3)
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
        self.assertEqual(len(response.data["results"]), 3)

    def test_can_read_proteome_id(self):
        response = self.client.get("/api/proteome/uniprot/UP000012042")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_proteome_details(response.data["metadata"])


class OrganismFixturesTest(InterproRESTTestCase):


    def test_can_read_taxonomy_with_proteome_list(self):
        response = self.client.get("/api/taxonomy/uniprot/proteome")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self._check_is_list_of_objects_with_key(response.data["results"], "proteomes")
        self.assertEqual(len(response.data["results"]), 3)

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
        self.assertIn("proteomes", response.data)
        self.assertEqual(len(response.data["proteomes"]), 1)


    def test_can_read_taxonomy_node_id_with_proteomes(self):
        response = self.client.get("/api/taxonomy/uniprot/2579/proteome/uniprot")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metadata", response.data)
        self.assertIn("proteomes", response.data)
        self.assertEqual(len(response.data["proteomes"]), 2)

    def test_can_read_proteome_id_including_tax_id(self):
        lineage = [1, 2, 40296]
        for taxon in lineage:
            response = self.client.get("/api/taxonomy/uniprot/{}/proteome/uniprot/UP000030104".format(taxon))
            self.assertEqual(response.status_code, status.HTTP_200_OK, "failed at "+str(taxon))
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
            "/api/entry/interpro/"+acc+"/pfam/taxonomy",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                self._check_taxonomy_count_overview(result)

    def test_urls_that_return_entry_with_taxonomy_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/entry/interpro/"+acc+"/taxonomy",
            "/api/entry/pfam/"+pfam+"/taxonomy",
            "/api/entry/pfam/"+pfam_un+"/taxonomy",
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/taxonomy",
            "/api/entry/interpro/pfam/"+pfam+"/taxonomy",
            "/api/entry/unintegrated/pfam/"+pfam_un+"/taxonomy",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("taxa", response.data, "'taxa' should be one of the keys in the response")
            self._check_taxonomy_count_overview(response.data)

    def test_can_filter_entry_counter_with_taxonomy_db(self):
        url = "/api/entry/taxonomy/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
        self.assertIn("taxa", response.data["entries"]["integrated"],
                      "'taxa' should be one of the keys in the response")
        if response.data["entries"]["unintegrated"] != 0:
            self.assertIn("taxa", response.data["entries"]["unintegrated"],
                          "'taxa' should be one of the keys in the response")

    def test_can_get_the_taxonomy_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/taxonomy/uniprot",
            "/api/entry/unintegrated/taxonomy/uniprot",
            "/api/entry/interpro/"+acc+"/pfam/taxonomy/uniprot",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "taxa")
            for result in response.data["results"]:
                for taxon in result["taxa"]:
                    self._check_taxonomy_from_searcher(taxon)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/entry/interpro/IPR003165/taxonomy/uniprot",
            "/api/entry/pfam/PF02171/taxonomy/uniprot",
            "/api/entry/unintegrated/pfam/PF17176/taxonomy/uniprot",
            "/api/entry/interpro/IPR003165/pfam/PF02171/taxonomy/uniprot",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("taxa", response.data)
            for org in response.data["taxa"]:
                self._check_taxonomy_from_searcher(org)

    def test_can_filter_entry_counter_with_taxonomy_acc(self):
        urls = [
            "/api/entry/taxonomy/uniprot/2579",
            "/api/entry/taxonomy/uniprot/40296",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_count_overview(response.data)

    def test_can_get_the_taxonomy_object_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/taxonomy/uniprot/2579",
            "/api/entry/unintegrated/taxonomy/uniprot/2579",
            "/api/entry/unintegrated/taxonomy/uniprot/344612",
            "/api/entry/interpro/"+acc+"/pfam/taxonomy/uniprot/344612",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("taxa", response.data)
            for org in response.data["taxa"]:
                self._check_taxonomy_from_searcher(org)


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
            "/api/entry/interpro/"+acc+"/pfam/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteomes")
            for result in response.data["results"]:
                self._check_proteome_count_overview(result)

    def test_urls_that_return_entry_with_proteome_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/entry/interpro/"+acc+"/proteome",
            "/api/entry/pfam/"+pfam+"/proteome",
            "/api/entry/pfam/"+pfam_un+"/proteome",
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/proteome",
            "/api/entry/interpro/pfam/"+pfam+"/proteome",
            "/api/entry/unintegrated/pfam/"+pfam_un+"/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("proteomes", response.data, "'proteomes' should be one of the keys in the response")
            self._check_proteome_count_overview(response.data)

    def test_can_filter_entry_counter_with_proteome_db(self):
        url = "/api/entry/proteome/uniprot"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
        self.assertIn("proteomes", response.data["entries"]["integrated"],
                      "'proteomes' should be one of the keys in the response")
        if response.data["entries"]["unintegrated"] != 0:
            self.assertIn("proteomes", response.data["entries"]["unintegrated"],
                          "'proteomes' should be one of the keys in the response")

    def test_can_get_the_proteome_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/pfam/proteome/uniprot",
            "/api/entry/interpro/pfam/proteome/uniprot",
            "/api/entry/unintegrated/pfam/proteome/uniprot",
            "/api/entry/interpro/"+acc+"/pfam/proteome/uniprot",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteomes")
            for result in response.data["results"]:
                for org in result["proteomes"]:
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("proteomes", response.data)
            for org in response.data["proteomes"]:
                self._check_proteome_from_searcher(org)

    def test_can_filter_entry_counter_with_proteome_acc(self):
        urls = [
            "/api/entry/proteome/uniprot/UP000006701",
            "/api/entry/proteome/uniprot/up000012042",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_count_overview(response.data)

    def test_can_get_the_proteome_object_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/pfam/proteome/uniprot/UP000006701",
            "/api/entry/interpro/pfam/proteome/uniprot/UP000006701",
            "/api/entry/interpro/"+acc+"/pfam/proteome/uniprot/UP000006701",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteomes")
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("proteomes", response.data)
            for org in response.data["proteomes"]:
                self._check_proteome_from_searcher(org)


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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_protein_details(response.data["metadata"])
            self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
            self._check_organism_count_overview(response.data)

    def test_can_filter_protein_counter_with_organism_db(self):
        urls = [
            "/api/protein/taxonomy/uniprot",
            "/api/protein/proteome/uniprot",
            "/api/protein/taxonomy/uniprot/proteome",
            "/api/protein/taxonomy/uniprot/2579/proteome",
            "/api/protein/taxonomy/uniprot/40296/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIn("proteins", response.data["proteins"]["uniprot"],
                          "'proteins' should be one of the keys in the response")
            self.assertIn("organisms", response.data["proteins"]["uniprot"],
                          "'organisms' should be one of the keys in the response")
            if "reviewed" in response.data["proteins"]:
                self.assertIn("proteins", response.data["proteins"]["reviewed"],
                              "'proteins' should be one of the keys in the response")
                self.assertIn("organisms", response.data["proteins"]["reviewed"],
                              "'organisms' should be one of the keys in the response")
            if "unreviewed" in response.data["proteins"]:
                self.assertIn("proteins", response.data["proteins"]["unreviewed"],
                              "'proteins' should be one of the keys in the response")
                self.assertIn("organisms", response.data["proteins"]["unreviewed"],
                              "'organisms' should be one of the keys in the response")

    def test_can_get_the_taxonomy_list_on_a_list(self):
        urls = [
            "/api/protein/reviewed/taxonomy/uniprot",
            "/api/protein/unreviewed/proteome/uniprot",
            "/api/protein/uniprot/taxonomy/uniprot/proteome",
            "/api/protein/reviewed/taxonomy/uniprot/2579/proteome",
            "/api/protein/reviewed/taxonomy/uniprot/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/taxonomy/uniprot",
            "/api/protein/uniprot/A0A0A2L2G2/proteome/uniprot",
            "/api/protein/unreviewed/P16582/taxonomy/uniprot/2/proteome",
            "/api/protein/unreviewed/P16582/taxonomy/uniprot",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/proteome",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/2579/proteome",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_protein_details(response.data["metadata"])
            self.assertIn("organisms", response.data)
            for org in response.data["organisms"]:
                self._check_organism_from_searcher(org)

    def test_can_filter_counter_with_organism_acc(self):
        urls = [
            "/api/protein/taxonomy/uniprot/2579",
            "/api/protein/taxonomy/uniprot/40296",
            "/api/protein/proteome/uniprot/UP000006701",
            "/api/protein/taxonomy/uniprot/proteome/UP000006701",
            "/api/protein/taxonomy/uniprot/2579/proteome/UP000006701",
            "/api/protein/taxonomy/uniprot/344612/proteome/UP000006701",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_protein_count_overview(response.data)

    def test_can_get_the_taxonomy_object_on_a_list(self):
        urls = [
            "/api/protein/reviewed/taxonomy/uniprot/2579",
            "/api/protein/unreviewed/proteome/uniprot/up000030104",
            "/api/protein/uniprot/taxonomy/uniprot/proteome/UP000006701",
            "/api/protein/reviewed/taxonomy/uniprot/2579/proteome/UP000006701",
            "/api/protein/reviewed/taxonomy/uniprot/344612/proteome/UP000006701",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_object_on_an_object(self):
        urls = [
            "/api/protein/uniprot/A0A0A2L2G2/taxonomy/uniprot/40296",
            "/api/protein/uniprot/A0A0A2L2G2/proteome/uniprot/up000030104",
            "/api/protein/unreviewed/P16582/taxonomy/uniprot/2/proteome/up000030104",
            "/api/protein/unreviewed/P16582/taxonomy/uniprot/40296",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/proteome/up000006701",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/2579/proteome/up000006701",
            "/api/protein/reviewed/A1CUJ5/taxonomy/uniprot/344612/proteome/up000006701",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                self._check_organism_count_overview(result)

    def test_urls_that_return_structure_with_organism_count(self):
        urls = ["/api/structure/pdb/"+pdb+"/organism/" for pdb in ["1JM7", "2BKM", "1T2V"]]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_structure_details(response.data["metadata"])
            self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
            self._check_organism_count_overview(response.data)

    def test_can_filter_structure_counter_with_organism_db(self):
        urls = [
            "/api/structure/taxonomy/uniprot",
            "/api/structure/proteome/uniprot",
            "/api/structure/taxonomy/uniprot/proteome",
            "/api/structure/taxonomy/uniprot/2579/proteome",
            "/api/structure/taxonomy/uniprot/40296/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIn("structures", response.data["structures"]["pdb"],
                          "'structures' should be one of the keys in the response")
            self.assertIn("organisms", response.data["structures"]["pdb"],
                          "'organisms' should be one of the keys in the response")

    def test_can_get_the_taxonomy_list_on_a_list(self):
        urls = [
            "/api/structure/pdb/taxonomy/uniprot",
            "/api/structure/pdb/proteome/uniprot",
            "/api/structure/pdb/taxonomy/uniprot/proteome",
            "/api/structure/pdb/taxonomy/uniprot/2579/proteome",
            "/api/structure/pdb/taxonomy/uniprot/344612/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/taxonomy/uniprot",
            "/api/structure/pdb/1T2V/proteome/uniprot",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot/2/proteome",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot",
            "/api/structure/pdb/1JM7/taxonomy/uniprot/proteome",
            "/api/structure/pdb/1JM7/taxonomy/uniprot/2579/proteome",
            "/api/structure/pdb/1JM7/taxonomy/uniprot/344612/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_structure_details(response.data["metadata"])
            self.assertIn("organisms", response.data)
            for org in response.data["organisms"]:
                self._check_organism_from_searcher(org)

    def test_can_filter_counter_with_organism_acc(self):
        urls = [
            "/api/structure/taxonomy/uniprot/2579",
            "/api/structure/taxonomy/uniprot/40296",
            "/api/structure/proteome/uniprot/UP000006701",
            "/api/structure/taxonomy/uniprot/proteome/UP000006701",
            "/api/structure/taxonomy/uniprot/2579/proteome/UP000006701",
            "/api/structure/taxonomy/uniprot/344612/proteome/UP000006701",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_structure_count_overview(response.data)

    def test_can_get_the_taxonomy_object_on_a_list(self):
        urls = [
            "/api/structure/pdb/taxonomy/uniprot/2579",
            "/api/structure/pdb/proteome/uniprot/up000030104",
            "/api/structure/pdb/taxonomy/uniprot/proteome/UP000006701",
            "/api/structure/pdb/taxonomy/uniprot/2579/proteome/UP000006701",
            "/api/structure/pdb/taxonomy/uniprot/344612/proteome/UP000006701",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for org in result["organisms"]:
                    self._check_organism_from_searcher(org)

    def test_can_get_the_taxonomy_object_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/taxonomy/uniprot/40296",
            "/api/structure/pdb/1T2V/proteome/uniprot/up000030104",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot/2/proteome/up000030104",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot/1",
            "/api/structure/pdb/1JZ8/taxonomy/uniprot/40296",
            "/api/structure/pdb/1JM7/taxonomy/uniprot/proteome/up000006701",
            "/api/structure/pdb/1JM7/taxonomy/uniprot/2579/proteome/up000006701",
            "/api/structure/pdb/1JM7/taxonomy/uniprot/344612/proteome/up000006701",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
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
            "/api/taxonomy/uniprot/entry",
            "/api/proteome/uniprot/entry",
            "/api/taxonomy/uniprot/proteome/entry",
            "/api/taxonomy/uniprot/2/proteome/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_entry_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/taxonomy/uniprot/2579/proteome/entry")
        response2 = self.client.get("/api/taxonomy/uniprot/1001583/proteome/entry")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response1.data["results"]), len(response2.data["results"]))

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/taxonomy/uniprot/40296/entry",
            "/api/taxonomy/uniprot/2/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self._check_entry_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/entry",
            "/api/taxonomy/uniprot/proteome/UP000006701/entry",
            "/api/taxonomy/uniprot/2/proteome/UP000030104/entry",
            "/api/taxonomy/uniprot/40296/proteome/UP000030104/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self._check_entry_count_overview(response.data)

    def test_can_filter_organismcounter_with_entry_db(self):
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            self.assertIn("taxonomy", response.data["organisms"],
                          "'taxonomy' should be one of the keys in the response")
            self.assertIn("proteome", response.data["organisms"],
                          "'proteome' should be one of the keys in the response")
            self.assertIn("entries", response.data["organisms"]["taxonomy"],
                          "'entries' should be one of the keys in the response")
            self.assertIn("entries", response.data["organisms"]["proteome"],
                          "'entries' should be one of the keys in the response")

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/entry/interpro",
            "/api/proteome/uniprot/entry/pfam",
            "/api/taxonomy/uniprot/proteome/entry/unintegrated",
            "/api/taxonomy/uniprot/proteome/entry/interpro/pfam",
            "/api/taxonomy/uniprot/2579/proteome/entry/unintegrated/pfam",
            "/api/taxonomy/uniprot/344612/proteome/entry/unintegrated/pfam",
            "/api/proteome/uniprot/entry/interpro/IPR003165/pfam",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["entries"]:
                    self._check_entry_from_searcher(st)

    def test_can_get_a_list_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/entry/interpro",
            "/api/proteome/uniprot/UP000006701/entry/pfam",
            "/api/taxonomy/uniprot/proteome/UP000006701/entry/unintegrated",
            "/api/taxonomy/uniprot/1/proteome/UP000006701/entry/interpro/pfam",
            "/api/taxonomy/uniprot/2579/proteome/UP000006701/entry/unintegrated/pfam",
            "/api/taxonomy/uniprot/344612/proteome/UP000006701/entry/unintegrated/pfam",
            "/api/proteome/uniprot/UP000006701/entry/interpro/IPR003165/smart",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            if "proteome" in url:
                self._check_proteome_details(response.data["metadata"], False)
            else:
                self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("entries", response.data)
            for st in response.data["entries"]:
                self._check_entry_from_searcher(st)

    def test_can_filter_organism_counter_with_acc(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/organism/entry/interpro/"+acc,
            "/api/organism/entry/pfam/"+pfam,
            "/api/organism/entry/pfam/"+pfam_un,
            "/api/organism/entry/interpro/"+acc+"/pfam/"+pfam,
            "/api/organism/entry/interpro/pfam/"+pfam,
            "/api/organism/entry/unintegrated/pfam/"+pfam_un,
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_organism_count_overview(response.data)

    def test_can_get_object_on_a_taxonomy_list(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/taxonomy/uniprot/entry/interpro/"+acc,
            "/api/proteome/uniprot/entry/pfam/"+pfam,
            "/api/taxonomy/uniprot/entry/unintegrated/pfam/"+pfam_un,
            "/api/taxonomy/uniprot/proteome/entry/unintegrated/pfam/"+pfam_un,
            "/api/taxonomy/uniprot/proteome/entry/interpro/pfam/"+pfam,
            "/api/taxonomy/uniprot/2579/proteome/entry/unintegrated/pfam/"+pfam_un,
            "/api/taxonomy/uniprot/344612/proteome/entry/unintegrated/pfam/"+pfam_un,
            "/api/proteome/uniprot/entry/interpro/IPR003165/pfam/"+pfam,
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["entries"]:
                    self._check_entry_from_searcher(st)

    def test_can_get_an_object_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/entry/interpro/ipr003165",
            "/api/proteome/uniprot/UP000006701/entry/pfam/pf02171",
            "/api/taxonomy/uniprot/proteome/UP000006701/entry/unintegrated/pfam/pf17176",
            "/api/taxonomy/uniprot/1/proteome/UP000006701/entry/interpro/pfam/pf02171",
            "/api/taxonomy/uniprot/2579/proteome/UP000006701/entry/unintegrated/pfam/pf17176",
            "/api/taxonomy/uniprot/344612/proteome/UP000006701/entry/unintegrated/pfam/pf17176",
            "/api/proteome/uniprot/UP000006701/entry/interpro/IPR003165/smart/sm00950",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            if "proteome" in url:
                self._check_proteome_details(response.data["metadata"], False)
            else:
                self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("entries", response.data)
            for st in response.data["entries"]:
                self._check_entry_from_searcher(st)


class OrganismProteinTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        urls = [
            "/api/taxonomy/uniprot/protein",
            "/api/proteome/uniprot/protein",
            "/api/taxonomy/uniprot/proteome/protein",
            "/api/taxonomy/uniprot/2/proteome/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                self._check_protein_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/taxonomy/uniprot/2579/proteome/protein")
        response2 = self.client.get("/api/taxonomy/uniprot/1001583/proteome/protein")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response1.data["results"]), len(response2.data["results"]))

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/taxonomy/uniprot/40296/protein",
            "/api/taxonomy/uniprot/2/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self._check_protein_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/protein",
            "/api/taxonomy/uniprot/proteome/UP000006701/protein",
            "/api/taxonomy/uniprot/2/proteome/UP000030104/protein",
            "/api/taxonomy/uniprot/40296/proteome/UP000030104/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
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
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            self.assertIn("taxonomy", response.data["organisms"],
                          "'taxonomy' should be one of the keys in the response")
            self.assertIn("proteome", response.data["organisms"],
                          "'proteome' should be one of the keys in the response")
            self.assertIn("proteins", response.data["organisms"]["taxonomy"],
                          "'entries' should be one of the keys in the response")
            self.assertIn("proteins", response.data["organisms"]["proteome"],
                          "'entries' should be one of the keys in the response")

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/protein/uniprot",
            "/api/proteome/uniprot/protein/uniprot",
            "/api/taxonomy/uniprot/proteome/protein/unreviewed",
            "/api/taxonomy/uniprot/2579/proteome/protein/reviewed",
            "/api/taxonomy/uniprot/344612/proteome/protein/reviewed",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["proteins"]:
                    self._check_match(st, include_coordinates=False)

    def test_can_get_a_list_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/protein/uniprot",
            "/api/proteome/uniprot/UP000006701/protein/uniprot",
            "/api/proteome/uniprot/UP000030104/protein/unreviewed",
            "/api/taxonomy/uniprot/proteome/UP000030104/protein/unreviewed",
            "/api/taxonomy/uniprot/1/proteome/UP000006701/protein/reviewed",
            "/api/taxonomy/uniprot/2579/proteome/UP000006701/protein/reviewed",
            "/api/taxonomy/uniprot/344612/proteome/UP000006701/protein/reviewed",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            if "proteome" in url:
                self._check_proteome_details(response.data["metadata"], False)
            else:
                self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("proteins", response.data)
            for st in response.data["proteins"]:
                self._check_match(st, include_coordinates=False)

    def test_can_filter_organism_counter_with_acc(self):
        urls = [
            "/api/organism/protein/uniprot/M5ADK6",
            "/api/organism/protein/unreviewed/A0A0A2L2G2",
            "/api/organism/protein/reviewed/M5ADK6",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_organism_count_overview(response.data)

    def test_can_get_object_on_a_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/protein/uniprot/P16582",
            "/api/proteome/uniprot/protein/uniprot/P16582",
            "/api/taxonomy/uniprot/protein/unreviewed/A0A0A2L2G2",
            "/api/proteome/uniprot/protein/unreviewed/A0A0A2L2G2",
            "/api/taxonomy/uniprot/proteome/protein/unreviewed/A0A0A2L2G2",
            "/api/taxonomy/uniprot/2579/proteome/protein/reviewed/M5ADK6",
            "/api/taxonomy/uniprot/344612/proteome/protein/reviewed/a1cuj5",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["proteins"]:
                    self._check_match(st, include_coordinates=False)

    def test_can_get_an_object_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/protein/uniprot/p16582",
            "/api/proteome/uniprot/UP000006701/protein/uniprot/a1cuj5",
            "/api/proteome/uniprot/UP000030104/protein/unreviewed/A0A0A2L2G2",
            "/api/taxonomy/uniprot/proteome/UP000030104/protein/unreviewed/A0A0A2L2G2",
            "/api/taxonomy/uniprot/1/proteome/UP000006701/protein/reviewed/a1cuj5",
            "/api/taxonomy/uniprot/2579/proteome/UP000006701/protein/reviewed/a1cuj5",
            "/api/taxonomy/uniprot/344612/proteome/UP000006701/protein/reviewed/a1cuj5",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            if "proteome" in url:
                self._check_proteome_details(response.data["metadata"], False)
            else:
                self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("proteins", response.data)
            for st in response.data["proteins"]:
                self._check_match(st, include_coordinates=False)


class OrganismStructureTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_organism_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        urls = [
            "/api/taxonomy/uniprot/structure",
            "/api/proteome/uniprot/structure",
            "/api/taxonomy/uniprot/proteome/structure",
            "/api/taxonomy/uniprot/2/proteome/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                self._check_structure_count_overview(result)

    def test_a_more_inclusive_taxon_has_more_items(self):
        response1 = self.client.get("/api/taxonomy/uniprot/2579/proteome/structure")
        response2 = self.client.get("/api/taxonomy/uniprot/1001583/proteome/structure")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response1.data["results"]), len(response2.data["results"]))

    def test_urls_that_return_taxonomy_with_entry_count(self):
        urls = [
            "/api/taxonomy/uniprot/40296/structure",
            "/api/taxonomy/uniprot/2/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_structure_count_overview(response.data)

    def test_urls_that_return_proteome_with_entry_count(self):
        urls = [
            "/api/proteome/uniprot/UP000012042/structure",
            "/api/taxonomy/uniprot/proteome/UP000006701/structure",
            "/api/taxonomy/uniprot/2/proteome/UP000030104/structure",
            "/api/taxonomy/uniprot/40296/proteome/UP000030104/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_structure_count_overview(response.data)

    def test_can_filter_structure_counter_with_organism_db(self):
        urls = [
            "/api/organism/structure/pdb",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            self.assertIn("taxonomy", response.data["organisms"],
                          "'taxonomy' should be one of the keys in the response")
            self.assertIn("proteome", response.data["organisms"],
                          "'proteome' should be one of the keys in the response")
            self.assertIn("structures", response.data["organisms"]["taxonomy"],
                          "'structures' should be one of the keys in the response")
            self.assertIn("structures", response.data["organisms"]["proteome"],
                          "'structures' should be one of the keys in the response")

    def test_can_get_a_list_from_the_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/structure/pdb",
            "/api/proteome/uniprot/structure/pdb",
            "/api/taxonomy/uniprot/proteome/structure/pdb",
            "/api/taxonomy/uniprot/2579/proteome/structure/pdb",
            "/api/taxonomy/uniprot/344612/proteome/structure/pdb",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["structures"]:
                    self._check_structure_chain_details(st)

    def test_can_get_a_list_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/structure/pdb",
            "/api/proteome/uniprot/UP000006701/structure/pdb",
            "/api/proteome/uniprot/UP000030104/structure/pdb",
            "/api/taxonomy/uniprot/proteome/UP000030104/structure/pdb",
            "/api/taxonomy/uniprot/1/proteome/UP000006701/structure/pdb",
            "/api/taxonomy/uniprot/2579/proteome/UP000006701/structure/pdb",
            "/api/taxonomy/uniprot/344612/proteome/UP000006701/structure/pdb",
            "/api/taxonomy/uniprot/1/structure/pdb",
            "/api/taxonomy/uniprot/2579/structure/pdb",
            "/api/taxonomy/uniprot/344612/structure/pdb",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            if "proteome" in url:
                self._check_proteome_details(response.data["metadata"], False)
            else:
                self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("structures", response.data)
            for st in response.data["structures"]:
                self._check_structure_chain_details(st)

    def test_can_filter_organism_counter_with_acc(self):
        urls = [
            "/api/organism/structure/pdb/1JM7",
            "/api/organism/structure/pdb/1JZ8",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_organism_count_overview(response.data)

    def test_can_get_object_on_a_taxonomy_list(self):
        urls = [
            "/api/taxonomy/uniprot/structure/pdb/1JM7",
            "/api/proteome/uniprot/structure/pdb/1JZ8",
            "/api/taxonomy/uniprot/proteome/structure/pdb/1JZ8",
            "/api/taxonomy/uniprot/2579/proteome/structure/pdb/1JM7",
            "/api/taxonomy/uniprot/344612/proteome/structure/pdb/1JM7",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                if "proteome" in url:
                    self._check_proteome_details(result["metadata"], False)
                else:
                    self._check_taxonomy_details(result["metadata"], False)
                for st in result["structures"]:
                    self._check_structure_chain_details(st)

    def test_can_get_an_object_from_the_taxonomy_object(self):
        urls = [
            "/api/taxonomy/uniprot/40296/structure/pdb/1t2v",
            "/api/proteome/uniprot/UP000006701/structure/pdb/1jm7",
            "/api/proteome/uniprot/UP000030104/structure/pdb/1t2v",
            "/api/taxonomy/uniprot/proteome/UP000030104/structure/pdb/1t2v",
            "/api/taxonomy/uniprot/1/proteome/UP000006701/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/2579/proteome/UP000006701/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/344612/proteome/UP000006701/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/1/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/2579/structure/pdb/1jm7",
            "/api/taxonomy/uniprot/344612/structure/pdb/1jm7",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            if "proteome" in url:
                self._check_proteome_details(response.data["metadata"], False)
            else:
                self._check_taxonomy_details(response.data["metadata"], False)
            self.assertIn("structures", response.data)
            for st in response.data["structures"]:
                self._check_structure_chain_details(st)
