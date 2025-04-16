from django.contrib.auth.decorators import login_required
from bangazonapi.models.product import Product
from bangazonapi.views import ProductSerializer
from bangazonapi.models.order import Order
from bangazonapi.models.orderproduct import OrderProduct
from django.shortcuts import render
from django.db.models import Sum, F
from django.urls import reverse
from bangazonapi.models.favorite import Favorite
from bangazonapi.models.customer import Customer


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

    elif "/reports/order" in request.path:

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


def favorite_sellers_report(request):
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
