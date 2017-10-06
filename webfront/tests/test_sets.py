from rest_framework import status

from webfront.models import Set
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


class SetsFixturesTest(InterproRESTTestCase):

    def test_the_fixtures_are_loaded(self):
        sets = Set.objects.all()
        self.assertEqual(sets.count(), 5)
        names = [t.name for t in sets]
        self.assertIn("The Clan", names)
        self.assertNotIn("unicorn", names)

    def test_can_get_the_set_count(self):
        response = self.client.get("/api/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sets", response.data)
        self.assertIn("pfam", response.data["sets"])
        self.assertIn("kegg", response.data["sets"])
        self.assertNotIn("unicorn", response.data["sets"])
        self.assertNotIn("node", response.data["sets"])

    def test_can_read_set_list(self):
        response = self.client.get("/api/set/pfam")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 2)

        response = self.client.get("/api/set/kegg")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 1)

    def test_can_read_set_id(self):
        response = self.client.get("/api/set/pfam/CL0001")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_details(response.data["metadata"])

    def test_can_read_set_nodes(self):
        response = self.client.get("/api/set/kegg/KEGG01/node")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
        self.assertEqual(len(response.data["results"]), 2)

    def test_can_read_set_node_id(self):
        response = self.client.get("/api/set/kegg/KEGG01/node/KEGG01-1")
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
            "/api/entry/interpro/set",
            "/api/entry/pfam/set",
            "/api/entry/unintegrated/set",
            "/api/entry/interpro/pfam/set",
            "/api/entry/unintegrated/pfam/set",
            "/api/entry/interpro/"+acc+"/pfam/set",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_entry_with_set_count(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_un = "PF17176"
        urls = [
            "/api/entry/interpro/"+acc+"/set",
            "/api/entry/pfam/"+pfam+"/set",
            "/api/entry/pfam/"+pfam_un+"/set",
            "/api/entry/interpro/"+acc+"/pfam/"+pfam+"/set",
            "/api/entry/interpro/pfam/"+pfam+"/set",
            "/api/entry/unintegrated/pfam/"+pfam_un+"/set",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("sets", response.data, "'sets' should be one of the keys in the response")
            self._check_set_count_overview(response.data)


class ProteinSetTest(InterproRESTTestCase):
    def test_can_get_the_set_count(self):
        response = self.client.get("/api/protein/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        urls = [
            "/api/protein/reviewed/set/",
            "/api/protein/unreviewed/set/",
            "/api/protein/uniprot/set/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_protein_with_set_count(self):
        reviewed = "A1CUJ5"
        unreviewed = "P16582"
        urls = [
            "/api/protein/uniprot/"+reviewed+"/set",
            "/api/protein/uniprot/"+unreviewed+"/set",
            "/api/protein/reviewed/"+reviewed+"/set",
            "/api/protein/unreviewed/"+unreviewed+"/set",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_protein_details(response.data["metadata"])
            self.assertIn("sets", response.data, "'sets' should be one of the keys in the response")
            self._check_set_count_overview(response.data)


class StructureSetTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/structure/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        urls = [
            "/api/structure/pdb/set/",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_structure_with_set_count(self):
        urls = ["/api/structure/pdb/"+pdb+"/set/" for pdb in ["1JM7", "2BKM", "1T2V"]]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_structure_details(response.data["metadata"])
            self.assertIn("sets", response.data, "'sets' should be one of the keys in the response")
            self._check_set_count_overview(response.data)


class OrganismSetTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/organism/set")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_organism_count_overview(response.data)

    def test_can_get_the_set_count_on_a_list(self):
        urls = [
            "/api/organism/taxonomy/set",
            "/api/organism/proteome/set",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                self._check_set_count_overview(result)

    def test_urls_that_return_taxonomy_with_set_count(self):
        urls = [
            "/api/organism/taxonomy/40296/set",
            "/api/organism/taxonomy/2/set",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("sets", response.data, "'sets' should be one of the keys in the response")
            self._check_set_count_overview(response.data)

    def test_urls_that_return_proteome_with_set_count(self):
        urls = [
            "/api/organism/proteome/UP000012042/set",
            "/api/organism/taxonomy/proteome/UP000006701/set",
            "/api/organism/taxonomy/2/proteome/UP000030104/set",
            "/api/organism/taxonomy/40296/proteome/UP000030104/set",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("sets", response.data, "'sets' should be one of the keys in the response")
            self._check_set_count_overview(response.data)


class SetEntryTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/entry")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_entry_count_overview(response.data)

    def test_can_get_the_entry_count_on_a_list(self):
        urls = [
            "/api/set/pfam/entry",
            "/api/set/kegg/entry",
            "/api/set/kegg/KEGG01/node/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                self._check_entry_count_overview(result)

    def test_can_get_the_entry_count_on_a_set(self):
        urls = [
            "/api/set/pfam/CL0001/entry",
            "/api/set/kegg/KEGG01/entry",
            "/api/set/kegg/KEGG01/node/KEGG01-1/entry",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"])
            self.assertIn("entries", response.data, "'entries' should be one of the keys in the response")
            self._check_entry_count_overview(response.data)


class SetProteinTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/protein")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_protein_count_overview(response.data)

    def test_can_get_the_protein_count_on_a_list(self):
        urls = [
            "/api/set/pfam/protein",
            "/api/set/kegg/protein",
            "/api/set/kegg/KEGG01/node/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                self._check_protein_count_overview(result)

    def test_can_get_the_protein_count_on_a_set(self):
        urls = [
            "/api/set/pfam/CL0001/protein",
            "/api/set/kegg/KEGG01/protein",
            "/api/set/kegg/KEGG01/node/KEGG01-1/protein",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"])
            self.assertIn("proteins", response.data, "'proteins' should be one of the keys in the response")
            self._check_protein_count_overview(response.data)


class SetStructureTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/structure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_structure_count_overview(response.data)

    def test_can_get_the_structure_count_on_a_list(self):
        urls = [
            "/api/set/pfam/structure",
            "/api/set/kegg/structure",
            "/api/set/kegg/KEGG01/node/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                self._check_structure_count_overview(result)

    def test_can_get_the_structure_count_on_a_set(self):
        urls = [
            "/api/set/pfam/CL0001/structure",
            "/api/set/kegg/KEGG01/structure",
            "/api/set/kegg/KEGG01/node/KEGG01-1/structure",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"])
            self.assertIn("structures", response.data, "'structures' should be one of the keys in the response")
            self._check_structure_count_overview(response.data)


class SetOrganismTest(InterproRESTTestCase):
    def test_can_get_the_taxonomy_count(self):
        response = self.client.get("/api/set/organism")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_set_count_overview(response.data)
        self._check_organism_count_overview(response.data)

    def test_can_get_the_organism_count_on_a_list(self):
        urls = [
            "/api/set/pfam/organism",
            "/api/set/kegg/organism",
            "/api/set/kegg/KEGG01/node/organism",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                self._check_organism_count_overview(result)

    def test_can_get_the_organism_count_on_a_set(self):
        urls = [
            "/api/set/pfam/CL0001/organism",
            "/api/set/kegg/KEGG01/organism",
            "/api/set/kegg/KEGG01/node/KEGG01-1/organism",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"])
            self.assertIn("organisms", response.data, "'organisms' should be one of the keys in the response")
            self._check_organism_count_overview(response.data)
