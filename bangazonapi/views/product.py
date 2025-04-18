"""View module for handling requests about products"""

from rest_framework.decorators import action
from bangazonapi.models.recommendation import Recommendation
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.conf import settings
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import Product, Customer, ProductCategory, Like, ProductRating
from bangazonapi.views.customer import CustomerSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from bangazonapi.views.productcategory import ProductCategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    is_liked = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "number_sold",
            "description",
            "quantity",
            "created_date",
            "location",
            "image_path",
            "avg_rating",
            "can_be_rated",
            "ratings",
            "is_liked",
            "likes"
        )
        depth = 4

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request:
            return obj.is_liked(request, obj.id)
        return False

    def get_likes(self, obj):
        # Filters product-likes relationships based on product primary key
        likes = Like.objects.filter(product=obj.id)

        # Gets the length of the list containing all likes associated with this product
        return len(likes)
    
    def get_avg_rating(self, obj):
        return obj.avg_rating

    def get_ratings(self, obj):
        ratings = ProductRating.objects.filter(product=obj)
        if ratings:
            serialized_ratings = ProductRatingSerializer(
                ratings, many=True, context=self.context
            )
            return serialized_ratings.data
        return None


class ProductRatingSerializer(serializers.ModelSerializer):
    """JSON serializer for product ratings"""

    customer = CustomerSerializer(
        many=False,
        read_only=True,
    )
    product = ProductSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = ProductRating
        fields = ("id", "customer", "product", "rating", "review", "created_date")
        depth = 1


class Products(ViewSet):
    """Request handlers for Products in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /products POST new product
        @apiName CreateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} name Short form name of product
        @apiParam {Number} price Cost of product
        @apiParam {String} description Long form description of product
        @apiParam {Number} quantity Number of items to sell
        @apiParam {String} location City where product is located
        @apiParam {Number} category_id Category of product
        @apiParamExample {json} Input
            {
                "name": "Kite",
                "price": 14.99,
                "description": "It flies high",
                "quantity": 60,
                "location": "Pittsburgh",
                "category_id": 4
            }

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        new_product = Product()
        new_product.name = request.data["name"]
        new_product.price = request.data["price"]
        new_product.description = request.data["description"]
        new_product.quantity = request.data["quantity"]
        new_product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        new_product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["categoryId"])
        new_product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f"{new_product.id}-{request.data['name']}.{ext}",
            )

            new_product.image_path = data
        new_product.full_clean()
        new_product.save()

        serializer = ProductSerializer(new_product, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /products/:id GET product
        @apiName GetProduct
        @apiGroup Product

        @apiParam {id} id Product Id

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        try:
            product = Product.objects.get(pk=pk)
            is_liked = product.is_liked(request, pk)
            serializer = ProductSerializer(product, context={"request": request})
            response_data = serializer.data
            response_data["is_liked"] = is_liked
            return Response(response_data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /products/:id PUT changes to product
        @apiName UpdateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]
        product.created_date = request.data["created_date"]
        product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        product.category = product_category
        product.full_clean()
        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /products/:id DELETE product
        @apiName DeleteProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            product = Product.objects.filter(pk=pk).first()
            product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """
        @api {GET} /products GET all products
        @apiName ListProducts
        @apiGroup Product

        @apiSuccess (200) {Object[]} products Array of products
        @apiSuccessExample {json} Success
            [
                {
                    "id": 101,
                    "url": "http://localhost:8000/products/101",
                    "name": "Kite",
                    "price": 14.99,
                    "number_sold": 0,
                    "description": "It flies high",
                    "quantity": 60,
                    "created_date": "2019-10-23",
                    "location": "Pittsburgh",
                    "image_path": null,
                    "average_rating": 0,
                    "category": {
                        "url": "http://localhost:8000/productcategories/6",
                        "name": "Games/Toys"
                    }
                }
            ]
        """

        products = Product.objects.all()

        # Support filtering by category and/or quantity
        category_id = self.request.query_params.get("category", None)
        quantity = self.request.query_params.get("quantity", None)
        order = self.request.query_params.get("order_by", None)
        direction = self.request.query_params.get("direction", None)
        name = self.request.query_params.get("name", None)
        number_sold = self.request.query_params.get("number_sold", None)
        min_price = self.request.query_params.get("min_price", None)
        max_price = self.request.query_params.get("max_price", None)
        product_location = self.request.query_params.get("location", None)

        if order is not None:
            order_filter = order

            if direction is not None:
                if direction == "desc":
                    order_filter = f"-{order}"

            products = products.order_by(order_filter)
        if name is not None:
            products = products.filter(name__icontains=name)

        if category_id is not None:
            products = products.filter(category__id=category_id)

        if quantity is not None:
            products = products.order_by("-created_date")[: int(quantity)]

        if number_sold is not None:

            def sold_filter(product):
                if product.number_sold >= int(number_sold):
                    return True
                return False

            products = filter(sold_filter, products)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        if product_location is not None:
            products = products.filter(location=product_location)

        # Has the query been filtered? Checks all possible filtering conditions. 
        if category_id is None and quantity is None and order is None and direction is None and name is None and number_sold is None and min_price is None and product_location is None:

            # Gets all categories, expanded with the last five products in that category
            categories = ProductCategory.objects.all()
            
            # Serializes the categories list with the products expansion
            serializer = ProductCategorySerializer(categories, many=True, context={"request":request})
            product_serializer = ProductSerializer(
                products, many=True
            )

            # A collection of unique locations
            locations = set(product['location'] for product in product_serializer.data)

            # Sends a custom response to the client with a key representing if the response was filtered or not
            return Response({"no_filter": True, "locations":locations,"products": serializer.data}, status=status.HTTP_200_OK)

        else:
            product_serializer = ProductSerializer(
                products, many=True
            )
            locations = set(product['location'] for product in product_serializer.data)
            
            return Response({"no_filter": False,"locations":locations,"products": product_serializer.data}, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=True)
    def recommend(self, request, pk=None):
        """Recommend products to other users"""

        if request.method != "POST":
            return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            recipient_customer = Customer.objects.get(
                user__username=request.data["recipient"]
            )
        except Customer.DoesNotExist:
            return Response("Recipient not found", status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

        recommender_customer = Customer.objects.get(user=request.auth.user)

        if Recommendation.objects.filter(
            recommender=recommender_customer,
            customer=recipient_customer,
            product=product,
        ).exists():
            return Response(
                "You have already recommended this product to this user",
                status=status.HTTP_400_BAD_REQUEST,
            )

        rec = Recommendation()
        rec.recommender = recommender_customer
        rec.customer = recipient_customer
        rec.product = product
        rec.save()
        return Response(None, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=True)
    def add_to_order(self, request, pk=None):
        """Add product to order"""
        if request.method == "POST":
            pass

    @action(methods=["post", "delete"], detail=True)
    def like(self, request, pk=True):

        try:
            customer = Customer.objects.get(user=request.auth.user)
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist as Ex:
            return Response(f"Details: {ex.args[0]}", status=status.HTTP_404_NOT_FOUND)
        try:
            customer_liked_products =  Like.objects.filter(customer=customer, product=product)
            if customer_liked_products.exists():
                customer_liked_products.delete()
                return Response("deleted", status=status.HTTP_204_NO_CONTENT)
            
            like = Like()
            like.customer = Customer.objects.filter(user=request.auth.user).first()
            like.product = Product.objects.filter(pk=pk).first()
            like.save()
            return Response("created", status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"error": ex}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["post", "delete"], detail=True)
    def rate(self, request, pk=None):
        """Rate a product"""
        try:
            product_to_rate = Product.objects.get(pk=pk)
            customer = Customer.objects.get(user=request.auth.user)
            rating = request.data.get("rating", None)

            product_rating = ProductRating()
            product_rating.customer = customer
            product_rating.product = product_to_rate

            if rating and rating["score"]:
                product_rating.rating = rating["score"]

            if rating["review"]:
                product_rating.review = rating["review"]

            product_rating.save()

            msg = {"created": True}
            return Response(msg, status=status.HTTP_201_CREATED)

        except Exception as ex:
            msg = {
                "created": False,
                "details": ex.args[0],
            }
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
