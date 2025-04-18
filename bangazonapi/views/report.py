from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication, BaseAuthentication
from bangazonapi.models.product import Product
from rest_framework import serializers
from bangazonapi.views import ProductSerializer
from bangazonapi.models.order import Order
from django.db.models import Sum, F
from django.shortcuts import render
from django.contrib.auth.models import User
from bangazonapi.models import Report, Customer, Favorite


class ReportAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # get the token from the request parameters
        token = request.query_params.get("token")
        if token:
            try:
                user = User.objects.get(auth_token=token)
                return (user, token)
            except User.DoesNotExist:
                return None


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "title", "description", "url")
        read_only_fields = ("id",)
        depth = 1


class ReportView(ViewSet):
    authentication_classes = [ReportAuthentication]
    permission_classes = [IsAdminUser]

    def list(self, request):
        report_urls = Report.objects.all()
        serialized_reports = ReportSerializer(
            report_urls, many=True, context={"request": request}
        )
        return Response(serialized_reports.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="expensiveproducts")
    def expensive_products(self, request):
        # Handle expensive products report
        products = Product.objects.filter(price__gte=1000).order_by("price")[:20]
        serialized_products = ProductSerializer(products, many=True)
        context = {
            "title": "20 most Expensive products",
            "heading": "20 most Expensive products",
            "pricey_products": serialized_products.data,
        }
        return render(request, "report.html", context)

    @action(detail=False, methods=["get"], url_path="inexpensiveproducts")
    def inexpensive_products(self, request):
        # Handle inexpensive products report
        products = Product.objects.filter(price__lte=999).order_by("price")
        serialized_products = ProductSerializer(products, many=True)
        context = {
            "title": "Least Expensive products",
            "heading": "Least Expensive products",
            "pricey_products": serialized_products.data,
        }
        return render(request, "report.html", context)

    @action(detail=False, methods=["get"], url_path="orders")
    def orders_report(self, request):
        # Handle orders report
        status = request.GET.get("status", "completed")
        orders_queryset = Order.objects.all()

        if status == "incomplete":
            orders_queryset = orders_queryset.filter(payment_type_id__isnull=True)
        else:
            orders_queryset = orders_queryset.filter(payment_type_id__isnull=False)

        completed_orders = orders_queryset.annotate(
            total_cost=Sum(F("lineitems__product__price")),
            customer_name=F("customer__user__first_name"),
            customer_last_name=F("customer__user__last_name"),
        ).values("id", "customer_name", "customer_last_name", "total_cost")

        context = {
            "title": "Orders Report",
            "heading": f"{status.capitalize()} Orders with Totals",
            "orders": completed_orders,
        }
        return render(request, "orderreport.html", context)

    @action(detail=False, methods=["get"], url_path="favoritesellers")
    def favorite_sellers_report(self, request):
        customer_id = request.GET.get("customer")

        if not customer_id:
            return render(
                request,
                "favoritesreport.html",
                {
                    "title": "Favorite Sellers Report",
                    "heading": "Missing Customer ID",
                    "error": "You must include a customer ID in the URL (e.g., ?customer=1).",
                },
            )

        try:
            customer = Customer.objects.select_related("user").get(pk=customer_id)
        except Customer.DoesNotExist:
            return render(
                request,
                "report.html",
                {
                    "title": "Favorite Sellers Report",
                    "heading": "Customer Not Found",
                    "error": f"No customer found with ID {customer_id}.",
                },
            )

        # Get the favorite sellers (which are also customers)
        favorites = Favorite.objects.filter(customer_id=customer_id).select_related(
            "seller__user"
        )  # ensure we prefetch user data
        sellers = [favorite.seller for favorite in favorites]

        context = {
            "title": "Favorite Sellers",
            "heading": f"Favorite Sellers of {customer.user.first_name} {customer.user.last_name}",
            "sellers": sellers,
        }

        return render(request, "favoritesreport.html", context)
