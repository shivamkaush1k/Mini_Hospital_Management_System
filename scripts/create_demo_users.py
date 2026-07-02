import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hms.settings")

import django
django.setup()

from django.contrib.auth.models import User

from accounts.models import Profile
from doctors.models import Doctor
from patients.models import Patient

PASSWORD = "Demo@12345"


def create_user(username, first, last, email):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first,
            "last_name": last,
            "email": email,
        },
    )

    if created:
        user.set_password(PASSWORD)
        user.save()

    return user


# ---------------- ADMIN ----------------

admin = create_user(
    "admin",
    "System",
    "Admin",
    "admin@example.com",
)

admin.is_staff = True
admin.is_superuser = True
admin.save()

Profile.objects.get_or_create(
    user=admin,
    defaults={
        "role": Profile.Role.ADMIN,
    },
)

print("Admin Ready")


# ---------------- DOCTOR 1 ----------------

u = create_user(
    "doctor1",
    "Amit",
    "Sharma",
    "doctor1@example.com",
)

Profile.objects.get_or_create(
    user=u,
    defaults={
        "role": Profile.Role.DOCTOR,
        "phone": "9876543210",
        "gender": Profile.Gender.MALE,
        "city": "Noida",
        "state": "Uttar Pradesh",
    },
)

Doctor.objects.get_or_create(
    user=u,
    defaults={
        "specialization": Doctor.Specialization.CARDIOLOGY,
        "qualification": "MBBS, MD",
        "experience": 8,
        "consultation_fee": 700,
        "department": "Cardiology",
        "license_number": "DOC1001",
        "room_number": "101",
    },
)

print("Doctor1 Ready")


# ---------------- DOCTOR 2 ----------------

u = create_user(
    "doctor2",
    "Neha",
    "Verma",
    "doctor2@example.com",
)

Profile.objects.get_or_create(
    user=u,
    defaults={
        "role": Profile.Role.DOCTOR,
        "phone": "9876543211",
        "gender": Profile.Gender.FEMALE,
        "city": "Delhi",
        "state": "Delhi",
    },
)

Doctor.objects.get_or_create(
    user=u,
    defaults={
        "specialization": Doctor.Specialization.DERMATOLOGY,
        "qualification": "MBBS, DDVL",
        "experience": 5,
        "consultation_fee": 600,
        "department": "Dermatology",
        "license_number": "DOC1002",
        "room_number": "102",
    },
)

print("Doctor2 Ready")


# ---------------- PATIENT 1 ----------------

u = create_user(
    "patient1",
    "Rahul",
    "Yadav",
    "patient1@example.com",
)

Profile.objects.get_or_create(
    user=u,
    defaults={
        "role": Profile.Role.PATIENT,
        "phone": "9876543220",
        "gender": Profile.Gender.MALE,
        "city": "Dadri",
        "state": "Uttar Pradesh",
    },
)

Patient.objects.get_or_create(
    user=u,
    defaults={
        "blood_group": Patient.BloodGroup.O_POSITIVE,
        "height": 172,
        "weight": 70,
        "allergies": "None",
        "emergency_contact_name": "Ramesh Yadav",
        "emergency_contact_phone": "9999999999",
    },
)

print("Patient1 Ready")


# ---------------- PATIENT 2 ----------------

u = create_user(
    "patient2",
    "Priya",
    "Singh",
    "patient2@example.com",
)

Profile.objects.get_or_create(
    user=u,
    defaults={
        "role": Profile.Role.PATIENT,
        "phone": "9876543221",
        "gender": Profile.Gender.FEMALE,
        "city": "Noida",
        "state": "Uttar Pradesh",
    },
)

Patient.objects.get_or_create(
    user=u,
    defaults={
        "blood_group": Patient.BloodGroup.A_POSITIVE,
        "height": 160,
        "weight": 55,
        "allergies": "Dust",
        "emergency_contact_name": "Anil Singh",
        "emergency_contact_phone": "9999999998",
    },
)

print()
print("================================")
print("Demo data created successfully.")
print("Username examples:")
print("admin")
print("doctor1")
print("doctor2")
print("patient1")
print("patient2")
print()
print(f"Password: {PASSWORD}")
print("================================")