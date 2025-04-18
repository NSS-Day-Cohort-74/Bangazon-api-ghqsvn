from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Customer)
admin.site.register(Favorite)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductRating)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Like)
admin.site.register(Recommendation)
admin.site.register(Report)
