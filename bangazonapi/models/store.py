
from django.db import models
from .customer import Customer


class Store(models.Model):
    customer = models.ForeignKey(Customer, related_name='store', on_delete=models.CASCADE,)
    created_on = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)
