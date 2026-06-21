from django.contrib import admin
from .models import Product, Order, RefundReQuest


admin.site.register(Product)
admin.site.register(Order)
admin.site.register(RefundReQuest)
