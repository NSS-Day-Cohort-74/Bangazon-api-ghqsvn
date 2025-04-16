import json
from rest_framework import status
from rest_framework.test import APITestCase


class OrderTests(APITestCase):
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
        }
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a product category
        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        # Create a product
        url = "/products"
        data = {
            "name": "Kite",
            "price": 14.99,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_order(self):
        """
        Ensure we can add a product to an order.
        """
        # Add product to order
        url = "/profile/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get cart and verify product was added
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)

    def test_remove_product_from_order(self):
        """
        Ensure we can remove a product from an order.
        """
        # Add product
        self.test_add_product_to_order()

        # Remove product from cart
        url = "/lineitems/1"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.delete(url, None, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was removed
        url = "/profile/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["size"], 0)
        self.assertEqual(len(json_response["lineitems"]), 0)

    def test_remove_order(self):
        """
        Ensure we can remove a product from an order.
        """
        # Add product
        self.test_add_product_to_order()

        # Remove product from cart
        url = "/profile/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.delete(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was removed
        url = "/profile/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_not_added_to_closed_order(self):
        """
        Ensure that a product cannot be added to a closed order.
        """
        # add product to users order
        url = "/profile/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # create new payment type for user
        url = "/payment-types"
        data = {
            "merchant_name": "Visa",
            "account_number": "1234567890",
            "expiration_date": "2025-12-02",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_type_id = json.loads(response.content)["id"]

        # Complete order
        url = "/cart/complete"
        data = {"payment_type_id": payment_type_id}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # create new cart
        url = "/profile/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_correct_order(self):
        """
        Ensure that a product is added to the correct order.
        """
        # Create new user
        url = "/register"
        data = {
            "username": "john",
            "password": "password",
            "email": "john@example.com",
            "address": "123 Road St",
            "phone_number": "931-000-0000",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_two_token = json.loads(response.content)["token"]

        # add product to user 1 cart
        url = "/profile/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # add product to user 2 cart
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_two_token)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get user 1 cart
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_one_cart = json.loads(response.content)
        # validate item added to user 1 cart
        self.assertEqual(user_one_cart["size"], 1)
        self.assertEqual(len(user_one_cart["lineitems"]), 1)

        # get user 2 cart
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_two_token)
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # validate item added to user 2 cart
        user_two_cart = json.loads(response.content)
        self.assertEqual(user_two_cart["size"], 1)
        self.assertEqual(len(user_two_cart["lineitems"]), 1)

    # TODO: Complete order by adding payment type
    def test_add_payment_type_to_order(self):
        url = "/profile/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        self.client.post(url, data, format="json")

        response = self.client.get("/cart", format="json")
        order_id = json.loads(response.content)["id"]

        data = {
            "merchant_name": "Visa",
            "account_number": "03030303934",
            "expiration_date": "2111-01-01"
        }
        response = self.client.post("/payment-types", data, format="json")
        payment_type_id = json.loads(response.content)["id"]

        data = {"payment_type": payment_type_id}
        self.client.put(f"/orders/{order_id}", data, format="json")

        response = self.client.get(f"/orders/{order_id}", format="json")
        order = json.loads(response.content)
        self.assertEqual(order["payment_type"]["id"], payment_type_id)

