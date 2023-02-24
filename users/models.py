from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_customer = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="user+")
    user_permissions = models.ManyToManyField(Permission, related_name="user+")

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Customer(User):
    phone_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        self.is_worker = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class Worker(User):
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    skillset = models.CharField(max_length=400)
    hourly_rate = models.FloatField()
    email_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        self.is_customer = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
