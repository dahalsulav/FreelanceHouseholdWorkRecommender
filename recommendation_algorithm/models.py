from django.db import models
from django.contrib.auth.models import User


class Skillset(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class WorkerSkillset(models.Model):
    worker = models.ForeignKey(
        User, related_name="worker_skillset", on_delete=models.CASCADE
    )
    skillset = models.ForeignKey(Skillset, on_delete=models.CASCADE)


class Ratings(models.Model):
    rating = models.FloatField()
    review = models.TextField()
    customer = models.ForeignKey(
        User, related_name="rating_customer", on_delete=models.CASCADE
    )
    worker = models.ForeignKey(
        User, related_name="rating_worker", on_delete=models.CASCADE
    )
    task = models.ForeignKey("Task", on_delete=models.CASCADE)

    def __str__(self):
        return self.review


class Recommendation(models.Model):
    worker = models.ForeignKey(
        User, related_name="worker_recommendation", on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        "Task", related_name="task_recommendation", on_delete=models.CASCADE
    )
    score = models.FloatField()

    def __str__(self):
        return f"{self.worker.username} for task {self.task.name}"
