from bangazonapi.models.product import Product
from django.shortcuts import render


def report(request):
    products = Product.objects.filter(price__gte=1000)
    context = {
        "title": "20 most Expensive products",
        "heading": "20 most Expensive products",
        "pricey_products": products,
    }
    return render(request, "most_expensive_report.html", context)
