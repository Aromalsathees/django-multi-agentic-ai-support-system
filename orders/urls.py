from django.urls import path
from . import views

urlpatterns = [
    path('', views.orders_list, name='orders_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
]