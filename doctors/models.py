from datetime import datetime, timedelta
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

    # Duration of one consultation (minutes)
    consultation_duration = models.PositiveIntegerField(
        default=10,
        help_text="Consultation duration in minutes."
    )

    # Gap after each consultation (minutes)
    buffer_duration = models.PositiveIntegerField(
        default=5,
        help_text="Buffer time between appointments."
    )

    is_active = models.BooleanField(
        default=True
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

        if self.consultation_duration <= 0:
            raise ValidationError(
                "Consultation duration must be greater than zero."
            )

        if self.buffer_duration < 0:
            raise ValidationError(
                "Buffer duration cannot be negative."
            )

    def __str__(self):

        return (
            f"Dr. {self.doctor.user.get_full_name()} | "
            f"{self.date} | "
            f"{self.start_time.strftime('%I:%M %p')} - "
            f"{self.end_time.strftime('%I:%M %p')}"
        )

    @property
    def slot_interval(self):
        """
        Total minutes occupied by one patient.
        """
        return self.consultation_duration + self.buffer_duration

    def generated_times(self):
        """
        Generate every appointment start time.
        Example:
        09:00
        09:15
        09:30
        ...
        """

        start = datetime.combine(
            self.date,
            self.start_time,
        )

        end = datetime.combine(
            self.date,
            self.end_time,
        )

        current = start

        times = []

        while True:

            consultation_end = (
                current +
                timedelta(
                    minutes=self.consultation_duration
                )
            )

            if consultation_end > end:
                break

            times.append(current.time())

            current = (
                consultation_end +
                timedelta(
                    minutes=self.buffer_duration
                )
            )

        return times

    def booked_times(self):
        """
        Return all booked appointment times.
        """

        from appointments.models import Appointment

        return set(

            Appointment.objects.filter(
                slot=self,
                status__in=[
                    Appointment.Status.PENDING,
                    Appointment.Status.CONFIRMED,
                ],
            ).values_list(
                "appointment_time",
                flat=True,
            )

        )

    def available_times(self):
        """
        Return only available appointment times.
        """

        booked = self.booked_times()

        return [

            time

            for time in self.generated_times()

            if time not in booked

        ]

    @property
    def total_slots(self):
        """
        Total appointment slots generated.
        """

        return len(self.generated_times())

    @property
    def booked_slots(self):
        """
        Number of booked appointments.
        """

        return len(self.booked_times())

    @property
    def available_slots(self):
        """
        Number of remaining appointments.
        """

        return len(self.available_times())

    @property
    def is_full(self):
        """
        True when no appointment times remain.
        """

        return self.available_slots == 0

    @property
    def current_status(self):

        now = timezone.localtime()

        if not self.is_active:
            return "Inactive"

        if self.date < now.date():
            return "Expired"

        if self.date == now.date() and now.time() > self.end_time:
            return "Expired"

        if self.is_full:
            return "Full"

        return "Available"
