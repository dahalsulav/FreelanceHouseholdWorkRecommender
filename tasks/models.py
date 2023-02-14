from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20)
    customer = models.ForeignKey(
        User, related_name="task_customer", on_delete=models.CASCADE
    )
    worker = models.ForeignKey(
        User,
        related_name="task_worker",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Ratings(models.Model):
    rating = models.FloatField()
    review = models.TextField()
    customer = models.ForeignKey(
        User, related_name="rating_customer", on_delete=models.CASCADE
    )
    worker = models.ForeignKey(
        User, related_name="rating_worker", on_delete=models.CASCADE
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.review
