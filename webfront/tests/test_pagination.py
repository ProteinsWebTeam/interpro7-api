from webfront.tests.InterproRESTTestCase import InterproRESTTestCase
from rest_framework import status


def get_next_value_from_response(response):
    try:
        return "/api" + response.data["next"].split("/api")[1]
    except:
        return None


def get_previous_value_from_response(response):
    try:
        return "/api" + response.data["previous"].split("/api")[1]
    except:
        return None


class PaginationOverSingleEnpointTest(InterproRESTTestCase):
    def test_pagesize(self):
        for size in range(1, 5):
            response = self.client.get("/api/entry/all?page_size={}".format(size))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), size)

    def test_pagesize_larger_than_total(self):
        size = 20
        response = self.client.get("/api/entry/all?page_size={}".format(size))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertLess(response.data["count"], size)

    def test_next_and_back_should_be_the_same(self):
        for size in range(1, 5):
            response = self.client.get("/api/entry/all?page_size={}".format(size))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            next_url = get_next_value_from_response(response)
            self.assertIsNotNone(next_url)
            next_response = self.client.get(next_url)
            self.assertEqual(next_response.status_code, status.HTTP_200_OK)
            previous_url = get_previous_value_from_response(next_response)
            self.assertIsNotNone(previous_url)
            previous_response = self.client.get(previous_url)
            self.assertEqual(previous_response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, previous_response.data)

    def test_walking_through_all_pages_and_back(self):
        full_response = self.client.get("/api/entry/all?page_size=20")
        self.assertEqual(full_response.status_code, status.HTTP_200_OK)
        for size in range(1, 10):
            response = self.client.get("/api/entry/all?page_size={}".format(size))
            self.assertEqual(
                response.data["results"], full_response.data["results"][:size]
            )
            next_url = get_next_value_from_response(response)
            start = size
            previous_url = None
            while next_url is not None:
                response = self.client.get(next_url)
                self.assertEqual(
                    response.data["results"],
                    full_response.data["results"][start : start + size],
                )
                next_url = get_next_value_from_response(response)
                previous_url = get_previous_value_from_response(response)
                start = start + size
            start = start - 2 * size
            while previous_url is not None:
                response = self.client.get(previous_url)
                self.assertEqual(
                    response.data["results"],
                    full_response.data["results"][start : start + size],
                )
                previous_url = get_previous_value_from_response(response)
                start = start - size


class PaginationOverMultipleEnpointTest(InterproRESTTestCase):
    def test_pagesize(self):
        for size in range(1, 5):
            response = self.client.get(
                "/api/entry/all/protein?page_size={}".format(size)
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), size)

    def test_pagesize_larger_than_total(self):
        size = 20
        response = self.client.get("/api/entry/all/protein?page_size={}".format(size))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(response.data["results"]))
        self.assertLess(response.data["count"], size)

    def test_next_and_back_should_be_the_same(self):
        for size in range(1, 5):
            response = self.client.get(
                "/api/entry/all/protein?page_size={}".format(size)
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            next_url = get_next_value_from_response(response)
            self.assertIsNotNone(next_url)
            next_response = self.client.get(next_url)
            self.assertEqual(next_response.status_code, status.HTTP_200_OK)
            previous_url = get_previous_value_from_response(next_response)
            self.assertIsNotNone(previous_url)
            previous_response = self.client.get(previous_url)
            self.assertEqual(previous_response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], previous_response.data["count"])
            self.assertEqual(
                response.data["results"], previous_response.data["results"]
            )
            self.assertEqual(response.data["next"], previous_response.data["next"])
            # self.assertEqual(response.data["previous"], previous_response.data["previous"])

    def test_next_until_the_end(self):
        full_response = self.client.get("/api/entry/all/protein?page_size=20")
        self.assertEqual(full_response.status_code, status.HTTP_200_OK)
        for size in range(1, 10):
            response = self.client.get(
                "/api/entry/all/protein?page_size={}".format(size)
            )
            count = len(response.data["results"])
            next_url = get_next_value_from_response(response)
            start = size
            while next_url is not None:
                response = self.client.get(next_url)
                count += len(response.data["results"])
                next_url = get_next_value_from_response(response)
                start = start + size
            self.assertEqual(len(full_response.data["results"]), count)

    def test_goto_the_end_and_prev_back(self):
        full_response = self.client.get("/api/entry/all/protein?page_size=20")
        self.assertEqual(full_response.status_code, status.HTTP_200_OK)
        for size in range(1, 10):
            response = self.client.get(
                "/api/entry/all/protein?page_size={}".format(size)
            )
            count = len(response.data["results"])
            next_url = get_next_value_from_response(response)
            start = size
            previous_url = None
            while next_url is not None:
                response = self.client.get(next_url)
                count += len(response.data["results"])
                next_url = get_next_value_from_response(response)
                previous_url = get_previous_value_from_response(response)
                start = start + size
            self.assertEqual(len(full_response.data["results"]), count)
            count -= len(response.data["results"])
            start = start - 2 * size
            while previous_url is not None:
                response = self.client.get(previous_url)
                count -= len(response.data["results"])
                previous_url = get_previous_value_from_response(response)
                start = start - size
            self.assertEqual(count, 0)
