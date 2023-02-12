from django.db import models
from django.contrib.auth.models import User


class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skillset = models.TextField()
    ratings = models.ManyToManyField(
        User, through="Rating", related_name="worker_ratings"
    )

    def __str__(self):
        return self.user.username


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ratings = models.ManyToManyField(
        User, through="Rating", related_name="customer_ratings"
    )

    def __str__(self):
        return self.user.username


class Rating(models.Model):
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    rating = models.FloatField()

    def __str__(self):
        return f"{self.customer} - {self.worker}: {self.rating}"
