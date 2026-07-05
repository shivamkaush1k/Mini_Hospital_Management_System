import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment


class Prescription(models.Model):
    """
    Issued by a doctor for a single completed appointment.

    Once created, a prescription becomes immutable:
    - cannot be edited
    - cannot be deleted
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="prescription",
    )

    diagnosis = models.TextField(help_text="Diagnosis made by the doctor.")
    advice = models.TextField(blank=True, help_text="General advice for the patient.")

    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"

    def __str__(self):
        return f"Prescription for {self.patient} ({self.created_at:%Y-%m-%d})"

    @property
    def patient(self):
        return self.appointment.patient

    @property
    def doctor(self):
        return self.appointment.slot.doctor

    def clean(self):
        super().clean()

        if self.appointment_id and self.appointment.status != Appointment.Status.COMPLETED:
            raise ValidationError(
                "A prescription can only be created for a completed appointment."
            )

        if self.follow_up_required and not self.follow_up_date:
            raise ValidationError(
                {"follow_up_date": "Follow-up date is required when follow-up is marked as required."}
            )

        if self.follow_up_date and self.follow_up_date < timezone.localdate():
            raise ValidationError({"follow_up_date": "Follow-up date cannot be before today."})

    def save(self, *args, **kwargs):
        if self.pk and Prescription.objects.filter(pk=self.pk).exists():
            raise ValidationError("Saved prescriptions cannot be edited.")
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Saved prescriptions cannot be deleted.")

    def get_absolute_url(self):
        return reverse("prescriptions:prescription_detail", kwargs={"pk": self.pk})


class PrescriptionMedicine(models.Model):
    """A single medicine line item within a prescription."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medicines",
    )

    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg")
    frequency = models.CharField(max_length=100, help_text="e.g. Twice a day")
    duration = models.CharField(max_length=100, help_text="e.g. 5 days")
    instructions = models.TextField(blank=True, help_text="e.g. After food")

    class Meta:
        ordering = ["name"]
        verbose_name = "Prescribed Medicine"
        verbose_name_plural = "Prescribed Medicines"

    def __str__(self):
        return f"{self.name} ({self.dosage})"

    def save(self, *args, **kwargs):
        if self.pk and PrescriptionMedicine.objects.filter(pk=self.pk).exists():
            raise ValidationError("Medicines of a saved prescription cannot be edited.")

        if self.prescription_id and Prescription.objects.filter(pk=self.prescription_id).exists():
            if self.prescription.created_at:
                if self.pk is None and self.prescription.medicines.exists():
                    raise ValidationError("You cannot add medicines after the prescription is saved.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Medicines of a saved prescription cannot be deleted.")