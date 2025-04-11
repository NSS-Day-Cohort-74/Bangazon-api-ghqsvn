from django.db import models
from .product import Product
from .customer import Customer



class Like(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=True)

    