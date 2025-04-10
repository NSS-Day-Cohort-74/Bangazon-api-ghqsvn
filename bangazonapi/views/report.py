from bangazonapi.models.product import Product
from bangazonapi.models.order import Order
from bangazonapi.models.orderproduct import OrderProduct
from django.shortcuts import render
from django.db.models import Sum, F


def report(request):
    products = Product.objects.filter(price__gte=1000).order_by("price")[:20]
    context = {
        "title": "20 most Expensive products",
        "heading": "20 most Expensive products",
        "products": products,
    }
    return render(request, "productreport.html", context)


def ireport(request):
    products = Product.objects.filter(price__lte=999).order_by("price")[:20]
    context = {
        "title": "20 least Expensive products",
        "heading": "20 least Expensive products",
        "products": products,
    }
    return render(request, "productreport.html", context)


def ocreport(request):
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

