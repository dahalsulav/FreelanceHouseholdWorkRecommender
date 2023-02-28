from django.db import models
from users.models import Customer, Worker


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="tasks"
    )
    worker = models.ForeignKey(
        Worker, on_delete=models.SET_NULL, related_name="tasks", null=True, blank=True
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("in-progress", "In Progress"),
            ("completed", "Completed"),
            ("rejected", "Rejected"),
        ],
    )
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
