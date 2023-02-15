from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(Group, related_name="user+")
    user_permissions = models.ManyToManyField(Permission, related_name="user+")


class Customer(User):
    phone_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Worker(User):
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    skillset = models.CharField()
    hourly_rate = models.FloatField()
    email_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
