from django.utils import timezone
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Doctor(models.Model):

    class Specialization(models.TextChoices):
        GENERAL = "General Physician", "General Physician"
        CARDIOLOGY = "Cardiologist", "Cardiologist"
        DERMATOLOGY = "Dermatologist", "Dermatologist"
        ENT = "ENT", "ENT"
        NEUROLOGY = "Neurologist", "Neurologist"
        ORTHOPEDICS = "Orthopedic", "Orthopedic"
        PEDIATRICS = "Pediatrician", "Pediatrician"
        PSYCHIATRY = "Psychiatrist", "Psychiatrist"
        GYNECOLOGY = "Gynecologist", "Gynecologist"
        OPHTHALMOLOGY = "Ophthalmologist", "Ophthalmologist"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor",
    )

    specialization = models.CharField(
        max_length=50,
        choices=Specialization.choices,
    )

    qualification = models.CharField(max_length=150)

    experience = models.PositiveIntegerField(
        help_text="Years of experience"
    )

    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    department = models.CharField(
        max_length=100,
        blank=True,
    )

    license_number = models.CharField(
        max_length=100,
        blank=True,
    )

    room_number = models.CharField(max_length=20)

    bio = models.TextField(blank=True)

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=5.0,
    )

    is_active = models.BooleanField(default=True)

    phone = models.CharField(
        _("Phone Number"),
        max_length=15,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "user__first_name",
            "user__last_name",
        ]

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class DoctorSlot(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="slots",
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    max_patients = models.PositiveIntegerField(
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    is_booked = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "date",
            "start_time",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "date",
                    "start_time",
                    "end_time",
                ],
                name="unique_doctor_slot",
            )
        ]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(
                "End time must be later than start time."
            )

    def __str__(self):
        return (
            f"Dr. {self.doctor.user.get_full_name()} | "
            f"{self.date} | "
            f"{self.start_time.strftime('%H:%M')} - "
            f"{self.end_time.strftime('%H:%M')}"
        )
    @property
    def current_status(self):
        now = timezone.localtime()

        if not self.is_active:
           return "Inactive"

        if self.is_booked:
           return "Booked"

        if self.date < now.date():
           return "Not Available"

        if self.date > now.date():
           return "Available"

        if now.time() > self.end_time:
           return "Not Available"

        return "Available"