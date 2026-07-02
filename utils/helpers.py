from django.utils import timezone


def get_full_name(user):
    if not user:
        return ""
    return user.get_full_name().strip() or user.username


def is_admin(user):
    return (
        user.is_authenticated
        and user.is_staff
    )


def is_doctor(user):
    return (
        user.is_authenticated
        and hasattr(user, "doctor")
    )


def is_patient(user):
    return (
        user.is_authenticated
        and hasattr(user, "patient")
    )


def get_doctor(user):
    if is_doctor(user):
        return user.doctor
    return None


def get_patient(user):
    if is_patient(user):
        return user.patient
    return None


def today():
    return timezone.localdate()