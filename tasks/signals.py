from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task


@receiver(post_save, sender=Task)
def send_notifications(sender, instance, created, **kwargs):
    """
    Sends notifications to the customer and worker when a task is created and saved.
    """
    if created:
        # Send task request notification to worker
        worker = instance.worker
        subject = "New task request"
        message = (
            f"You have a new task request from {instance.customer} for {instance.task}"
        )
        worker.email_user(subject, message)

        # Check worker availability based on customer date and time selection
        if (
            instance.date < worker.unavailability_start
            or instance.date > worker.unavailability_end
        ):
            # Send notification to worker that they are unavailable
            subject = "Task request declined"
            message = (
                f"You have declined the task request from {instance.customer} for {instance.task} "
                f"because you are not available on the selected date and time."
            )
            worker.email_user(subject, message)
            instance.worker = None
            instance.status = "rejected"
            instance.save()
        else:
            # Send notification to customer that task request has been accepted
            subject = "Task request accepted"
            message = (
                f"Your task request for {instance.task} has been accepted by {worker}."
            )
            instance.customer.email_user(subject, message)

    elif not instance.accepted:
        # Send task acceptance/rejection notification to customer
        subject = "Task request status update"
        if instance.status == "accepted":
            message = f"Your task request for {instance.task} has been accepted by {instance.worker}."
        else:
            message = f"Your task request for {instance.task} has been declined by {instance.worker}."
        instance.customer.email_user(subject, message)
