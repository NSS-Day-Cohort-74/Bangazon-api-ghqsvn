import json
import datetime
from rest_framework import status
from rest_framework.test import APITestCase


class StoreTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
            "store_name": "",
            "store_description": "",
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Sporting Goods")

    def test_create_store(self):
        """
        Ensure we can create a new product.
        """
        # what view we are pointing to
        url = "/profile/store"

        data = {
            "name": "Best Store",
            "description": "Only great things here",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        # Specifies we are inserting data to the url in json format
        response = self.client.post(url, data, format="json")
        # getting back the content of the response
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Best Store")
        self.assertEqual(json_response["description"], "Only great things here")
        self.assertEqual(json_response["id"], 1)
