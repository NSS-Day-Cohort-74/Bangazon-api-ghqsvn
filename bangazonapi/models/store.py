from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE
from bangazonapi.models import Customer


class Store(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    name = models.CharField(max_length=120)
    description = models.TextField()
    seller = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="storeseller"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def product_count(self):
        return len(Products.objects.filter())
