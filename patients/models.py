from django.db import models
from django.contrib.auth.models import User
import uuid
from doctors.models import Doctor


class Patient(models.Model):

    class BloodGroup(models.TextChoices):
        A_POSITIVE = "A+", "A+"
        A_NEGATIVE = "A-", "A-"
        B_POSITIVE = "B+", "B+"
        B_NEGATIVE = "B-", "B-"
        AB_POSITIVE = "AB+", "AB+"
        AB_NEGATIVE = "AB-", "AB-"
        O_POSITIVE = "O+", "O+"
        O_NEGATIVE = "O-", "O-"
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient"
    )

    blood_group = models.CharField(
        max_length=3,
        choices=BloodGroup.choices
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Height in centimeters"
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Weight in kilograms"
    )

    allergies = models.TextField(
        blank=True
    )

    emergency_contact_name = models.CharField(
        max_length=100
    )

    emergency_contact_phone = models.CharField(
        max_length=15
    )

    insurance_provider = models.CharField(
        max_length=100,
        blank=True
    )

    insurance_number = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __str__(self):
        return self.user.get_full_name()
    


class MedicalHistory(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="medical_records"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records"
    )

    diagnosis = models.TextField()

    treatment = models.TextField()

    notes = models.TextField(
        blank=True
    )

    visit_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-visit_date"
        ]

    def __str__(self):
        return (
            f"{self.patient.user.get_full_name()} "
            f"({self.visit_date})"
        )