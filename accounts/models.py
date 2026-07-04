from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        OTHER = "Other", "Other"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )

    image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(blank=True)

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')],blank=True)
    pincode = models.CharField(max_length=6,validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit PIN code.')],blank=True)


    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def age(self):
        from datetime import date

        if not self.date_of_birth:
            return None

        today = date.today()

        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                <
                (
                    self.date_of_birth.month,
                    self.date_of_birth.day
                )
            )
        )

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    