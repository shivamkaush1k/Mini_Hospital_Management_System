from .helpers import (
    is_admin,
    is_doctor,
    is_patient,
)


def can_view_patient(user, patient):

    if is_admin(user):
        return True

    if is_doctor(user):
        return True

    if is_patient(user):
        return patient == user.patient

    return False


def can_manage_prescription(user, prescription):

    if is_admin(user):
        return True

    if is_doctor(user):
        return (
            prescription.appointment.slot.doctor
            == user.doctor
        )

    return False


def can_view_appointment(user, appointment):

    if is_admin(user):
        return True

    if is_doctor(user):
        return (
            appointment.slot.doctor
            == user.doctor
        )

    if is_patient(user):
        return (
            appointment.patient
            == user.patient
        )

    return False