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

    def test_can_filter_entry_counter_with_set_db(self):
        urls = [
            "/api/entry/set/pfam",
            "/api/entry/set/kegg",
            "/api/entry/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIn("sets", response.data["entries"]["integrated"],
                          "'sets' should be one of the keys in the response")
            if response.data["entries"]["unintegrated"] != 0:
                self.assertIn("sets", response.data["entries"]["unintegrated"],
                              "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/entry/interpro/set/kegg",
            "/api/entry/pfam/set/pfam",
            "/api/entry/unintegrated/set/pfam",
            "/api/entry/interpro/pfam/set/kegg/kegg01/node",
            "/api/entry/interpro/"+acc+"/pfam/set/pfam",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for s in result["sets"]:
                    self._check_set_from_searcher(s)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/entry/interpro/IPR003165/set/kegg",
            "/api/entry/pfam/PF02171/set/pfam",
            "/api/entry/interpro/IPR003165/set/kegg/kegg01/node",
            "/api/entry/unintegrated/pfam/PF17176/set/pfam",
            "/api/entry/interpro/pfam/PF02171/set/kegg/",
            "/api/entry/interpro/IPR003165/pfam/PF02171/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for org in response.data["sets"]:
                self._check_set_from_searcher(org)

    def test_can_filter_entry_counter_with_set_acc(self):
        urls = [
            "/api/entry/set/pfam/Cl0001",
            "/api/entry/set/kegg/kegg01",
            "/api/entry/set/kegg/kegg01/node/KEGG01-1",
            "/api/entry/set/kegg/kegg01/node/KEGG01-2",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_entry_count_overview(response.data)


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

    def test_can_filter_protein_counter_with_set_db(self):
        urls = [
            "/api/protein/set/pfam",
            "/api/protein/set/kegg",
            "/api/protein/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIn("proteins", response.data["proteins"]["uniprot"],
                          "'proteins' should be one of the keys in the response")
            self.assertIn("sets", response.data["proteins"]["uniprot"],
                          "'sets' should be one of the keys in the response")
            if "reviewed" in response.data["proteins"]:
                self.assertIn("proteins", response.data["proteins"]["reviewed"],
                              "'proteins' should be one of the keys in the response")
                self.assertIn("sets", response.data["proteins"]["reviewed"],
                              "'sets' should be one of the keys in the response")
            if "unreviewed" in response.data["proteins"]:
                self.assertIn("proteins", response.data["proteins"]["unreviewed"],
                              "'proteins' should be one of the keys in the response")
                self.assertIn("sets", response.data["proteins"]["unreviewed"],
                              "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/protein/reviewed/set/pfam",
            "/api/protein/unreviewed/set/kegg",
            "/api/protein/uniprot/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for s in result["sets"]:
                    self._check_set_from_searcher(s)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/protein/unreviewed/P16582/set/kegg/kegg01/node",
            "/api/protein/uniprot/M5ADK6/set/pfam",
            "/api/protein/reviewed/A1CUJ5/set/pfam",
            "/api/protein/reviewed/A1CUJ5/set/kegg",
            "/api/protein/reviewed/A1CUJ5/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_protein_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)

    def test_can_filter_counter_with_set_acc(self):
        urls = [
            "/api/protein/set/pfam/Cl0001",
            "/api/protein/set/kegg/kegg01",
            "/api/protein/set/kegg/kegg01/node/KEGG01-1",
            "/api/protein/set/kegg/kegg01/node/KEGG01-2",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_protein_count_overview(response.data)


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

    def test_can_filter_structure_counter_with_organism_db(self):
        urls = [
            "/api/structure/set/pfam",
            "/api/structure/set/kegg",
            "/api/structure/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIn("structures", response.data["structures"]["pdb"],
                          "'structures' should be one of the keys in the response")
            self.assertIn("sets", response.data["structures"]["pdb"],
                          "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/structure/pdb/set/pfam",
            "/api/structure/pdb/set/kegg",
            "/api/structure/pdb/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for s in result["sets"]:
                    self._check_set_from_searcher(s)

    def test_can_get_the_taxonomy_list_on_an_object(self):
        urls = [
            "/api/structure/pdb/1T2V/set/kegg",
            "/api/structure/pdb/1T2V/set/kegg/kegg01/node",
            "/api/structure/pdb/1JM7/set/pfam",
            "/api/structure/pdb/1JM7/set/kegg",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_structure_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)

    def test_can_filter_counter_with_set_acc(self):
        urls = [
            "/api/structure/set/pfam/Cl0001",
            "/api/structure/set/kegg/kegg01",
            "/api/structure/set/kegg/kegg01/node/KEGG01-1",
            "/api/structure/set/kegg/kegg01/node/KEGG01-2",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_structure_count_overview(response.data)



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

    def test_can_filter_organism_counter_with_organism_db(self):
        urls = [
            "/api/organism/set/pfam",
            "/api/organism/set/kegg",
            "/api/organism/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIn("organisms", response.data["organisms"]["proteome"],
                          "'organisms' should be one of the keys in the response")
            self.assertIn("sets", response.data["organisms"]["proteome"],
                          "'sets' should be one of the keys in the response")
            self.assertIn("organisms", response.data["organisms"]["taxonomy"],
                          "'organisms' should be one of the keys in the response")
            self.assertIn("sets", response.data["organisms"]["taxonomy"],
                          "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/organism/taxonomy/set/pfam",
            "/api/organism/proteome/set/kegg",
            "/api/organism/taxonomy/proteome/set/kegg/kegg01/node",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "sets")
            for result in response.data["results"]:
                for s in result["sets"]:
                    self._check_set_from_searcher(s)

    def test_can_get_the_set_list_on_a__tax_object(self):
        urls = [
            "/api/organism/taxonomy/2579/set/pfam",
            "/api/organism/taxonomy/2579/set/kegg",
            "/api/organism/taxonomy/2579/set/kegg/kegg01/node",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_taxonomy_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)

    def test_can_get_the_set_list_on_a_proteome_object(self):
        urls = [
            "/api/organism/proteome/UP000006701/set/pfam",
            "/api/organism/taxonomy/344612/proteome/UP000006701/set/pfam",
            "/api/organism/proteome/UP000006701/set/kegg",
            "/api/organism/taxonomy/344612/proteome/UP000006701/set/kegg",
            "/api/organism/proteome/UP000006701/set/kegg/kegg01/node",
            "/api/organism/taxonomy/344612/proteome/UP000006701/set/kegg/kegg01/node",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_proteome_details(response.data["metadata"])
            self.assertIn("sets", response.data)
            for s in response.data["sets"]:
                self._check_set_from_searcher(s)

    def test_can_filter_counter_with_set_acc(self):
        urls = [
            "/api/organism/set/pfam/Cl0001",
            "/api/organism/set/kegg/kegg01",
            "/api/organism/set/kegg/kegg01/node/KEGG01-1",
            "/api/organism/set/kegg/kegg01/node/KEGG01-2",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_organism_count_overview(response.data)


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

    def test_can_filter_set_counter_with_entry_db(self):
        acc = "IPR003165"
        urls = [
            "/api/set/entry/interpro",
            "/api/set/entry/pfam",
            "/api/set/entry/unintegrated",
            "/api/set/entry/unintegrated/pfam",
            "/api/set/entry/interpro/pfam",
            "/api/set/entry/interpro/"+acc+"/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            if "kegg" in response.data["sets"]:
                self.assertIn("entries", response.data["sets"]["kegg"],
                              "'entries' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["kegg"],
                              "'sets' should be one of the keys in the response")
            if "pfam" in response.data["sets"]:
                self.assertIn("entries", response.data["sets"]["pfam"],
                              "'entries' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["pfam"],
                              "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        acc = "IPR003165"
        urls = [
            "/api/set/kegg/entry/interpro",
            "/api/set/pfam/entry/pfam",
            "/api/set/pfam/entry/unintegrated",
            "/api/set/kegg/kegg01/node/entry/interpro/pfam",
            "/api/set/pfam/entry/interpro/"+acc+"/pfam",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")
            for result in response.data["results"]:
                for s in result["entries"]:
                    self._check_entry_from_searcher(s)

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/kegg/kegg01/entry/interpro",
            "/api/set/pfam/Cl0001/entry/pfam",
            "/api/set/pfam/CL0001/entry/unintegrated",
            "/api/set/kegg/kegg01/node/kegg01-1/entry/interpro/pfam",
            "/api/set/pfam/CL0001/entry/unintegrated/pfam",
            "/api/set/kegg/kegg01/entry/interpro/IPR003165/pfam",
            "/api/set/kegg/kegg01/node/KEGG01-1/entry/interpro/IPR003165/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"], True)
            self.assertIn("entries", response.data)
            for st in response.data["entries"]:
                self._check_entry_from_searcher(st)


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

    def test_can_filter_set_counter_with_protein_db(self):
        urls = [
            "/api/set/protein/uniprot",
            "/api/set/protein/reviewed",
            "/api/set/protein/unreviewed",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            if "kegg" in response.data["sets"]:
                self.assertIn("proteins", response.data["sets"]["kegg"],
                              "'proteins' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["kegg"],
                              "'sets' should be one of the keys in the response")
            if "pfam" in response.data["sets"]:
                self.assertIn("proteins", response.data["sets"]["pfam"],
                              "'proteins' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["pfam"],
                              "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/set/kegg/protein/uniprot",
            "/api/set/kegg/protein/unreviewed",
            "/api/set/pfam/protein/reviewed",
            "/api/set/kegg/kegg01/node/protein/unreviewed",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "proteins")
            for result in response.data["results"]:
                for s in result["proteins"]:
                    self._check_match(s, include_coordinates=False)

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/protein/reviewed",
            "/api/set/pfam/CL0001/protein/uniprot",
            "/api/set/kegg/kegg01/protein/unreviewed",
            "/api/set/kegg/kegg01/protein/reviewed",
            "/api/set/kegg/kegg01/node/kegg01-1/protein/reviewed",
            "/api/set/kegg/kegg01/node/KEGG01-1/protein/unreviewed",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"], True)
            self.assertIn("proteins", response.data)
            for st in response.data["proteins"]:
                self._check_match(st, include_coordinates=False)


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

    def test_can_filter_set_counter_with_structure_db(self):
        urls = [
            "/api/set/structure/pdb",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            if "kegg" in response.data["sets"]:
                self.assertIn("structures", response.data["sets"]["kegg"],
                              "'structures' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["kegg"],
                              "'sets' should be one of the keys in the response")
            if "pfam" in response.data["sets"]:
                self.assertIn("structures", response.data["sets"]["pfam"],
                              "'structures' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["pfam"],
                              "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/set/kegg/structure/pdb",
            "/api/set/kegg/structure/pdb",
            "/api/set/pfam/structure/pdb",
            "/api/set/kegg/kegg01/node/structure/pdb",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "structures")
            for result in response.data["results"]:
                for s in result["structures"]:
                    self._check_structure_chain_details(s)

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/structure/pdb",
            "/api/set/kegg/kegg01/structure/pdb",
            "/api/set/kegg/kegg01/node/KEGG01-1/structure/pdb",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"], True)
            self.assertIn("structures", response.data)
            for st in response.data["structures"]:
                self._check_structure_chain_details(st)


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

    def test_can_filter_set_counter_with_structure_db(self):
        urls = [
            "/api/set/organism/taxonomy",
            "/api/set/organism/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self.assertIsInstance(response.data, dict)
            if "kegg" in response.data["sets"]:
                self.assertIn("organisms", response.data["sets"]["kegg"],
                              "'organisms' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["kegg"],
                              "'sets' should be one of the keys in the response")
            if "pfam" in response.data["sets"]:
                self.assertIn("organisms", response.data["sets"]["pfam"],
                              "'organisms' should be one of the keys in the response")
                self.assertIn("sets", response.data["sets"]["pfam"],
                              "'sets' should be one of the keys in the response")

    def test_can_get_the_set_list_on_a_list(self):
        urls = [
            "/api/set/kegg/organism/taxonomy",
            "/api/set/kegg/organism/proteome",
            "/api/set/pfam/organism/taxonomy/proteome",
            "/api/set/kegg/kegg01/node/organism/taxonomy",
            "/api/set/kegg/kegg01/node/organism/proteome",
            "/api/set/kegg/kegg01/node/organism/taxonomy/proteome",
            ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_is_list_of_objects_with_key(response.data["results"], "metadata")
            self._check_is_list_of_objects_with_key(response.data["results"], "organisms")
            for result in response.data["results"]:
                for s in result["organisms"]:
                    self._check_organism_from_searcher(s)

    def test_can_get_a_list_from_the_set_object(self):
        urls = [
            "/api/set/pfam/Cl0001/organism/taxonomy",
            "/api/set/pfam/Cl0001/organism/taxonomy/1/proteome",
            "/api/set/pfam/Cl0001/organism/taxonomy/1001583/proteome",
            "/api/set/kegg/kegg01/organism/proteome",
            "/api/set/kegg/kegg01/node/KEGG01-1/organism/taxonomy/40296/proteome",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK, "URL : [{}]".format(url))
            self._check_set_details(response.data["metadata"], True)
            self.assertIn("organisms", response.data)
            for st in response.data["organisms"]:
                self._check_organism_from_searcher(st)
