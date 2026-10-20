from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):

    phone_number = models.CharField(max_length=12,null=True,blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"

    def __str__(self):
        return self.email