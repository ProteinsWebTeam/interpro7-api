import unittest
import os

from rest_framework import status
from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from webfront.serializers.content_serializers import ModelContentSerializer

api_test_map = {
    "entry": {
        "interpro": ["IPR003165", "IPR001165"],
        "pfam": ["PF02171", "PF17180", "PF17176"],
        "smart": ["SM00950", "SM00002"],
        "profile": ["PS50822", "PS01031"],
        "interpro/pfam": ["PF02171"],
        "interpro/smart": ["SM00950"],
        "interpro/profile": ["PS50822"],
        "unintegrated/pfam": ["PF17180", "PF17176"],
        "unintegrated/smart": ["SM00002"],
        "unintegrated/profile": ["PS01031"],
    },
    "protein": {
        "uniprot": ["A1CUJ5", "M5ADK6", "A0A0A2L2G2", "P16582", "Q0VDM6"],
        "reviewed": ["A1CUJ5", "M5ADK6"],
        "unreviewed": ["A0A0A2L2G2", "P16582", "Q0VDM6"],
    },
    "structure": {"pdb": ["1JM7", "1T2V", "2BKM", "1JZ8"]},
    "taxonomy": {"uniprot": ["1", "2", "2579", "40296", "344612", "1001583", "10090"]},
    "proteome": {
        "uniprot": ["UP000006701", "UP000012042", "UP000030104", "UP000000589"]
    },
}
plurals = ModelContentSerializer.plurals

endpoints_with_url = ["entry", "protein", "proteome"]


class ObjectStructureTwoEndpointsTest(InterproRESTTestCase):
    def test_endpoints_independently(self):
        for endpoint in api_test_map:
            current = f"/api/{endpoint}"
            response = self.client.get(current)
            self.assertEqual(
                response.status_code, status.HTTP_200_OK, f"URL: [{current}]"
            )
            self._check_counter_by_endpoint(
                endpoint, response.data, f"URL: [{current}]"
            )

            for db in api_test_map[endpoint]:
                current = f"/api/{endpoint}/{db}"
                response_db = self.client.get(current)
                self.assertEqual(
                    response_db.status_code,
                    status.HTTP_200_OK,
                    f"URL: [{current}]",
                )
                self.assertEqual(
                    len(response_db.data["results"]),
                    len(api_test_map[endpoint][db]),
                    f"URL: [{current}]",
                )
                self._check_is_list_of_metadata_objects(
                    response_db.data["results"], f"URL: [{current}]"
                )

                for acc in api_test_map[endpoint][db]:
                    current = f"/api/{endpoint}/{db}/{acc}"
                    response_acc = self.client.get(current)
                    self.assertEqual(
                        response_acc.status_code,
                        status.HTTP_200_OK,
                        f"URL: [{current}]",
                    )
                    self._check_object_by_accesssion(
                        response_acc.data, f"URL: [{current}]"
                    )

                    self._check_structure_and_chains(
                        response_acc, endpoint, db, acc, f"URL: [{current}]"
                    )

    def test_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue

                # [endpoint]/[endpoint]
                current = f"/api/{endpoint1}/{endpoint2}"
                response = self.client.get(current)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    f"URL : [{current}]",
                )
                self._check_counter_by_endpoint(
                    endpoint1, response.data, f"URL : [{current}]"
                )
                self._check_counter_by_endpoint(
                    endpoint2, response.data, f"URL : [{current}]"
                )

    def test_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    # [endpoint]/[db]/[endpoint]
                    current = f"/api/{endpoint1}/{db}/{endpoint2}"
                    response = self._get_in_debug_mode(current)
                    if response.status_code == status.HTTP_200_OK:
                        self.assertEqual(
                            response.status_code,
                            status.HTTP_200_OK,
                            f"URL : [{current}]",
                        )
                        self._check_is_list_of_metadata_objects(
                            response.data["results"], f"URL : [{current}]"
                        )
                        self._check_is_list_of_objects_with_key(
                            response.data["results"],
                            plurals[endpoint2],
                            f"URL : [{current}]",
                        )
                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                        self.assertEqual(
                            response.status_code, status.HTTP_204_NO_CONTENT
                        )

    def test_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    # [endpoint]/[endpoint]/[db]
                    current = f"/api/{endpoint2}/{endpoint1}/{db}/"
                    response = self._get_in_debug_mode(current)
                    if response.status_code == status.HTTP_200_OK:
                        self.assertEqual(
                            response.status_code,
                            status.HTTP_200_OK,
                            f"URL : [{current}]",
                        )
                        self._check_counter_by_endpoint(
                            endpoint2, response.data, f"URL : [{current}]"
                        )
                        self._check_count_overview_per_endpoints(
                            response.data,
                            plurals[endpoint1],
                            plurals[endpoint2],
                            f"URL : [{current}]",
                        )
                    elif response.status_code != status.HTTP_204_NO_CONTENT:
                        self.fail(
                            "unexpected error code {} for the URL : [{}]".format(
                                response.status_code, current
                            )
                        )

    def test_acc_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for acc in api_test_map[endpoint1][db]:
                        # [endpoint]/[db]/[acc]/[endpoint]
                        current = f"/api/{endpoint1}/{db}/{acc}/{endpoint2}"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_200_OK,
                                f"URL : [{current}]",
                            )
                            self._check_object_by_accesssion(
                                response.data, f"URL : [{current}]"
                            )
                            self._check_counter_by_endpoint(
                                endpoint2, response.data, f"URL : [{current}]"
                            )
                            self._check_structure_and_chains(
                                response, endpoint1, db, acc, f"/{endpoint2}"
                            )
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(
                                response.status_code, status.HTTP_204_NO_CONTENT
                            )

    def test_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for acc in api_test_map[endpoint1][db]:
                        # [endpoint]/[endpoint]/[db]/[acc]
                        current = f"/api/{endpoint2}/{endpoint1}/{db}/{acc}/"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_200_OK,
                                f"URL : [{current}]",
                            )
                            self._check_counter_by_endpoint(
                                endpoint2, response.data, f"URL : [{current}]"
                            )
                            self._check_structure_chains_as_counter_filter(
                                endpoint1,
                                db,
                                acc,
                                endpoint2,
                                "",
                                plurals[endpoint1],
                                plurals[endpoint2],
                            )
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.fail("ONLY 204 Errors are expected")

    def test_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    # [endpoint]/[db]/[endpoint]/[db]
                    for db2 in api_test_map[endpoint2]:
                        current = f"/api/{endpoint1}/{db}/{endpoint2}/{db2}"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self._check_is_list_of_metadata_objects(
                                response.data["results"], f"URL : [{current}]"
                            )
                            key2 = f"{plurals[endpoint2]}_url"
                            if endpoint2 not in endpoints_with_url:
                                key2 = f"{endpoint2}_subset"
                                self._check_is_list_of_objects_with_key(
                                    response.data["results"],
                                    key2,
                                    f"URL : [{current}]",
                                )
                            for result in [x[key2] for x in response.data["results"]]:
                                if "_subset" in key2:
                                    self._check_list_of_matches(
                                        result,
                                        check_coordinates=endpoint2 != "taxonomy"
                                        and endpoint2 != "proteome",
                                        msg=f"URL : [{current}]",
                                    )
                                else:
                                    self.asserURL(
                                        result,
                                        f"The URL in {key2}: {result} is not valid | URL: {current}",
                                    )

                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_204_NO_CONTENT,
                                f"URL : [{current}]",
                            )

    def test_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for db2 in api_test_map[endpoint2]:
                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[endpoint]/[db]/[acc]
                            current = f"/api/{endpoint2}/{db2}/{endpoint1}/{db}/{acc}/"
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_200_OK,
                                    f"URL : [{current}]",
                                )
                                self._check_is_list_of_metadata_objects(
                                    response.data["results"]
                                )
                                for result in [
                                    x[plurals[endpoint1]]
                                    for x in response.data["results"]
                                ]:
                                    self._check_list_of_matches(
                                        result,
                                        check_coordinates=endpoint1 != "taxonomy"
                                        and endpoint1 != "proteome",
                                        msg=f"URL : [{current}]",
                                    )
                                self._check_structure_chains_as_filter(
                                    endpoint1,
                                    db,
                                    acc,
                                    f"{endpoint2}/{db2}",
                                    "",
                                    plurals[endpoint1],
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_204_NO_CONTENT,
                                    f"URL : [{current}]",
                                )

    def test_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for db2 in api_test_map[endpoint2]:
                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[db]
                            current = f"/api/{endpoint1}/{db}/{acc}/{endpoint2}/{db2}"
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_200_OK,
                                    f"URL : [{current}]",
                                )
                                self._check_object_by_accesssion(
                                    response.data, f"URL : [{current}]"
                                )
                                key = f"{plurals[endpoint2]}_url"
                                if endpoint2 not in endpoints_with_url:
                                    key = f"{endpoint2}_subset"
                                    self._check_list_of_matches(
                                        response.data[key],
                                        check_coordinates=endpoint2 != "taxonomy"
                                        and endpoint2 != "proteome",
                                        msg=f"URL : [{current}]",
                                    )
                                    self._check_structure_and_chains(
                                        response,
                                        endpoint1,
                                        db,
                                        acc,
                                        f"/{endpoint2}/{db2}",
                                        key,
                                        msg=f"URL : [{current}]",
                                    )
                                else:
                                    self.asserURL(
                                        response.data[key],
                                        f"The URL in {key}: {response.data[key]} is not valid | URL: {current}",
                                    )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(
                                    response.status_code, status.HTTP_204_NO_CONTENT
                                )

    def test_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for db in api_test_map[endpoint1]:
                    for db2 in api_test_map[endpoint2]:
                        for acc in api_test_map[endpoint1][db]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                            for acc2 in api_test_map[endpoint2][db2]:
                                current = "/api/{}/{}/{}/{}/{}/{}".format(
                                    endpoint1, db, acc, endpoint2, db2, acc2
                                )
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_object_by_accesssion(response.data)
                                    self._check_list_of_matches(
                                        response.data[plurals[endpoint2]],
                                        check_coordinates=endpoint2 != "taxonomy"
                                        and endpoint2 != "proteome",
                                        msg=f"URL : [{current}]",
                                    )
                                    self._check_structure_and_chains(
                                        response,
                                        endpoint1,
                                        db,
                                        acc,
                                        f"/{endpoint2}/{db2}/{acc2}",
                                        plurals[endpoint2],
                                    )
                                    self._check_structure_chains_as_filter(
                                        endpoint2,
                                        db2,
                                        acc2,
                                        f"{endpoint1}/{db}/{acc}",
                                        "",
                                        plurals[endpoint2],
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_204_NO_CONTENT,
                                        f"URL : [{current}]",
                                    )


@unittest.skipIf(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    "Skipping this test on Travis CI.",
)
class ObjectStructureThreeEndpointsTest(InterproRESTTestCase):
    def test_endpoint_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue

                    # [endpoint]/[endpoint]
                    current = f"/api/{endpoint1}/{endpoint2}/{endpoint3}"
                    response = self.client.get(current)
                    self.assertEqual(
                        response.status_code,
                        status.HTTP_200_OK,
                        f"URL : [{current}]",
                    )
                    self._check_counter_by_endpoint(
                        endpoint1, response.data, f"URL : [{current}]"
                    )
                    self._check_counter_by_endpoint(
                        endpoint2, response.data, f"URL : [{current}]"
                    )
                    self._check_counter_by_endpoint(
                        endpoint3, response.data, f"URL : [{current}]"
                    )

    def test_endpoint_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[endpoint]/[db]/[endpoint]
                        current = f"/api/{endpoint2}/{endpoint1}/{db1}/{endpoint3}"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_200_OK,
                                f"URL : [{current}]",
                            )
                            self._check_counter_by_endpoint(
                                endpoint2, response.data, f"URL : [{current}]"
                            )
                            self._check_counter_by_endpoint(
                                endpoint3, response.data, f"URL : [{current}]"
                            )
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(
                                response.status_code, status.HTTP_204_NO_CONTENT
                            )

    def test_db_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[db]/[endpoint]/[endpoint]
                        current = f"/api/{endpoint1}/{db1}/{endpoint2}/{endpoint3}"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_200_OK,
                                f"URL : [{current}]",
                            )
                            self._check_is_list_of_metadata_objects(
                                response.data["results"], f"URL : [{current}]"
                            )
                            self._check_is_list_of_objects_with_key(
                                response.data["results"],
                                plurals[endpoint2],
                                f"URL : [{current}]",
                            )
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.assertEqual(
                                response.status_code, status.HTTP_204_NO_CONTENT
                            )

    def test_endpoint_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for acc in api_test_map[endpoint1][db1]:
                            # [endpoint]/[endpoint]/[endpoint]/[db]/[acc]
                            current = (
                                f"/api/{endpoint2}/{endpoint3}/{endpoint1}/{db1}/{acc}/"
                            )
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_200_OK,
                                    f"URL : [{current}]",
                                )
                                self._check_counter_by_endpoint(
                                    endpoint2,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_counter_by_endpoint(
                                    endpoint3,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_structure_chains_as_counter_filter(
                                    endpoint1,
                                    db1,
                                    acc,
                                    f"{endpoint2}/{endpoint3}",
                                    "",
                                    plurals[endpoint1],
                                    plurals[endpoint2],
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail(
                                    "The response for [{}] had an HTTP error differen to 204".format(
                                        current
                                    )
                                )

    def test_endpoint_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[endpoint]/[endpoint]/[db]
                        current = f"/api/{endpoint2}/{endpoint3}/{endpoint1}/{db1}/"
                        response = self._get_in_debug_mode(current)
                        if response.status_code == status.HTTP_200_OK:
                            self.assertEqual(
                                response.status_code,
                                status.HTTP_200_OK,
                                f"URL : [{current}]",
                            )
                            self._check_counter_by_endpoint(
                                endpoint2, response.data, f"URL : [{current}]"
                            )
                            self._check_counter_by_endpoint(
                                endpoint3, response.data, f"URL : [{current}]"
                            )
                            self._check_count_overview_per_endpoints(
                                response.data,
                                plurals[endpoint1],
                                plurals[endpoint2],
                                f"URL : [{current}]",
                            )
                        elif response.status_code != status.HTTP_204_NO_CONTENT:
                            self.fail(
                                "The response for [{}] had an HTTP error differen to 204".format(
                                    current
                                )
                            )

    def test_endpoint_acc_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for acc in api_test_map[endpoint1][db1]:
                            # [endpoint]/[endpoint]/[db]/[acc]/[endpoint]
                            current = (
                                f"/api/{endpoint2}/{endpoint1}/{db1}/{acc}/{endpoint3}"
                            )
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_200_OK,
                                    f"URL : [{current}]",
                                )
                                self._check_counter_by_endpoint(
                                    endpoint2,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_counter_by_endpoint(
                                    endpoint3,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_structure_chains_as_counter_filter(
                                    endpoint1,
                                    db1,
                                    acc,
                                    endpoint2,
                                    f"/{endpoint3}",
                                    plurals[endpoint1],
                                    plurals[endpoint2],
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail(
                                    "The response for [{}] had an HTTP error differen to 204".format(
                                        current
                                    )
                                )

    def test_acc_endpoint_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for acc in api_test_map[endpoint1][db1]:
                            # [endpoint]/[db]/[acc]/[endpoint]/[endpoint]
                            current = (
                                f"/api/{endpoint1}/{db1}/{acc}/{endpoint2}/{endpoint3}"
                            )
                            response = self._get_in_debug_mode(current)

                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_200_OK,
                                    f"URL : [{current}]",
                                )
                                self._check_object_by_accesssion(
                                    response.data, f"URL : [{current}]"
                                )
                                self._check_counter_by_endpoint(
                                    endpoint2,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_counter_by_endpoint(
                                    endpoint3,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_structure_and_chains(
                                    response,
                                    endpoint1,
                                    db1,
                                    acc,
                                    f"/{endpoint2}/{endpoint3}",
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(
                                    response.status_code, status.HTTP_204_NO_CONTENT
                                )

    def test_db_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        # [endpoint]/[db]/[endpoint]/[db]/[endpoint]
                        for db2 in api_test_map[endpoint2]:
                            current = (
                                f"/api/{endpoint1}/{db1}/{endpoint2}/{db2}/{endpoint3}"
                            )
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self._check_is_list_of_metadata_objects(
                                    response.data["results"],
                                    f"URL : [{current}]",
                                )

                                key = f"{plurals[endpoint2]}_url"
                                if endpoint2 not in endpoints_with_url:
                                    key = f"{endpoint2}_subset"
                                self._check_is_list_of_objects_with_key(
                                    response.data["results"],
                                    key,
                                    f"URL : [{current}]",
                                )
                                for result in [
                                    x[key] for x in response.data["results"]
                                ]:
                                    if "_subset" in key:
                                        self._check_list_of_matches(
                                            result,
                                            check_coordinates=endpoint2 != "taxonomy"
                                            and endpoint2 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                    else:
                                        self.asserURL(
                                            result,
                                            f"The URL in {key}: {result} is not valid | URL: {current}",
                                        )
                                self._check_is_list_of_objects_with_key(
                                    response.data["results"],
                                    plurals[endpoint3],
                                    f"URL : [{current}]",
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(
                                    response.status_code, status.HTTP_204_NO_CONTENT
                                )

    def test_db_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            # [endpoint]/[db]/[endpoint]/[endpoint]/[db]
                            current = (
                                f"/api/{endpoint1}/{db1}/{endpoint3}/{endpoint2}/{db2}"
                            )
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self._check_is_list_of_metadata_objects(
                                    response.data["results"],
                                    f"URL : [{current}]",
                                )
                                key2 = f"{plurals[endpoint2]}_url"
                                if endpoint2 not in endpoints_with_url:
                                    key2 = f"{endpoint2}_subset"
                                self._check_is_list_of_objects_with_key(
                                    response.data["results"],
                                    key2,
                                    f"URL : [{current}]",
                                )
                                for result in [
                                    x[key2] for x in response.data["results"]
                                ]:
                                    if "_subset" in key2:
                                        self._check_list_of_matches(
                                            result,
                                            check_coordinates=endpoint2 != "taxonomy"
                                            and endpoint2 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                    else:
                                        self.asserURL(
                                            result,
                                            f"The URL in {key2}: {result} is not valid | URL: {current}",
                                        )
                                self._check_is_list_of_objects_with_key(
                                    response.data["results"],
                                    plurals[endpoint3],
                                    f"URL : [{current}]",
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.assertEqual(
                                    response.status_code, status.HTTP_204_NO_CONTENT
                                )

    def test_endpoint_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            # [endpoint]/[endpoint]/[db]/[endpoint]/[db]
                            current = (
                                f"/api/{endpoint3}/{endpoint2}/{db2}/{endpoint1}/{db1}"
                            )
                            response = self._get_in_debug_mode(current)
                            if response.status_code == status.HTTP_200_OK:
                                self.assertEqual(
                                    response.status_code,
                                    status.HTTP_200_OK,
                                    f"URL : [{current}]",
                                )
                                self._check_counter_by_endpoint(
                                    endpoint3,
                                    response.data,
                                    f"URL : [{current}]",
                                )
                                self._check_count_overview_per_endpoints(
                                    response.data,
                                    plurals[endpoint2],
                                    plurals[endpoint3],
                                    f"URL : [{current}]",
                                )
                                self._check_count_overview_per_endpoints(
                                    response.data,
                                    plurals[endpoint1],
                                    plurals[endpoint3],
                                    f"URL : [{current}]",
                                )
                            elif response.status_code != status.HTTP_204_NO_CONTENT:
                                self.fail(
                                    "The response for [{}] had an HTTP error differen to 204".format(
                                        current
                                    )
                                )

    def test_acc_db_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # [endpoint]/[db]/[acc]/[endpoint]/[db]/[endpoint]
                                current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{endpoint3}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_object_by_accesssion(
                                        response.data, f"URL : [{current}]"
                                    )
                                    key2 = f"{plurals[endpoint2]}_url"
                                    if endpoint2 not in endpoints_with_url:
                                        key2 = f"{endpoint2}_subset"
                                        self._check_list_of_matches(
                                            response.data[key2],
                                            check_coordinates=endpoint2 != "taxonomy"
                                            and endpoint2 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                    else:
                                        self.asserURL(
                                            response.data[key2],
                                            f"The URL in {key2}: {response.data[key2]} is not valid | URL: {current}",
                                        )
                                    self._check_counter_by_endpoint(
                                        endpoint3,
                                        response.data,
                                        f"URL : [{current}]",
                                    )
                                    self._check_structure_and_chains(
                                        response,
                                        endpoint1,
                                        db1,
                                        acc1,
                                        f"/{endpoint2}/{db2}/{endpoint3}",
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(
                                        response.status_code, status.HTTP_204_NO_CONTENT
                                    )

    def test_acc_endpoint_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # [endpoint]/[db]/[acc]/[endpoint]/[endpoint]/[db]
                                current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint3}/{endpoint2}/{db2}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_object_by_accesssion(
                                        response.data, f"URL : [{current}]"
                                    )
                                    key2 = f"{plurals[endpoint2]}_url"
                                    if endpoint2 not in endpoints_with_url:
                                        key2 = f"{endpoint2}_subset"
                                        self._check_list_of_matches(
                                            response.data[key2],
                                            check_coordinates=endpoint2 != "taxonomy"
                                            and endpoint2 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                    else:
                                        self.asserURL(
                                            response.data[key2],
                                            f"The URL in {key2}: {response.data[key2]} is not valid | URL: {current}",
                                        )
                                    self._check_counter_by_endpoint(
                                        endpoint3,
                                        response.data,
                                        f"URL : [{current}]",
                                    )
                                    self._check_structure_and_chains(
                                        response,
                                        endpoint1,
                                        db1,
                                        acc1,
                                        f"/{endpoint3}/{endpoint2}/{db2}",
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(
                                        response.status_code, status.HTTP_204_NO_CONTENT
                                    )

    def test_db_acc_endpoint(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[db]/[endpoint]/[db]/[acc]/[endpoint]
                                current = f"/api/{endpoint2}/{db2}/{endpoint1}/{db1}/{acc1}/{endpoint3}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_is_list_of_metadata_objects(
                                        response.data["results"]
                                    )
                                    for result in [
                                        x[plurals[endpoint1]]
                                        for x in response.data["results"]
                                    ]:
                                        self._check_list_of_matches(
                                            result,
                                            check_coordinates=endpoint1 != "taxonomy"
                                            and endpoint1 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                    self._check_is_list_of_objects_with_key(
                                        response.data["results"],
                                        plurals[endpoint3],
                                        f"URL : [{current}]",
                                    )
                                    self._check_structure_chains_as_filter(
                                        endpoint1,
                                        db1,
                                        acc1,
                                        f"{endpoint2}/{db2}",
                                        f"/{endpoint3}",
                                        plurals[endpoint1],
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(
                                        response.status_code, status.HTTP_204_NO_CONTENT
                                    )

    def test_db_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[db]/[endpoint]/[endpoint]/[db]/[acc]
                                current = f"/api/{endpoint2}/{db2}/{endpoint3}/{endpoint1}/{db1}/{acc1}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_is_list_of_metadata_objects(
                                        response.data["results"]
                                    )
                                    for result in [
                                        x[plurals[endpoint1]]
                                        for x in response.data["results"]
                                    ]:
                                        self._check_list_of_matches(
                                            result,
                                            check_coordinates=endpoint1 != "taxonomy"
                                            and endpoint1 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                    self._check_is_list_of_objects_with_key(
                                        response.data["results"],
                                        plurals[endpoint3],
                                        f"URL : [{current}]",
                                    )
                                    self._check_structure_chains_as_filter(
                                        endpoint1,
                                        db1,
                                        acc1,
                                        f"{endpoint2}/{db2}/{endpoint3}",
                                        "",
                                        plurals[endpoint1],
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(
                                        response.status_code, status.HTTP_204_NO_CONTENT
                                    )

    def test_endpoint_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[endpoint]/[db]/[endpoint]/[db]/[acc]
                                current = f"/api/{endpoint3}/{endpoint2}/{db2}/{endpoint1}/{db1}/{acc1}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_counter_by_endpoint(
                                        endpoint3,
                                        response.data,
                                        f"URL : [{current}]",
                                    )
                                    self._check_count_overview_per_endpoints(
                                        response.data,
                                        plurals[endpoint2],
                                        plurals[endpoint3],
                                        f"URL : [{current}]",
                                    )

                                    self._check_structure_chains_as_counter_filter(
                                        endpoint1,
                                        db1,
                                        acc1,
                                        f"{endpoint3}/{endpoint2}/{db2}/",
                                        "",
                                        plurals[endpoint1],
                                        plurals[endpoint3],
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.fail(
                                        "The response for [{}] had an HTTP error differen to 204".format(
                                            current
                                        )
                                    )

    def test_endpoint_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                # /[endpoint]/[endpoint]/[db]/[acc]/[endpoint]/[db]
                                current = f"/api/{endpoint3}/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_200_OK,
                                        f"URL : [{current}]",
                                    )
                                    self._check_counter_by_endpoint(
                                        endpoint3,
                                        response.data,
                                        f"URL : [{current}]",
                                    )
                                    self._check_count_overview_per_endpoints(
                                        response.data,
                                        plurals[endpoint2],
                                        plurals[endpoint3],
                                        f"URL : [{current}]",
                                    )

                                    self._check_structure_chains_as_counter_filter(
                                        endpoint1,
                                        db1,
                                        acc1,
                                        endpoint3,
                                        f"/{endpoint2}/{db2}",
                                        plurals[endpoint1],
                                        plurals[endpoint3],
                                    )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.fail(
                                        "unexpected error code {} for the URL : [{}]".format(
                                            response.status_code, current
                                        )
                                    )

    def test_acc_acc_endpoint(self):
        tested = []
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                for acc2 in api_test_map[endpoint2][db2]:
                                    # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]/[endpoint]
                                    current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{acc2}/{endpoint3}"
                                    tested.append(current)
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_200_OK,
                                            f"URL : [{current}]",
                                        )
                                        self._check_object_by_accesssion(response.data)
                                        self._check_list_of_matches(
                                            response.data[plurals[endpoint2]],
                                            check_coordinates=endpoint2 != "taxonomy"
                                            and endpoint2 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                        self._check_counter_by_endpoint(
                                            endpoint3,
                                            response.data,
                                            f"URL : [{current}]",
                                        )

                                        tested += self._check_structure_and_chains(
                                            response,
                                            endpoint1,
                                            db1,
                                            acc1,
                                            f"/{endpoint2}/{db2}/{acc2}/{endpoint3}",
                                        )

                                        tested += (
                                            self._check_structure_chains_as_filter(
                                                endpoint2,
                                                db2,
                                                acc2,
                                                f"{endpoint1}/{db1}/{acc1}",
                                                f"/{endpoint3}",
                                            )
                                        )

                                    elif (
                                        response.status_code
                                        != status.HTTP_204_NO_CONTENT
                                    ):
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_204_NO_CONTENT,
                                        )

    def test_acc_endpoint_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                for acc2 in api_test_map[endpoint2][db2]:
                                    # [endpoint]/[db]/[acc]/[endpoint]/[endpoint]/[db]/[acc]
                                    current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint3}/{endpoint2}/{db2}/{acc2}"
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_200_OK,
                                            f"URL : [{current}]",
                                        )
                                        self._check_object_by_accesssion(response.data)
                                        self._check_list_of_matches(
                                            response.data[plurals[endpoint2]],
                                            check_coordinates=endpoint2 != "taxonomy"
                                            and endpoint2 != "proteome",
                                            msg=f"URL : [{current}]",
                                        )
                                        self._check_counter_by_endpoint(
                                            endpoint3,
                                            response.data,
                                            f"URL : [{current}]",
                                        )

                                        self._check_structure_and_chains(
                                            response,
                                            endpoint1,
                                            db1,
                                            acc1,
                                            f"/{endpoint3}/{endpoint2}/{db2}/{acc2}",
                                        )

                                        self._check_structure_chains_as_filter(
                                            endpoint2,
                                            db2,
                                            acc2,
                                            f"{endpoint1}/{db1}/{acc1}/{endpoint3}",
                                            "",
                                        )
                                    elif (
                                        response.status_code
                                        != status.HTTP_204_NO_CONTENT
                                    ):
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_204_NO_CONTENT,
                                        )

    def test_endpoint_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for acc1 in api_test_map[endpoint1][db1]:
                                for acc2 in api_test_map[endpoint2][db2]:
                                    # /[endpoint]/[endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                                    current = f"/api/{endpoint3}/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{acc2}"

                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_200_OK,
                                            f"URL : [{current}]",
                                        )
                                        self._check_counter_by_endpoint(
                                            endpoint3,
                                            response.data,
                                            f"URL : [{current}]",
                                        )
                                        self._check_structure_chains_as_counter_filter(
                                            endpoint1,
                                            db1,
                                            acc1,
                                            endpoint3,
                                            f"/{endpoint2}/{db2}/{acc2}",
                                            plurals[endpoint1],
                                            plurals[endpoint3],
                                        )
                                        self._check_structure_chains_as_counter_filter(
                                            endpoint2,
                                            db2,
                                            acc2,
                                            f"{endpoint3}/{endpoint1}/{db1}/{acc1}",
                                            "",
                                            plurals[endpoint2],
                                            plurals[endpoint3],
                                        )
                                    elif (
                                        response.status_code
                                        != status.HTTP_204_NO_CONTENT
                                    ):
                                        self.fail(
                                            "unexpected error code {} for the URL : [{}]".format(
                                                response.status_code, current
                                            )
                                        )

    def test_db_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                current = f"/api/{endpoint1}/{db1}/{endpoint2}/{db2}/{endpoint3}/{db3}"
                                response = self._get_in_debug_mode(current)
                                if response.status_code == status.HTTP_200_OK:
                                    self._check_is_list_of_metadata_objects(
                                        response.data["results"],
                                        f"URL : [{current}]",
                                    )
                                    key2 = f"{plurals[endpoint2]}_url"
                                    if endpoint2 not in endpoints_with_url:
                                        key2 = f"{endpoint2}_subset"
                                    self._check_is_list_of_objects_with_key(
                                        response.data["results"],
                                        key2,
                                        f"URL : [{current}]",
                                    )
                                    for result in [
                                        x[key2] for x in response.data["results"]
                                    ]:
                                        if "_subset" in key2:
                                            self._check_list_of_matches(
                                                result,
                                                check_coordinates=endpoint2
                                                != "taxonomy"
                                                and endpoint2 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                        else:
                                            self.asserURL(
                                                result,
                                                f"The URL in {key2}: {result} is not valid | URL: {current}",
                                            )
                                    key3 = f"{plurals[endpoint3]}_url"
                                    if endpoint3 not in endpoints_with_url:
                                        key3 = f"{endpoint3}_subset"
                                    self._check_is_list_of_objects_with_key(
                                        response.data["results"],
                                        key3,
                                        f"URL : [{current}]",
                                    )
                                    for result in [
                                        x[key3] for x in response.data["results"]
                                    ]:
                                        if "_subset" in key3:
                                            self._check_list_of_matches(
                                                result,
                                                check_coordinates=endpoint3
                                                != "taxonomy"
                                                and endpoint3 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                        else:
                                            self.asserURL(
                                                result,
                                                f"The URL in {key3}: {result} is not valid | URL: {current}",
                                            )
                                elif response.status_code != status.HTTP_204_NO_CONTENT:
                                    self.assertEqual(
                                        response.status_code,
                                        status.HTTP_204_NO_CONTENT,
                                        f"URL : [{current}]",
                                    )

    def test_acc_db_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    # [endpoint]/[db]/[acc]/[endpoint]/[db]/[endpoint]/[db]
                                    current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{endpoint3}/{db3}"
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_200_OK,
                                            f"URL : [{current}]",
                                        )
                                        self._check_object_by_accesssion(
                                            response.data, f"URL : [{current}]"
                                        )
                                        key2 = f"{plurals[endpoint2]}_url"
                                        if endpoint2 not in endpoints_with_url:
                                            key2 = f"{endpoint2}_subset"
                                            self._check_list_of_matches(
                                                response.data[key2],
                                                check_coordinates=endpoint2
                                                != "taxonomy"
                                                and endpoint2 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                        else:
                                            self.asserURL(
                                                response.data[key2],
                                                f"The URL in {key2}: {response.data[key2]} is not valid | URL: {current}",
                                            )
                                        key3 = f"{plurals[endpoint3]}_url"
                                        if endpoint3 not in endpoints_with_url:
                                            key3 = f"{endpoint3}_subset"
                                            self._check_list_of_matches(
                                                response.data[key3],
                                                check_coordinates=endpoint3
                                                != "taxonomy"
                                                and endpoint3 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                        else:
                                            self.asserURL(
                                                response.data[key3],
                                                f"The URL in {key3}: {response.data[key3]} is not valid | URL: {current}",
                                            )
                                        self._check_structure_and_chains(
                                            response,
                                            endpoint1,
                                            db1,
                                            acc1,
                                            f"/{endpoint2}/{db2}/{endpoint3}/{db3}",
                                        )
                                    elif (
                                        response.status_code
                                        != status.HTTP_204_NO_CONTENT
                                    ):
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_204_NO_CONTENT,
                                        )

    def test_db_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    # /[endpoint]/[db]/[endpoint]/[db]/[acc]/[endpoint]/[db]
                                    current = f"/api/{endpoint2}/{db2}/{endpoint1}/{db1}/{acc1}/{endpoint3}/{db3}"
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self._check_is_list_of_metadata_objects(
                                            response.data["results"]
                                        )
                                        for result in [
                                            x[plurals[endpoint1]]
                                            for x in response.data["results"]
                                        ]:
                                            self._check_list_of_matches(
                                                result,
                                                check_coordinates=endpoint1
                                                != "taxonomy"
                                                and endpoint1 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                        key3 = f"{plurals[endpoint3]}_url"
                                        if endpoint3 not in endpoints_with_url:
                                            key3 = f"{endpoint3}_subset"
                                        for result in [
                                            x[key3] for x in response.data["results"]
                                        ]:
                                            if "_subset" in key3:
                                                self._check_list_of_matches(
                                                    result,
                                                    check_coordinates=endpoint3
                                                    != "taxonomy"
                                                    and endpoint3 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                            else:
                                                self.asserURL(
                                                    result,
                                                    f"The URL in {key3}: {result} is not valid | URL: {current}",
                                                )

                                        self._check_structure_chains_as_filter(
                                            endpoint1,
                                            db1,
                                            acc1,
                                            f"{endpoint2}/{db2}",
                                            f"/{endpoint3}/{db3}",
                                            plurals[endpoint1],
                                        )
                                    elif (
                                        response.status_code
                                        != status.HTTP_204_NO_CONTENT
                                    ):
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_204_NO_CONTENT,
                                        )

    def test_db_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    # /[endpoint]/[db]/[endpoint]/[db]/[endpoint]/[db]/[acc]
                                    current = f"/api/{endpoint2}/{db2}/{endpoint3}/{db3}/{endpoint1}/{db1}/{acc1}"
                                    response = self._get_in_debug_mode(current)
                                    if response.status_code == status.HTTP_200_OK:
                                        self._check_is_list_of_metadata_objects(
                                            response.data["results"]
                                        )
                                        for result in [
                                            x[plurals[endpoint1]]
                                            for x in response.data["results"]
                                        ]:
                                            self._check_list_of_matches(
                                                result,
                                                check_coordinates=endpoint1
                                                != "taxonomy"
                                                and endpoint1 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                        key3 = f"{plurals[endpoint3]}_url"
                                        if endpoint3 not in endpoints_with_url:
                                            key3 = f"{endpoint3}_subset"
                                        for result in [
                                            x[key3] for x in response.data["results"]
                                        ]:
                                            if "_subset" in key3:
                                                self._check_list_of_matches(
                                                    result,
                                                    check_coordinates=endpoint3
                                                    != "taxonomy"
                                                    and endpoint3 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                            else:
                                                self.asserURL(
                                                    result,
                                                    f"The URL in {key3}: {result} is not valid | URL: {current}",
                                                )

                                        self._check_structure_chains_as_filter(
                                            endpoint1,
                                            db1,
                                            acc1,
                                            f"{endpoint2}/{db2}/{endpoint3}/{db3}",
                                            "",
                                            plurals[endpoint1],
                                        )

                                    elif (
                                        response.status_code
                                        != status.HTTP_204_NO_CONTENT
                                    ):
                                        self.assertEqual(
                                            response.status_code,
                                            status.HTTP_204_NO_CONTENT,
                                        )

    def test_acc_acc_db(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]/[endpoint]/[db]
                                        current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{acc2}/{endpoint3}/{db3}"
                                        response = self._get_in_debug_mode(current)
                                        if response.status_code == status.HTTP_200_OK:
                                            self.assertEqual(
                                                response.status_code,
                                                status.HTTP_200_OK,
                                                f"URL : [{current}]",
                                            )
                                            self._check_object_by_accesssion(
                                                response.data
                                            )
                                            self._check_list_of_matches(
                                                response.data[plurals[endpoint2]],
                                                check_coordinates=endpoint2
                                                != "taxonomy"
                                                and endpoint2 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                            key3 = f"{plurals[endpoint3]}_url"
                                            if endpoint3 not in endpoints_with_url:
                                                key3 = f"{endpoint3}_subset"
                                                self._check_list_of_matches(
                                                    response.data[key3],
                                                    check_coordinates=endpoint3
                                                    != "taxonomy"
                                                    and endpoint3 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                            else:
                                                self.asserURL(
                                                    response.data[key3],
                                                    f"The URL in {key3}: {response.data[key3]} is not valid | URL: {current}",
                                                )
                                            self._check_structure_and_chains(
                                                response,
                                                endpoint1,
                                                db1,
                                                acc1,
                                                f"/{endpoint2}/{db2}/{acc2}/{endpoint3}/{db3}",
                                            )
                                            self._check_structure_chains_as_filter(
                                                endpoint2,
                                                db2,
                                                acc2,
                                                f"{endpoint1}/{db1}/{acc1}",
                                                f"/{endpoint3}/{db3}",
                                                plurals[endpoint2],
                                            )
                                        elif (
                                            response.status_code
                                            != status.HTTP_204_NO_CONTENT
                                        ):
                                            self.assertEqual(
                                                response.status_code,
                                                status.HTTP_204_NO_CONTENT,
                                            )

    def test_acc_db_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[endpoint]/[db]/[acc]
                                        current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint3}/{db3}/{endpoint2}/{db2}/{acc2}"
                                        response = self._get_in_debug_mode(current)
                                        if response.status_code == status.HTTP_200_OK:
                                            self.assertEqual(
                                                response.status_code,
                                                status.HTTP_200_OK,
                                                f"URL : [{current}]",
                                            )
                                            self._check_object_by_accesssion(
                                                response.data
                                            )
                                            self._check_list_of_matches(
                                                response.data[plurals[endpoint2]],
                                                check_coordinates=endpoint2
                                                != "taxonomy"
                                                and endpoint2 != "proteome",
                                                msg=f"URL : [{current}]",
                                            )
                                            key3 = f"{plurals[endpoint3]}_url"
                                            if endpoint3 not in endpoints_with_url:
                                                key3 = f"{endpoint3}_subset"
                                                self._check_list_of_matches(
                                                    response.data[key3],
                                                    check_coordinates=endpoint3
                                                    != "taxonomy"
                                                    and endpoint3 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                            else:
                                                self.asserURL(
                                                    response.data[key3],
                                                    f"The URL in {key3}: {response.data[key3]} is not valid | URL: {current}",
                                                )
                                            self._check_structure_and_chains(
                                                response,
                                                endpoint1,
                                                db1,
                                                acc1,
                                                f"/{endpoint3}/{db3}/{endpoint2}/{db2}/{acc2}",
                                            )
                                            self._check_structure_chains_as_filter(
                                                endpoint2,
                                                db2,
                                                acc2,
                                                f"{endpoint1}/{db1}/{acc1}/{endpoint3}/{db3}",
                                                "",
                                                plurals[endpoint2],
                                            )
                                        elif (
                                            response.status_code
                                            != status.HTTP_204_NO_CONTENT
                                        ):
                                            self.assertEqual(
                                                response.status_code,
                                                status.HTTP_204_NO_CONTENT,
                                            )

    def test_db_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                                        current = f"/api/{endpoint3}/{db3}/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{acc2}"
                                        response = self._get_in_debug_mode(current)
                                        if response.status_code == status.HTTP_200_OK:
                                            self.assertEqual(
                                                response.status_code,
                                                status.HTTP_200_OK,
                                                f"URL : [{current}]",
                                            )
                                            self._check_is_list_of_metadata_objects(
                                                response.data["results"]
                                            )
                                            for result in [
                                                x[plurals[endpoint1]]
                                                for x in response.data["results"]
                                            ]:
                                                self._check_list_of_matches(
                                                    result,
                                                    check_coordinates=endpoint1
                                                    != "taxonomy"
                                                    and endpoint1 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                            for result in [
                                                x[plurals[endpoint2]]
                                                for x in response.data["results"]
                                            ]:
                                                self._check_list_of_matches(
                                                    result,
                                                    check_coordinates=endpoint2
                                                    != "taxonomy"
                                                    and endpoint2 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                            self._check_structure_chains_as_filter(
                                                endpoint1,
                                                db1,
                                                acc1,
                                                f"{endpoint3}/{db3}",
                                                f"/{endpoint2}/{db2}/{acc2}",
                                                plurals[endpoint1],
                                            )
                                            self._check_structure_chains_as_filter(
                                                endpoint2,
                                                db2,
                                                acc2,
                                                f"{endpoint3}/{db3}/{endpoint1}/{db1}/{acc1}",
                                                "",
                                                plurals[endpoint2],
                                            )
                                        elif (
                                            response.status_code
                                            != status.HTTP_204_NO_CONTENT
                                        ):
                                            self.assertEqual(
                                                response.status_code,
                                                status.HTTP_204_NO_CONTENT,
                                            )

    def test_acc_acc_acc(self):
        for endpoint1 in api_test_map:
            for endpoint2 in api_test_map:
                if endpoint1 == endpoint2:
                    continue
                for endpoint3 in api_test_map:
                    if endpoint3 == endpoint1 or endpoint3 == endpoint2:
                        continue
                    for db1 in api_test_map[endpoint1]:
                        for db2 in api_test_map[endpoint2]:
                            for db3 in api_test_map[endpoint3]:
                                for acc1 in api_test_map[endpoint1][db1]:
                                    for acc2 in api_test_map[endpoint2][db2]:
                                        # [endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]/[endpoint]/[db]/[acc]
                                        for acc3 in api_test_map[endpoint3][db3]:
                                            current = f"/api/{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{acc2}/{endpoint3}/{db3}/{acc3}"
                                            response = self._get_in_debug_mode(current)
                                            if (
                                                response.status_code
                                                == status.HTTP_200_OK
                                            ):
                                                self.assertEqual(
                                                    response.status_code,
                                                    status.HTTP_200_OK,
                                                    f"URL : [{current}]",
                                                )
                                                self._check_object_by_accesssion(
                                                    response.data
                                                )
                                                self._check_list_of_matches(
                                                    response.data[plurals[endpoint2]],
                                                    check_coordinates=endpoint2
                                                    != "taxonomy"
                                                    and endpoint2 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                                self._check_list_of_matches(
                                                    response.data[plurals[endpoint3]],
                                                    check_coordinates=endpoint3
                                                    != "taxonomy"
                                                    and endpoint3 != "proteome",
                                                    msg=f"URL : [{current}]",
                                                )
                                                self._check_structure_and_chains(
                                                    response,
                                                    endpoint1,
                                                    db1,
                                                    acc1,
                                                    f"/{endpoint2}/{db2}/{acc2}/{endpoint3}/{db3}/{acc3}",
                                                )
                                                self._check_structure_chains_as_filter(
                                                    endpoint2,
                                                    db2,
                                                    acc2,
                                                    f"{endpoint1}/{db1}/{acc1}",
                                                    f"/{endpoint3}/{db3}/{acc3}",
                                                    plurals[endpoint2],
                                                )
                                                self._check_structure_chains_as_filter(
                                                    endpoint3,
                                                    db3,
                                                    acc3,
                                                    f"{endpoint1}/{db1}/{acc1}/{endpoint2}/{db2}/{acc2}",
                                                    "",
                                                    plurals[endpoint3],
                                                )
                                            elif (
                                                response.status_code
                                                != status.HTTP_204_NO_CONTENT
                                            ):
                                                self.assertEqual(
                                                    response.status_code,
                                                    status.HTTP_204_NO_CONTENT,
                                                )
