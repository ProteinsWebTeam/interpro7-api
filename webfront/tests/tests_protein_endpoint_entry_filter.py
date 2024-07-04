from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase


# import unittest


class ProteinWithFilterEntryRESTTest(InterproRESTTestCase):
    def test_can_get_protein_amount_from_entry(self):
        response = self.client.get("/api/protein/entry")
        self._check_protein_count_overview(response.data)
        self.assertIn(
            "entries",
            response.data,
            "'entries' should be one of the keys in the response",
        )
        self._check_entry_count_overview(response.data)

    def test_urls_that_return_list_of_accessions_and_entries(self):
        urls = [
            "/api/protein/uniprot/entry/",
            "/api/protein/reviewed/entry/",
            "/api/protein/unreviewed/entry/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(response.data["results"], "entries")

    def test_can_get_entries_from_protein_id(self):
        reviewed = "A1CUJ5"
        unreviewed = "P16582"
        urls = [
            "/api/protein/uniprot/" + reviewed + "/entry/",
            "/api/protein/uniprot/" + unreviewed + "/entry/",
            "/api/protein/reviewed/" + reviewed + "/entry/",
            "/api/protein/unreviewed/" + unreviewed + "/entry/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertIn(
                "entries",
                response.data,
                "'entries' should be one of the keys in the response",
            )
            self._check_protein_details(response.data["metadata"])
            self._check_entry_count_overview(response.data)

    def test_urls_that_should_fails_with_no_content(self):
        tests = ["/api/protein/uniprot/A0A0A2L2G2/entry/"]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg="The URL [" + url + "] should've failed."
            )

    def test_urls_that_should_fails(self):
        reviewed = "A1CUJ5"
        unreviewed = "P16582"
        tests = [
            "/api/protein/reviewed/" + unreviewed + "/entry/",
            "/api/protein/unreviewed/" + reviewed + "/entry/",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_204_NO_CONTENT,
                msg="The URL [" + url + "] should've failed.",
            )
        tests = [
            "/api/protein/reviewed/" + unreviewed + "/bad_endpoint/",
            "/api/protein/bad_db/" + reviewed + "/entry/",
            "/api/protein/bad_db/entry/",
            "/api/protein/reviewed/bad_endpoint/",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_404_NOT_FOUND,
                msg="The URL [" + url + "] should've failed.",
            )


class ProteinWithFilterEntryDatabaseRESTTest(InterproRESTTestCase):
    def test_urls_that_return_object_of_protein_and_entry_counts(self):
        acc = "IPR003165"
        urls = [
            "/api/protein/entry/interpro",
            "/api/protein/entry/pfam",
            "/api/protein/entry/unintegrated",
            "/api/protein/entry/unintegrated/pfam",
            "/api/protein/entry/interpro/pfam",
            "/api/protein/entry/interpro/" + acc + "/pfam",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, dict)
            for prot_db in response.data["proteins"]:
                self.assertIn(prot_db, ["uniprot", "reviewed", "unreviewed"])
                self.assertIn("proteins", response.data["proteins"][prot_db])
                self.assertIn("entries", response.data["proteins"][prot_db])

    def test_urls_that_return_list_of_protein_accessions_with_matches(self):
        acc = "IPR003165"
        urls = [
            "/api/protein/uniprot/entry/interpro",
            "/api/protein/reviewed/entry/interpro",
            "/api/protein/unreviewed/entry/interpro",
            "/api/protein/uniprot/entry/pfam",
            "/api/protein/uniprot/entry/unintegrated",
            "/api/protein/uniprot/entry/unintegrated/pfam",
            "/api/protein/uniprot/entry/interpro/pfam",
            "/api/protein/uniprot/entry/interpro/" + acc + "/pfam",
        ]
        for url in urls:
            self._check_list_url_with_and_without_subset(
                url,
                "entry",
                inner_subset_check_fn=self._check_match,
            )

    def test_urls_that_return_a_protein_details_with_matches(self):
        sp_1 = "M5ADK6"
        sp_2 = "A1CUJ5"
        acc = "IPR003165"
        urls = {
            f"/api/protein/uniprot/{sp_2}/entry/interpro": ["IPR003165", "IPR001165"],
            f"/api/protein/uniprot/{sp_1}/entry/unintegrated": ["PF17180", "PTHR43214"],
            f"/api/protein/uniprot/{sp_2}/entry/pfam": ["PF17176", "PF02171"],
            f"/api/protein/uniprot/{sp_2}/entry/interpro/pfam": ["PF02171"],
            f"/api/protein/uniprot/{sp_2}/entry/interpro/smart": ["SM00950"],
            f"/api/protein/uniprot/{sp_1}/entry/unintegrated/pfam": ["PF17180"],
            f"/api/protein/uniprot/{sp_2}/entry/interpro/{acc}/smart": ["SM00950"],
            f"/api/protein/uniprot/{sp_2}/entry/interpro/{acc}/pfam": ["PF02171"],
        }
        for url in urls:
            self._check_details_url_with_and_without_subset(
                url,
                "entry",
                inner_subset_check_fn=self._check_entry_from_searcher,
                check_metadata_fn=self._check_protein_details,
                subset_check_fn=lambda subset: self.assertEqual(
                    len(subset),
                    len(urls[url]),
                    "The number of entries should be the same URL: [{}]".format(url),
                )
                and self.assertIn(subset[0]["accession"].upper(), urls[url]),
            )
            response = self.client.get(url + "?show-subset")

    def test_urls_that_should_fails(self):
        tr_1 = "P16582"
        sp_1 = "M5ADK6"
        tests = [
            "/api/protein/reviewed/" + tr_1 + "/entry/unintegrated",
            "/api/protein/unreviewed/" + sp_1 + "/entry/unintegrated",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_204_NO_CONTENT,
                msg="The URL [" + url + "] should've failed.",
            )
        tests = [
            "/api/protein/reviewed/" + tr_1 + "/entry/bad_db",
            "/api/protein/unreviewed/" + sp_1 + "/bad_endpoint/unintegrated",
            "/api/bad_endpoint/reviewed/" + tr_1 + "/entry/unintegrated",
            "/api/protein/bad_db/" + sp_1 + "/entry/unintegrated",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_404_NOT_FOUND,
                msg="The URL [" + url + "] should've failed.",
            )

    def test_urls_that_should_fails_with_no_content(self):
        tr_1 = "P16582"
        tests = [
            "/api/protein/entry/unintegrated/smart",
            "/api/protein/uniprot/entry/unintegrated/smart",
            f"/api/protein/uniprot/{tr_1}/entry/unintegrated",
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg="The URL [" + url + "] should've failed."
            )


class ProteinWithFilterEntryDatabaseAccessionRESTTest(InterproRESTTestCase):
    def test_urls_that_return_object_of_protein_and_entry_counts(self):
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        urls = [
            "/api/protein/entry/unintegrated/pfam/" + pfam_u,
            "/api/protein/entry/interpro/pfam/" + pfam,
            "/api/protein/entry/pfam/" + pfam,
            "/api/protein/entry/interpro/" + acc + "/pfam/" + pfam,
            "/api/protein/entry/interpro/" + acc,
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_protein_count_overview(response.data)

    def test_can_get_entries_from_protein_id_interpro_ids(self):
        acc = "A1CUJ5"
        ips = ["IPR001165", "IPR003165"]
        for ip in ips:
            url = "/api/protein/uniprot/" + acc + "/entry/interpro/" + ip
            response = self.client.get(url)
            self._check_single_entry_response(response, "URL: [{}]".format(url))

    def test_urls_that_return_list_of_protein_accessions_with_matches_and_detailed_entries(
        self,
    ):
        acc = "IPR003165"
        pfam = "PF02171"
        smart = "SM00950"
        urls = [
            "/api/protein/uniprot/entry/interpro/" + acc,
            "/api/protein/reviewed/entry/interpro/" + acc,
            "/api/protein/unreviewed/entry/interpro/" + acc,
            "/api/protein/uniprot/entry/pfam/" + pfam,
            "/api/protein/uniprot/entry/interpro/smart/" + smart,
            "/api/protein/uniprot/entry/interpro/pfam/" + pfam,
            "/api/protein/uniprot/entry/interpro/" + acc + "/pfam/" + pfam,
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._check_is_list_of_objects_with_key(
                response.data["results"], "metadata"
            )
            self._check_is_list_of_objects_with_key(
                response.data["results"],
                "entries",
                "It should have the key 'entries' for the URL [" + url + "]",
            )
            for protein in response.data["results"]:
                for match in protein["entries"]:
                    self._check_match(match)
                    # self._check_entry_details(match["entry"])

    def test_urls_that_return_a_protein_details_with_matches(self):
        sp_1 = "M5ADK6"
        sp_2 = "A1CUJ5"
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        smart = "SM00950"
        urls = [
            "/api/protein/uniprot/" + sp_2 + "/entry/interpro/" + acc,
            "/api/protein/uniprot/" + sp_2 + "/entry/pfam/" + pfam,
            "/api/protein/uniprot/" + sp_2 + "/entry/interpro/pfam/" + pfam,
            "/api/protein/uniprot/" + sp_2 + "/entry/interpro/smart/" + smart,
            "/api/protein/uniprot/"
            + sp_2
            + "/entry/interpro/"
            + acc
            + "/smart/"
            + smart,
            "/api/protein/uniprot/" + sp_2 + "/entry/interpro/" + acc + "/pfam/" + pfam,
            "/api/protein/uniprot/" + sp_1 + "/entry/unintegrated/pfam/" + pfam_u,
        ]
        for url in urls:
            response = self.client.get(url)
            self._check_protein_details(response.data["metadata"])
            self.assertIn(
                "entries",
                response.data,
                "'entries' should be one of the keys in the response",
            )
            # self.assertEqual(len(response.data["entries"]), 1,
            #                  "The number of entries should be 1. URL: [{}]".format(url))
            self._check_match(response.data["entries"][0])
            # self._check_entry_details(response.data["entries"][0]["entry"])

    def test_can_get_entries_from_protein_id_pfam_id(self):
        acc = "A1CUJ5"
        pfam = "PF02171"
        response = self.client.get(
            "/api/protein/uniprot/" + acc + "/entry/pfam/" + pfam
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._check_single_entry_response(response)

    def test_urls_that_should_fails_with_no_content(self):
        tr_1 = "P16582"
        sp_1 = "M5ADK6"
        acc = "IPR003165"
        pfam = "PF02171"
        pfam_u = "PF17180"
        tests = [
            "/api/protein/uniprot/" + tr_1 + "/entry/unintegrated/pfam/" + pfam_u,
            "/api/protein/uniprot/" + sp_1 + "/entry/interpro/" + acc,
            "/api/protein/uniprot/" + sp_1 + "/entry/interpro/" + acc + "/pfam/" + pfam,
            "/api/protein/uniprot/entry/unintegrated/pfam/" + pfam,
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url, msg="The URL [" + url + "] should've failed."
            )

    def test_urls_that_should_fail(self):
        tr_1 = "P16582"
        sp_1 = "M5ADK6"
        pfam_u = "PF17180"
        tests = [
            "/api/protein/reviewed/" + tr_1 + "/entry/unintegrated/pfam/" + pfam_u,
            "/api/protein/unreviewed/" + sp_1 + "/entry/unintegrated/pfam/" + pfam_u,
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_204_NO_CONTENT,
                msg="The URL [" + url + "] should've failed.",
            )
        tests = [
            "/api/bad_endpoint/reviewed/" + tr_1 + "/entry/unintegrated/pfam/" + pfam_u,
            "/api/protein/unreviewed/"
            + sp_1
            + "/bad_endpoint/unintegrated/pfam/"
            + pfam_u,
            "/api/protein/bad_db/" + tr_1 + "/entry/unintegrated/pfam/" + pfam_u,
            "/api/protein/bad_db/" + tr_1 + "/entry/unintegrated/bad_db/" + pfam_u,
            "/api/protein/unreviewed/" + sp_1 + "/entry/bad_db/pfam/" + pfam_u,
        ]
        for url in tests:
            self._check_HTTP_response_code(
                url,
                code=status.HTTP_404_NOT_FOUND,
                msg="The URL [" + url + "] should've failed.",
            )
