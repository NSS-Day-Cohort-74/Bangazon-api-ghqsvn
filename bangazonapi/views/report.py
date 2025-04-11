from django.contrib.auth.decorators import login_required
from bangazonapi.models.product import Product
from django.shortcuts import render

from django.urls import reverse


@login_required(login_url="reports_login")
def report(request):
    if request.path == "/reports/expensiveproducts":
        products = Product.objects.filter(price__gte=1000)
        context = {
            "title": "20 most Expensive products",
            "heading": "20 most Expensive products",
            "pricey_products": products,
        }
        return render(request, "report.html", context)
    elif request.path == "/reports/inexpensiveproducts":
        products = Product.objects.filter(price__lte=999)
        context = {
            "title": "Least Expensive products",
            "heading": "Least Expensive products",
            "pricey_products": products,
        }
        return render(request, "report.html", context)
