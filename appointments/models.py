import uuid

from django.db import models
from django.core.exceptions import ValidationError

from doctors.models import DoctorSlot
from patients.models import Patient


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        CONFIRMED = "Confirmed", "Confirmed"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
        MISSED = "Missed", "Missed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    appointment_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    slot = models.ForeignKey(
        DoctorSlot,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    notes = models.TextField(
        blank=True
    )

    cancellation_reason = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-appointment_date", "-created_at"]

        constraints = [
            # IMPORTANT: `slot` is now a whole working session (e.g. 9am-1pm),
            # not a single appointment. Many different appointment_times can
            # be booked against the same slot on the same day, so the
            # uniqueness must include appointment_time — otherwise only one
            # patient could ever book a given session per day.
            models.UniqueConstraint(
                fields=[
                    "slot",
                    "appointment_date",
                    "appointment_time",
                ],
                name="unique_slot_time_per_day"
            )
        ]

    def clean(self):
        super().clean()

        if not self.slot_id or not self.appointment_date:
            return
        if self.slot.date != self.appointment_date:
            raise ValidationError("Selected slot does not match the appointment date.")

    @property
    def doctor(self):
        return self.slot.doctor

    def save(self, *args, **kwargs):

        if not self.appointment_number:

            last = Appointment.objects.count() + 1

            self.appointment_number = (
                f"APT-{self.appointment_date.strftime('%Y%m%d')}-{last:04d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.appointment_number