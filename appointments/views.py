from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from .forms import AppointmentForm, AppointmentSearchForm, AppointmentStatusForm
from .models import Appointment
from doctors.models import Doctor, DoctorSlot

from utils.email_client import send_email
from utils.google_calendar import create_appointment_events


# ==========================================================
# HELPERS
# ==========================================================
def _is_staff(user):
    return user.is_staff


def _is_doctor(user):
    return hasattr(user, "doctor")


def _is_patient(user):
    return hasattr(user, "patient")


def _can_access_appointment(user, appointment):
    if _is_staff(user):
        return True
    if _is_doctor(user) and appointment.slot.doctor_id == user.doctor.id:
        return True
    if _is_patient(user) and appointment.patient_id == user.patient.id:
        return True
    return False


def _can_modify_status(user, appointment):
    if _is_staff(user):
        return True
    if _is_doctor(user) and appointment.slot.doctor_id == user.doctor.id:
        return True
    return False


def _can_cancel_appointment(user, appointment):
    if _is_staff(user):
        return True
    if _is_doctor(user) and appointment.slot.doctor_id == user.doctor.id:
        return True
    if _is_patient(user) and appointment.patient_id == user.patient.id:
        return True
    return False


# NOTE: capacity and double-booking checks now live entirely on
# DoctorSlot.available_times() / is_full (see doctors/models.py), which is
# the single source of truth for what's bookable. There's no more
# _slot_has_capacity() or _appointment_time_taken() helper here — they
# referenced fields (max_patients) that no longer exist on DoctorSlot.


# ==========================================================
# APPOINTMENT LIST
# ==========================================================
@login_required
def appointment_list(request):
    user = request.user
    appointments = Appointment.objects.select_related(
        "patient__user",
        "slot__doctor__user",
    ).order_by("-appointment_date", "-appointment_time")

    if _is_staff(user):
        pass
    elif _is_doctor(user):
        appointments = appointments.filter(slot__doctor=user.doctor)
    elif _is_patient(user):
        appointments = appointments.filter(patient=user.patient)
    else:
        appointments = Appointment.objects.none()

    form = AppointmentSearchForm(request.GET or None)

    if form.is_valid():
        patient = form.cleaned_data.get("patient")
        doctor = form.cleaned_data.get("doctor")
        appointment_date = form.cleaned_data.get("appointment_date")
        status = form.cleaned_data.get("status")

        if patient:
            appointments = appointments.filter(
                patient__user__first_name__icontains=patient
            )

        if doctor:
            appointments = appointments.filter(
                slot__doctor__user__first_name__icontains=doctor
            )

        if appointment_date:
            appointments = appointments.filter(
                appointment_date=appointment_date
            )

        if status:
            appointments = appointments.filter(status=status)

    return render(
        request,
        "appointments/list.html",
        {
            "appointments": appointments,
            "form": form,
        },
    )


# ==========================================================
# BOOK APPOINTMENT
# ==========================================================
@login_required
@transaction.atomic
def book_appointment_form(request, doctor_id):
    doctor = get_object_or_404(
        Doctor.objects.select_related("user"),
        pk=doctor_id,
    )

    if not _is_patient(request.user):
        messages.error(request, "Only patients can book appointments.")
        return redirect("accounts:dashboard")

    patient = request.user.patient

    if request.method == "POST":
        form = AppointmentForm(request.POST, doctor=doctor)

        if form.is_valid():
            slot = get_object_or_404(
                DoctorSlot.objects.select_for_update().select_related(
                    "doctor__user"
                ),
                pk=form.cleaned_data["slot"].pk,
                doctor=doctor,
                is_active=True,
            )

            appointment_date = slot.date
            appointment_time = form.cleaned_data["appointment_time"]

            if slot.current_status != "Available":
                form.add_error(
                    "slot",
                    f"This session is {slot.current_status.lower()}."
                )

            elif not (slot.start_time <= appointment_time < slot.end_time):
                form.add_error(
                    "appointment_time",
                    (
                        f"Please select a time between "
                        f"{slot.start_time.strftime('%I:%M %p')} and "
                        f"{slot.end_time.strftime('%I:%M %p')}."
                    ),
                )

            elif appointment_time not in slot.available_times():
                form.add_error(
                    "appointment_time",
                    "That time is no longer available. Please choose another.",
                )

            else:
                appointment = Appointment.objects.create(patient=patient,slot=slot,appointment_date=appointment_date,appointment_time=appointment_time,reason=form.cleaned_data["reason"],status=Appointment.Status.PENDING,)
                try:
                    create_appointment_events(appointment)
                except Exception as e:
                    print("Calendar error:", e)
                
                try:
                    transaction.on_commit(lambda: send_email(trigger="BOOKING_CONFIRMATION",email=patient.user.email,subject="Appointment Confirmed",patient=patient.user.get_full_name(),doctor=doctor.user.get_full_name(),date=appointment.appointment_date.strftime("%d %b %Y"),time=appointment.appointment_time.strftime("%I:%M %p"),))
                except Exception as e:
                    print("Email error:", e)

                messages.success(
                    request,
                    "Appointment booked successfully."
                )

                return redirect("appointments:my_appointments")

    else:
        form = AppointmentForm(doctor=doctor)

    return render(
        request,
        "appointments/book.html",
        {
            "doctor": doctor,
            "patient": patient,
            "form": form,
        },
    )


# ==========================================================
# APPOINTMENT DETAIL
# ==========================================================
@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient__user",
            "slot__doctor__user",
        ),
        pk=pk,
    )

    if not _can_access_appointment(request.user, appointment):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    return render(
        request,
        "appointments/detail.html",
        {"appointment": appointment},
    )


# ==========================================================
# UPDATE STATUS
# ==========================================================
@login_required
def update_status(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related("slot__doctor", "patient__user"),
        pk=pk,
    )

    if not _can_modify_status(request.user, appointment):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    form = AppointmentStatusForm(request.POST or None, instance=appointment)

    if request.method == "POST" and form.is_valid():
        form.save()
        appointment.refresh_from_db()
        if appointment.status == Appointment.Status.COMPLETED:
            transaction.on_commit(
                lambda: send_email(
                    trigger="APPOINTMENT_COMPLETED",
                    email=appointment.patient.user.email,
                    subject="Appointment Completed",
                    patient=appointment.patient.user.get_full_name(),
                    doctor=appointment.slot.doctor.user.get_full_name(),
                    date=appointment.appointment_date.strftime("%d %b %Y"),
                    time=appointment.appointment_time.strftime("%I:%M %p"),))
        messages.success(request, "Appointment updated.")
        return redirect("appointments:appointment_detail", pk=appointment.pk)

    return render(
        request,
        "appointments/status_form.html",
        {
            "form": form,
            "appointment": appointment,
        },
    )


# ==========================================================
# CANCEL APPOINTMENT
# ==========================================================
@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related("slot__doctor", "patient__user"),
        pk=pk,
    )

    if not _can_cancel_appointment(request.user, appointment):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status"])
        transaction.on_commit(
            lambda: send_email(
                trigger="APPOINTMENT_CANCELLED",
                email=appointment.patient.user.email,
                subject="Appointment Cancelled",
                patient=appointment.patient.user.get_full_name(),
                doctor=appointment.slot.doctor.user.get_full_name(),
                date=appointment.appointment_date.strftime("%d %b %Y"),
                time=appointment.appointment_time.strftime("%I:%M %p"),
                )
                )
        messages.success(request, "Appointment cancelled.")
        return redirect("appointments:appointment_detail", pk=appointment.pk)

    return render(
        request,
        "appointments/cancel_appointement.html",
        {"appointment": appointment},
    )


# ==========================================================
# DELETE APPOINTMENT
# ==========================================================
@login_required
def delete_appointment(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related("slot__doctor", "patient__user"),
        pk=pk,
    )

    if not _can_cancel_appointment(request.user, appointment):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted.")
        return redirect("appointments:appointment_list")

    return render(
        request,
        "appointments/delete_appointment.html",
        {"appointment": appointment},
    )


# ==========================================================
# DOCTOR QUEUE
# ==========================================================
@login_required
def doctor_queue(request):
    if not _is_doctor(request.user):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    appointments = Appointment.objects.filter(
        slot__doctor=request.user.doctor
    ).select_related(
        "patient__user",
        "slot__doctor__user",
    ).order_by("appointment_date", "appointment_time")

    return render(
        request,
        "appointments/doctor_queue.html",
        {"appointments": appointments},
    )


# ==========================================================
# PATIENT APPOINTMENTS
# ==========================================================
@login_required
def my_appointments(request):
    if not _is_patient(request.user):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    appointments = request.user.patient.appointments.select_related(
        "slot__doctor__user"
    ).all().order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": appointments},
    )


# ==========================================================
# TODAY'S APPOINTMENTS
# ==========================================================
@login_required
def today_appointments(request):
    if not _is_doctor(request.user):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    appointments = Appointment.objects.filter(
        slot__doctor=request.user.doctor,
        appointment_date=date.today(),
    ).select_related(
        "patient__user",
        "slot__doctor__user",
    ).order_by("appointment_time")

    return render(
        request,
        "appointments/today_appointments.html",
        {"appointments": appointments},
    )


# ==========================================================
# AJAX: DOCTOR SLOTS BY DATE
# ==========================================================
@login_required
def doctor_slots_ajax(request, doctor_id):

    doctor = get_object_or_404(Doctor, pk=doctor_id)

    selected_date = parse_date(request.GET.get("date"))

    slots = doctor.slots.filter(
        is_active=True
    ).order_by("start_time")

    if selected_date:
        slots = slots.filter(date=selected_date)

    data = {
        "slots": []
    }

    for slot in slots:

        # Skip expired, full, or inactive sessions
        if slot.current_status != "Available":
            continue

        # Reuse the model's own time-generation logic instead of
        # duplicating the consultation/buffer math here.
        times = [
            {
                "value": t.strftime("%H:%M"),
                "label": t.strftime("%I:%M %p"),
            }
            for t in slot.available_times()
        ]

        data["slots"].append(
            {
                "id": str(slot.id),
                "date": slot.date.strftime("%Y-%m-%d"),
                "start_time": slot.start_time.strftime("%I:%M %p"),
                "end_time": slot.end_time.strftime("%I:%M %p"),
                "times": times,
            }
        )

    return JsonResponse(data)


# ==========================================================
# PRESCRIPTION-RELATED VIEWS UNCHANGED — see doctors/views.py
# ==========================================================