import uuid
from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )


    class Type(models.TextChoices):
        APPOINTMENT = "APPOINTMENT", "Appointment"
        PRESCRIPTION = "PRESCRIPTION", "Prescription"
        GENERAL = "GENERAL", "General"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.GENERAL,
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title