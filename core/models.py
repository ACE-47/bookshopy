from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    objects = CustomUserManager()