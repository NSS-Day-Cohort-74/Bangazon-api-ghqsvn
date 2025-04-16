"""View module for handling requests about customer profiles"""

import json
import datetime
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from bangazonapi.models import Order, Customer, Product
from bangazonapi.models import OrderProduct, Favorite
from bangazonapi.models import Recommendation, Like
from .product import ProductSerializer
from .order import OrderSerializer


class Profile(ViewSet):
    """Request handlers for user profile info in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        @api {GET} /profile GET user profile info
        @apiName GetProfile
        @apiGroup UserProfile

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {Number} id Profile id
        @apiSuccess (200) {String} url URI of customer profile
        @apiSuccess (200) {Object} user Related user object
        @apiSuccess (200) {String} user.first_name Customer first name
        @apiSuccess (200) {String} user.last_name Customer last name
        @apiSuccess (200) {String} user.email Customer email
        @apiSuccess (200) {String} phone_number Customer phone number
        @apiSuccess (200) {String} address Customer address
        @apiSuccess (200) {Object[]} payment_types Array of user's payment types
        @apiSuccess (200) {Object[]} recommends Array of recommendations made by the user

        @apiSuccessExample {json} Success
            HTTP/1.1 200 OK
            {
                "id": 7,
                "url": "http://localhost:8000/customers/7",
                "user": {
                    "first_name": "Brenda",
                    "last_name": "Long",
                    "email": "brenda@brendalong.com"
                },
                "phone_number": "555-1212",
                "address": "100 Indefatiguable Way",
                "payment_types": [
                    {
                        "url": "http://localhost:8000/paymenttypes/3",
                        "deleted": null,
                        "merchant_name": "Visa",
                        "account_number": "fj0398fjw0g89434",
                        "expiration_date": "2020-03-01",
                        "create_date": "2019-03-11",
                        "customer": "http://localhost:8000/customers/7"
                    }
                ],
                "recommends": [
                    {
                        "product": {
                            "id": 32,
                            "name": "DB9"
                        },
                        "customer": {
                            "id": 5,
                            "user": {
                                "first_name": "Joe",
                                "last_name": "Shepherd",
                                "email": "joe@joeshepherd.com"
                            }
                        }
                    }
                ]
            }
        """
        try:
            current_user = Customer.objects.get(user=request.auth.user)
            current_user.recommends = Recommendation.objects.filter(
                recommender=current_user
            )
            current_user.recommended = Recommendation.objects.filter(
                customer=current_user
            )

            serializer = ProfileSerializer(
                current_user, many=False, context={"request": request}
            )

            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    @action(methods=["get", "post", "delete"], detail=False)
    def cart(self, request):
        """Shopping cart manipulation"""

        current_user = Customer.objects.get(user=request.auth.user)

        if request.method == "DELETE":
            """
            @api {DELETE} /profile/cart DELETE all line items in cart
            @apiName DeleteCart
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccessExample {json} Success
                HTTP/1.1 204 No Content
            @apiError (404) {String} message  Not found message.
            """
            try:
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                line_items = OrderProduct.objects.filter(order=open_order)
                line_items.delete()
                open_order.delete()
            except Order.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        if request.method == "GET":
            """
            @api {GET} /profile/cart GET line items in cart
            @apiName GetCart
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccess (200) {Number} id Order cart
            @apiSuccess (200) {String} url URL of order
            @apiSuccess (200) {String} created_date Date created
            @apiSuccess (200) {Object} payment_type Payment Id used to complete order
            @apiSuccess (200) {String} customer URI for customer
            @apiSuccess (200) {Number} size Number of items in cart
            @apiSuccess (200) {Object[]} line_items Line items in cart
            @apiSuccess (200) {Number} line_items.id Line item id
            @apiSuccess (200) {Object} line_items.product Product in cart
            @apiSuccessExample {json} Success
                {
                    "id": 2,
                    "url": "http://localhost:8000/orders/2",
                    "created_date": "2019-04-12",
                    "payment_type": null,
                    "customer": "http://localhost:8000/customers/7",
                    "line_items": [
                        {
                            "id": 4,
                            "product": {
                                "id": 52,
                                "url": "http://localhost:8000/products/52",
                                "name": "900",
                                "price": 1296.98,
                                "number_sold": 0,
                                "description": "1987 Saab",
                                "quantity": 2,
                                "created_date": "2019-03-19",
                                "location": "Vratsa",
                                "image_path": null,
                                "average_rating": 0,
                                "category": {
                                    "url": "http://localhost:8000/productcategories/2",
                                    "name": "Auto"
                                }
                            }
                        }
                    ],
                    "size": 1
                }
            @apiError (404) {String} message  Not found message
            """
            try:
                # Gets current_user's order, where no payment is yet given
                open_order = Order.objects.get(customer=current_user, payment_type=None)
                # Gets all order/product relationships associated with customer's open order id

                # Initializes empty dictionary to send in response to client
                cart = {}
                # Creates new dictionary key holding serialized data following OrderSerializer pattern
                cart["order"] = OrderSerializer(
                    open_order, many=False, context={"request": request}
                ).data
                # Calculates the size of an order by list containing line_items
                cart["order"]["size"] = len(cart["order"]["lineitems"])
            except Order.DoesNotExist as ex:
                return Response(
                    {"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(cart["order"], status=status.HTTP_200_OK)

        if request.method == "POST":
            """
            @api {POST} /profile/cart POST new product to cart
            @apiName AddToCart
            @apiGroup UserProfile

            @apiHeader {String} Authorization Auth token
            @apiHeaderExample {String} Authorization
                Token 9ba45f09651c5b0c404f37a2d2572c026c146611

            @apiSuccess (200) {Object} line_item Line items in cart
            @apiSuccess (200) {Number} line_item.id Line item id
            @apiSuccess (200) {Object} line_item.product Product in cart
            @apiSuccess (200) {Object} line_item.order Open order for cart
            @apiSuccessExample {json} Success
                {
                    "id": 14,
                    "product": {
                        "url": "http://localhost:8000/products/52",
                        "deleted": null,
                        "name": "900",
                        "price": 1296.98,
                        "description": "1987 Saab",
                        "quantity": 2,
                        "created_date": "2019-03-19",
                        "location": "Vratsa",
                        "image_path": null,
                        "customer": "http://localhost:8000/customers/7",
                        "category": "http://localhost:8000/productcategories/2"
                    },
                    "order": {
                        "url": "http://localhost:8000/orders/2",
                        "created_date": "2019-04-12",
                        "customer": "http://localhost:8000/customers/7",
                        "payment_type": null
                    }
                }

            @apiError (404) {String} message  Not found message
            """

            try:

                open_order = Order.objects.get(
                    customer=current_user, payment_type__isnull=True
                )

            except Order.DoesNotExist as ex:
                open_order = Order()
                open_order.created_date = datetime.datetime.now()
                open_order.customer = current_user
                open_order.save()

            line_item = OrderProduct()
            line_item.product = Product.objects.get(pk=request.data["product_id"])
            line_item.order = open_order
            line_item.save()

            line_item_json = LineItemSerializer(
                line_item, many=False, context={"request": request}
            )

            return Response(
                {"line_item": line_item_json.data, "order_no": open_order.id},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"details": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(methods=["get"], detail=False)
    def favoritesellers(self, request):
        """
        @api {GET} /profile/favoritesellers GET favorite sellers
        @apiName GetFavoriteSellers
        @apiGroup UserProfile

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiSuccess (200) {id} id Favorite id
        @apiSuccess (200) {Object} seller Favorited seller
        @apiSuccess (200) {String} seller.url Seller URI
        @apiSuccess (200) {String} seller.phone_number Seller phone number
        @apiSuccess (200) {String} seller.address Seller address
        @apiSuccess (200) {String} seller.user Seller user profile URI
        @apiSuccessExample {json} Success
            [
                {
                    "id": 1,
                    "seller": {
                        "url": "http://localhost:8000/customers/5",
                        "phone_number": "555-1212",
                        "address": "100 Endless Way",
                        "user": "http://localhost:8000/users/6"
                    }
                },
                {
                    "id": 2,
                    "seller": {
                        "url": "http://localhost:8000/customers/6",
                        "phone_number": "555-1212",
                        "address": "100 Dauntless Way",
                        "user": "http://localhost:8000/users/7"
                    }
                },
                {
                    "id": 3,
                    "seller": {
                        "url": "http://localhost:8000/customers/7",
                        "phone_number": "555-1212",
                        "address": "100 Indefatiguable Way",
                        "user": "http://localhost:8000/users/8"
                    }
                }
            ]
        """
        customer = Customer.objects.get(user=request.user.id)
        favorites = Favorite.objects.filter(customer=customer)

        serializer = FavoriteSerializer(
            favorites, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(methods=["get", "post"], detail=False)
    def favorite(self, request):
        """
        Endpoint responsible for creating new customer-to-store relationships
        Args:
            request (dict): The request body sent from the client containing data required for
            creating these relationships.
            pk (integer): The primary key used to find a unique collection of data.
            In this case, we are searching for the unique id of a customer acting as a seller.

            Defaults to None.

        Returns:
            Response Message and Status Code: Used to enlighten the user about the status of the
            favoriting process, whether it succeeded or failed.
        """

        # Gets customer making request
        favoring_customer = Customer.objects.get(user=request.auth.user)

        # Gets customer acting as seller to be favorited
        seller = Customer.objects.get(pk=int(request.data["store_id"]))

        try:
            # Does the relationship between these two customers already exist?
            existing_relationship = Favorite.objects.filter(
                customer=favoring_customer, seller=seller
            ).exists()

            if existing_relationship:
                return Response(
                    "Failure!: This relationship already exists",
                    status=status.HTTP_409_CONFLICT,
                )

            # Creates a new instance of a favorite object, this will hold data necessary for creating relationships
            favorite_relationship = Favorite()

            # Add the customer that is favoriting the store to the relationship
            favorite_relationship.customer = favoring_customer

            # Add the customer-seller that is being favorited to the relationship
            favorite_relationship.seller = seller

            # Create the relationship in the database
            favorite_relationship.save()

            # Return a response to the client notifying them of a successful creation process
            return Response(
                "Success!: You have successfully favorited this store!",
                status=status.HTTP_201_CREATED,
            )
        except Exception as ex:
            # Return a response to the client notifying them of a failure during the creation process
            return Response(
                f"Failure!: There was failure creating this relationship: {ex.args[0]}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post", "get"], detail=False)
    def store(self, request):
        # Gets authenticated user's customer profile.
        customer = Customer.objects.get(user=request.auth.user)
        # Is the authenticated user making a POST request
        if request.method == "POST":
            try:
                # Is request body data good?
                customer.store_name = request.data["name"]
                customer.store_description = request.data["description"]
                customer.save()
                # If request body data is good, send back the created object to the client as JSON.
                return Response(
                    {
                        "id": customer.id,
                        "name": customer.store_name,
                        "description": customer.store_description,
                    },
                    status=status.HTTP_201_CREATED,
                )
            # If request body data is not good, send an error to the client explaining what went wrong
            except Exception as ex:
                return Response(
                    {"details": f"Do better. {ex}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Is the client making a GET request for their store data?
        if request.method == "GET":
            # Filters all products by authenticated user's customer profile
            store_products = Product.objects.filter(customer=customer)
            serializered_store_products = ProductSerializer(
                store_products,
                many=True,
            )
            try:
                store = {
                    "id": customer.id,
                    "name": customer.store_name,
                    "description": customer.store_description,
                    "products": serializered_store_products.data,
                }
                return Response(store, status=status.HTTP_200_OK)
            except Exception as ex:
                return Response({"details": ex}, status=status.HTTP_400_BAD_REQUEST)


class LineItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for products

    Arguments:
        serializers
    """

    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        fields = ("id", "product")
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for customer profile

    Arguments:
        serializers
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        depth = 1


class CustomerSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendation customers"""

    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
        )


class ProfileProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "image_path",
        )


class RecommenderSerializer(serializers.ModelSerializer):
    """JSON serializer for recommendations"""

    customer = CustomerSerializer()
    product = ProfileProductSerializer()

    class Meta:
        model = Recommendation
        fields = (
            "product",
            "customer",
        )


class ProfileSerializer(serializers.ModelSerializer):
    """JSON serializer for customer profile

    Arguments:
        serializers
    """

    user = UserSerializer(many=False)
    recommends = RecommenderSerializer(many=True)
    recommended = RecommenderSerializer(many=True)
    store = serializers.SerializerMethodField()
    favorites = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    def get_is_admin(self, obj):
        # Check if the user is an admin
        if obj.user.is_staff:
            return True
        else:
            return False

    liked_products = serializers.SerializerMethodField()

    def get_favorites(self, obj):
        # Finds the customer who is making the request for their profile
        customer = Customer.objects.get(user=self.context["request"].user)
        try:
            # Filters the customer-to-store favorite relationships based on the requesting customer
            favorites = Favorite.objects.filter(customer=customer)

            # Serialize the list of this customer's favorite stores
            serializer = FavoriteSerializer(
                favorites, many=True, context={"request": self.context["request"]}
            )

            # Return the serialized list to the parent serializer.
            return serializer.data
        # If a customer does not any favorite stores, this field will be an empty initialized list
        except Exception as ex:
            # This is exception will only be thrown if there is a major error in the serialization process
            return f"There has been an issue serializing this data: {ex.args[0]}"

    def get_store(self, pbj):
        store = {}
        store["name"] = pbj.store_name
        store["description"] = pbj.store_description
        store["id"] = pbj.id

        return store

    def get_liked_products(self, obj):
        # Finds the customer who is making the request for their profile
        customer = Customer.objects.get(user=self.context["request"].user)

        # Filters all product-like relationships based on what this customer has liked
        likes = Like.objects.filter(customer=customer)

        # Gets product objects from the product-likes relationship
        liked_products = [like.product for like in likes]

        # Serialize this customer's liked products
        serializer = ProductSerializer(
            liked_products, many=True, context={"request": self.context["request"]}
        )

        # return a serialized list of liked products to be included in the likes field
        return serializer.data


    class Meta:
        model = Customer
        fields = (
            "id",
            "url",
            "user",
            "phone_number",
            "address",
            "payment_types",
            "recommends",
            "recommended",
            "store",
            "favorites",
            "is_admin",
            "liked_products",

        )
        depth = 1


class FavoriteUserSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for favorite sellers user

    Arguments:
        serializers
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
        depth = 1


class FavoriteSellerSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for favorite sellers

    Arguments:
        serializers
    """

    user = FavoriteUserSerializer(many=False)

    class Meta:
        model = Customer
        fields = (
            "id",
            "url",
            "user",
        )
        depth = 1


class FavoriteSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for favorites

    Arguments:
        serializers
    """

    seller = FavoriteSellerSerializer(many=False)

    class Meta:
        model = Favorite
        fields = ("id", "seller")
        depth = 2
