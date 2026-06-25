from django.urls import path  
from .views import * 

urlpatterns = [

    path('register_view/',register_view,name='register_view'),
    path('login_view/',login_view,name='login_view'),
    path('logout_view/',logout_view,name='logout')
    
]