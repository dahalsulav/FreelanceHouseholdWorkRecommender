from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(Group, related_name="auth_user_groups")
    user_permissions = models.ManyToManyField(
        Permission, related_name="auth_user_permissions"
    )


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    skillset = models.TextField()
    hourly_rate = models.FloatField()
    email_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
