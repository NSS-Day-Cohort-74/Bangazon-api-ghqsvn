from django.contrib.auth.decorators import login_required
from bangazonapi.models.product import Product
from bangazonapi.views import ProductSerializer
from bangazonapi.models.order import Order
from bangazonapi.models.orderproduct import OrderProduct
from django.shortcuts import render
from django.db.models import Sum, F
from django.urls import reverse


@login_required(login_url="reports_login")
def report(request):
    if request.path == "/reports/expensiveproducts":
        products = Product.objects.filter(price__gte=1000).order_by("price")[:20]
        serialized_products = ProductSerializer(products, many=True)
        context = {
            "title": "20 most Expensive products",
            "heading": "20 most Expensive products",
            "pricey_products": serialized_products.data,
        }
        return render(request, "report.html", context)
    elif request.path == "/reports/inexpensiveproducts":
        products = Product.objects.filter(price__lte=999).order_by("price")
        serialized_products = ProductSerializer(products, many=True)
        context = {
            "title": "Least Expensive products",
            "heading": "Least Expensive products",
            "pricey_products": serialized_products.data,
        }
        return render(request, "report.html", context)
    elif request.path == "/reports/order":


        # Check the URL parameter 'status'
        status = request.GET.get(
            "status", "completed"
        )  # Default to 'completed' if not specified

        # Base queryset
        orders_queryset = Order.objects.all()

        # Apply filters based on status parameter
        if status == "incomplete":
            # Filter for incomplete orders (payment_type_id is null)
            orders_queryset = orders_queryset.filter(payment_type_id__isnull=True)
        else:  # 'completed' or any other value
            # Filter for completed orders (payment_type_id is not null)
            orders_queryset = orders_queryset.filter(payment_type_id__isnull=False)

        # Continue with annotating and values as before
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

