from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.utils.dateparse import parse_date

from .forms import (
    AppointmentForm,
    AppointmentStatusForm,
    AppointmentSearchForm,
)

from .models import Appointment

from doctors.models import Doctor, DoctorSlot
from patients.models import Patient

from utils.email_client import send_email
from utils.google_calendar import create_appointment_events


# =========================
# APPOINTMENT LIST
# =========================
@login_required
def appointment_list(request):

    appointments = (
        Appointment.objects
        .select_related(
            "patient__user",
            "slot__doctor__user",
        )
        .all()
    )

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


# =========================
# BOOK APPOINTMENT (FORM UI)
# =========================
@login_required
def book_appointment_form(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if not hasattr(request.user, "patient"):
        messages.error(request, "Please complete your patient profile first.")
        return redirect("accounts:dashboard")

    if hasattr(request.user, "profile") and request.user.profile.role != "PATIENT":
        messages.error(request, "Only patients can book appointments.")
        return redirect("accounts:dashboard")

    patient = request.user.patient
    form = AppointmentForm(request.POST or None)

    return render(
        request,
        "appointments/book.html",
        {
            "form": form,
            "doctor": doctor,
            "patient": patient,
        },
    )
# =========================
# BOOK APPOINTMENT (API - FINAL CORE LOGIC)
# =========================
@transaction.atomic
@login_required
def book_appointment(request):
    """
    FINAL BOOKING FLOW:
    - race condition safe
    - slot locking
    - calendar integration
    - email trigger
    """

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    # validate patient
    try:
        patient = Patient.objects.select_related("user").get(user=request.user)
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Only patients can book"}, status=403)

    doctor_id = request.POST.get("doctor_id")
    slot_id = request.POST.get("slot_id")

    if not doctor_id or not slot_id:
        return JsonResponse({"error": "Missing data"}, status=400)

    doctor = get_object_or_404(Doctor, id=doctor_id)

    # LOCK SLOT (prevents double booking)
    slot = DoctorSlot.objects.select_for_update().get(
        id=slot_id,
        doctor=doctor
    )

    # validations
    if slot.is_booked:
        return JsonResponse({"error": "Slot already booked"}, status=400)

    if slot.start_time < timezone.now():
        return JsonResponse({"error": "Cannot book past slot"}, status=400)

    # mark slot booked
    slot.is_booked = True
    slot.save()

    # Create appointment.
    # NOTE: Appointment has no direct `doctor` field anywhere else in this
    # codebase — the doctor is always reached via `slot__doctor` (see
    # appointment_list, doctor_queue, today_appointments, etc). Passing
    # doctor=doctor here would raise a TypeError/FieldError since
    # Appointment.objects.create() doesn't accept an unknown kwarg. Removed.
    appointment = Appointment.objects.create(
        patient=patient,
        slot=slot,
        appointment_date=slot.start_time.date(),
    )

    # calendar integration
    try:
        create_appointment_events(appointment)
    except Exception as e:
        print("Calendar error:", e)

    # email notification (serverless)
    try:
        send_email(
            trigger="BOOKING_CONFIRMATION",
            email=patient.user.email,
            subject="Appointment Confirmed",
            patient=patient.user.username,
            doctor=doctor.user.username,
            date=str(slot.start_time.date()),
            time=str(slot.start_time.time())
        )
    except Exception as e:
        print("Email error:", e)

    return JsonResponse({
        "success": True,
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id
    })


# =========================
# APPOINTMENT DETAIL
# =========================
@login_required
def appointment_detail(request, pk):

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient__user",
            "slot__doctor__user",
        ),
        pk=pk,
    )

    return render(
        request,
        "appointments/appointment_detail.html",
        {"appointment": appointment},
    )


# =========================
# UPDATE STATUS
# =========================
@login_required
def update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentStatusForm(request.POST or None, instance=appointment)

    if form.is_valid():
        form.save()
        messages.success(request, "Appointment updated.")
        return redirect("appointments:appointment_detail", pk=appointment.pk)

    return render(request, "appointments/status_form.html", {"form": form, "appointment": appointment})


# =========================
# CANCEL APPOINTMENT
# =========================
@login_required
def cancel_appointment(request, pk):

    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":

        appointment.status = Appointment.Status.CANCELLED
        appointment.save()

        messages.success(request, "Appointment cancelled.")

        # FIX: was redirect("appointment_detail", appointment.pk) — an
        # un-namespaced name with a positional arg. The URLconf used
        # throughout this app is namespaced ("appointments:..."), and
        # appointment_detail expects a `pk` kwarg.
        return redirect("appointments:appointment_detail", pk=appointment.pk)

    return render(
        request,
        "appointments/cancel_appointment.html",
        {"appointment": appointment},
    )


# =========================
# DELETE APPOINTMENT
# =========================
@login_required
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted.")
        return redirect("appointments:appointment_list")

    return render(request, "appointments/delete_appointment.html", {"appointment": appointment})


# =========================
# DOCTOR DASHBOARD QUEUE
# =========================
@login_required
def doctor_queue(request):

    doctor = request.user.doctor

    appointments = Appointment.objects.filter(
        slot__doctor=doctor
    ).select_related("patient__user")

    return render(
        request,
        "appointments/doctor_queue.html",
        {"appointments": appointments},
    )


# =========================
# PATIENT APPOINTMENTS
# =========================
@login_required
def my_appointments(request):

    appointments = request.user.patient.appointments.all()

    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": appointments},
    )


# =========================
# TODAY APPOINTMENTS (DOCTOR)
# =========================
@login_required
def today_appointments(request):

    doctor = request.user.doctor

    appointments = Appointment.objects.filter(
        slot__doctor=doctor,
        appointment_date=date.today(),
    )

    return render(
        request,
        "appointments/today_appointments.html",
        {"appointments": appointments},
    )


@login_required
def doctor_slots_ajax(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)

    selected_date = request.GET.get("date")
    selected_date = parse_date(selected_date) if selected_date else None

    slots = doctor.slots.filter(is_active=True, is_booked=False)

    if selected_date:
        slots = slots.filter(start_time__date=selected_date)

    data = {
        "slots": [
            {
                "id": slot.id,
                "start_time": slot.start_time.strftime("%I:%M %p"),
                "is_available": not slot.is_booked,
            }
            for slot in slots.order_by("start_time")
        ]
    }
    return JsonResponse(data)