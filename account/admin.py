from django.contrib import admin
from .models import CustomUser 


class CustomAdminPanel(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')

admin.site.register(CustomUser,CustomAdminPanel)