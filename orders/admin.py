from django.contrib import admin
from .models import Product, Order, RefundReQuest

class ProductAdminPanel(admin.ModelAdmin):
    list_display = ('name','description','price', 'category', 'in_stock')

class OrderAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'product', 'delivery', 'status')

class RefundAdminpanel(admin.ModelAdmin):
    list_display = ('user','order','reason', 'STATUS_CHOICES', 'status')

admin.site.register(Product,ProductAdminPanel)
admin.site.register(Order,OrderAdminPanel)
admin.site.register(RefundReQuest,RefundAdminpanel)
