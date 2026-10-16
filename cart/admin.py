from django.contrib import admin

# Register your models here.
from .models import Order, Item, Region
admin.site.register(Order)
admin.site.register(Item)
admin.site.register(Region)

