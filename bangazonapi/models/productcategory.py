from django.db import models


class ProductCategory(models.Model):

    name = models.CharField(max_length=55)

    class Meta:
        verbose_name = ("productcategory")
        verbose_name_plural = ("productcategories")

    @property
    def last_5(self):
        from .product import Product
        from bangazonapi.views.product import ProductSerializer
        last_5_products = Product.objects.filter(category=self).order_by("created_date")[:5]
        serialzer = ProductSerializer(last_5_products, many=True)
        return serialzer.data