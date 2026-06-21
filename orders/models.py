from django.db import models
from django.contrib.auth.models import User 

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    category = models.CharField(max_length=100)
    in_stock = models.BooleanField(default=True)


class Order(models.Model):

    STATUC_CHOICES = [
        ("pending" , "Pening"),
        ("dispatched" , "Dispatched"),
        ("delivered" , "Delivered"),
        ("cancalled" , "Cancelled"),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True, related_name='oreders')
    product_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUC_CHOICES, default="pending")
    carrier = models.CharField(max_length=100, blank=True)
    delivery = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product_name} ({self.status})"
    
    
class RefundReQuest(models.Model):
    STATUS_CHOICES = [
        ("pending" , "Pending"),
        ("approved" , "Approved"),
        ("delivered" , "Delivered"),
    ]

    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Refund for Order #{self.order.id} - {self.status}"