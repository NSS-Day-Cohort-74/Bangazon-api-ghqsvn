
from django.db import models


class StoreProduct(models.Model):
    product = models.ForeignKey("Product",
                                on_delete=models.DO_NOTHING,
                                related_name="storeproduct")
    store = models.ForeignKey("Store",
                                on_delete=models.DO_NOTHING,
                                related_name="store")
    created_on = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)
