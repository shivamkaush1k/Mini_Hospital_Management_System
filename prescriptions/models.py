import uuid

from django.db import models

from appointments.models import Appointment


class Prescription(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="prescription"
    )

    diagnosis = models.TextField()

    advice = models.TextField(blank=True)

    follow_up_required = models.BooleanField(default=False)

    follow_up_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def doctor(self):
        return self.appointment.slot.doctor

    @property
    def patient(self):
        return self.appointment.patient

    def __str__(self):
        return f"Prescription - {self.appointment.appointment_number}"
    

class PrescriptionMedicine(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medicines"
    )

    name = models.CharField(max_length=255)

    dosage = models.CharField(max_length=255)

    frequency = models.CharField(max_length=255)

    duration = models.CharField(max_length=255)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"