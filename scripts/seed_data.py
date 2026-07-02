import os
import uuid
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hms.settings")
django.setup()

from django.utils import timezone

from django.contrib.auth.models import User
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from doctors.models import DoctorSlot

try:
    from prescriptions.models import Prescription
except Exception:
    Prescription = None


def get_attr_if_exists(obj, attr, default=None):
    return getattr(obj, attr, default)


def create_base_users():
    doctor_user, _ = User.objects.get_or_create(
        username="seed_doctor",
        defaults={
            "first_name": "Seed",
            "last_name": "Doctor",
            "email": "seed_doctor@example.com",
        },
    )
    if not doctor_user.check_password("Seed@12345"):
        doctor_user.set_password("Seed@12345")
        doctor_user.save()

    patient_user, _ = User.objects.get_or_create(
        username="seed_patient",
        defaults={
            "first_name": "Seed",
            "last_name": "Patient",
            "email": "seed_patient@example.com",
        },
    )
    if not patient_user.check_password("Seed@12345"):
        patient_user.set_password("Seed@12345")
        patient_user.save()

    doctor_defaults = {}
    if hasattr(Doctor, "specialization"):
        doctor_defaults["specialization"] = "General Physician"
    if hasattr(Doctor, "qualification"):
        doctor_defaults["qualification"] = "MBBS"
    if hasattr(Doctor, "experience_years"):
        doctor_defaults["experience_years"] = 4
    if hasattr(Doctor, "phone"):
        doctor_defaults["phone"] = "9999999991"

    patient_defaults = {}
    if hasattr(Patient, "phone"):
        patient_defaults["phone"] = "9999999992"
    if hasattr(Patient, "gender"):
        patient_defaults["gender"] = "male"
    if hasattr(Patient, "address"):
        patient_defaults["address"] = "Sample Address"

    doctor, _ = Doctor.objects.get_or_create(user=doctor_user, defaults=doctor_defaults)
    patient, _ = Patient.objects.get_or_create(user=patient_user, defaults=patient_defaults)

    return doctor, patient

from datetime import time

def create_slots(doctor):
    slots = []

    days = [
        DoctorSlot.WeekDay.MONDAY,
        DoctorSlot.WeekDay.TUESDAY,
        DoctorSlot.WeekDay.WEDNESDAY,
    ]

    for i, day in enumerate(days):
        slot, _ = DoctorSlot.objects.get_or_create(
            doctor=doctor,
            day=day,
            start_time=time(10 + i, 0),
            end_time=time(11 + i, 0),
            defaults={
                "max_patients": 5,
                "is_active": True,
            },
        )

        slots.append(slot)

    print(f"Prepared {len(slots)} slots.")
    return slots

def create_appointments(patient, slots):
    appointments = []

    today = timezone.localdate()

    weekday_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    for slot in slots:
        target = weekday_map[slot.day]

        days = (target - today.weekday()) % 7

        appointment_date = today + timedelta(days=days)

        appointment, _ = Appointment.objects.get_or_create(
            slot=slot,
            appointment_date=appointment_date,
            defaults={
                "patient": patient,
                "reason": "General Checkup",
                "status": Appointment.Status.CONFIRMED,
                "notes": "Seeded Appointment",
            },
        )

        appointments.append(appointment)

    print(f"Prepared {len(appointments)} appointments.")
    return appointments

def create_prescriptions(appointments):
    if Prescription is None:
        print("Prescription model not found, skipping prescriptions.")
        return

    for appointment in appointments:
        defaults = {}

        if hasattr(Prescription, "appointment"):
            defaults["appointment"] = appointment
        if hasattr(Prescription, "diagnosis"):
            defaults["diagnosis"] = "Mild fever and weakness"
        if hasattr(Prescription, "advice"):
            defaults["advice"] = "Drink water, take rest, and follow medication."
        if hasattr(Prescription, "follow_up_required"):
            defaults["follow_up_required"] = True
        if hasattr(Prescription, "follow_up_date"):
            defaults["follow_up_date"] = timezone.localdate() + timedelta(days=7)

        lookup = {}
        if hasattr(Prescription, "appointment"):
            lookup["appointment"] = appointment
        else:
            continue

        Prescription.objects.get_or_create(**lookup, defaults=defaults)

    print("Prepared prescriptions.")


def main():
    print("Seeding data...")
    doctor, patient = create_base_users()
    slots = create_slots(doctor)
    appointments = create_appointments(patient, slots)
    create_prescriptions(appointments)
    print("Seed data completed successfully.")


if __name__ == "__main__":
    main()