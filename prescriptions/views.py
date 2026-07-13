from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from notifications.utils import create_notification
from appointments.models import Appointment
from .forms import PrescriptionForm, PrescriptionMedicineFormSet, PrescriptionSearchForm
from .models import Prescription
from utils.email_client import send_email


def _is_staff(user):
    return user.is_staff


def _is_doctor(user):
    return hasattr(user, "doctor")


def _is_patient(user):
    return hasattr(user, "patient")


def _can_view_prescription(user, prescription):
    if _is_staff(user):
        return True
    if _is_doctor(user) and prescription.appointment.slot.doctor_id == user.doctor.id:
        return True
    if _is_patient(user) and prescription.appointment.patient_id == user.patient.id:
        return True
    return False


@login_required
def prescription_list(request):
    user = request.user

    prescriptions = Prescription.objects.select_related(
        "appointment__patient__user",
        "appointment__slot__doctor__user",
    ).order_by("-created_at")

    if _is_staff(user):
        pass
    elif _is_doctor(user):
        prescriptions = prescriptions.filter(appointment__slot__doctor=user.doctor)
    elif _is_patient(user):
        prescriptions = prescriptions.filter(appointment__patient=user.patient)
    else:
        prescriptions = Prescription.objects.none()

    form = PrescriptionSearchForm(request.GET or None)

    if form.is_valid():
        patient = form.cleaned_data.get("patient")
        doctor = form.cleaned_data.get("doctor")
        follow_up_required = form.cleaned_data.get("follow_up_required")

        if patient:
            prescriptions = prescriptions.filter(
                appointment__patient__user__first_name__icontains=patient
            ) | prescriptions.filter(
                appointment__patient__user__last_name__icontains=patient
            )

        if doctor:
            prescriptions = prescriptions.filter(
                appointment__slot__doctor__user__first_name__icontains=doctor
            ) | prescriptions.filter(
                appointment__slot__doctor__user__last_name__icontains=doctor
            )

        if follow_up_required:
            prescriptions = prescriptions.filter(follow_up_required=True)

    return render(
        request,
        "prescriptions/prescription_list.html",
        {
            "prescriptions": prescriptions.distinct(),
            "form": form,
            "is_doctor": _is_doctor(user),
            "is_patient": _is_patient(user),
            "is_staff": _is_staff(user),
        },
    )


@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            "appointment__patient__user",
            "appointment__slot__doctor__user",
        ).prefetch_related("medicines"),
        pk=pk,
    )

    if not _can_view_prescription(request.user, prescription):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    return render(
        request,
        "prescriptions/prescription_detail.html",
        {
            "prescription": prescription,
            "can_edit": False,
        },
    )


@login_required
@transaction.atomic
def prescription_create(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related("slot__doctor__user", "patient__user"),
        pk=appointment_id,
    )

    if not (_is_doctor(request.user) or _is_staff(request.user)):
        messages.error(request, "Only doctors can create prescriptions.")
        return redirect("accounts:dashboard")

    if _is_doctor(request.user) and appointment.slot.doctor_id != request.user.doctor.id:
        messages.error(request, "You can only prescribe for your own appointments.")
        return redirect("accounts:dashboard")

    if hasattr(appointment, "prescription"):
        messages.warning(request, "This appointment already has a prescription.")
        return redirect("prescriptions:prescription_detail", pk=appointment.prescription.pk)

    if appointment.status != Appointment.Status.COMPLETED:
        messages.error(
            request, "A prescription can only be created for a completed appointment."
        )
        return redirect("appointments:appointment_detail", pk=appointment.pk)

    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        formset = PrescriptionMedicineFormSet(
            request.POST, instance=Prescription(appointment=appointment)
        )

        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.save()

            formset.instance = prescription
            formset.save()
            create_notification(user=appointment.patient.user,title="Prescription Ready",message="Your doctor has uploaded your prescription.",url=f"/prescriptions/{prescription.pk}/",)
            transaction.on_commit(
                lambda: send_email(
                    trigger="PRESCRIPTION_CREATED",
                    email=appointment.patient.user.email,
                    subject="Your Prescription is Ready",
                    patient=appointment.patient.user.get_full_name(),
                    doctor=appointment.slot.doctor.user.get_full_name(),
    )
)

            messages.success(
                request,
                "Prescription created successfully. It is now locked and cannot be edited or deleted."
            )
            return redirect("prescriptions:prescription_detail", pk=prescription.pk)
    else:
        form = PrescriptionForm()
        formset = PrescriptionMedicineFormSet(instance=Prescription(appointment=appointment))

    return render(
        request,
        "prescriptions/prescription_form.html",
        {
            "form": form,
            "formset": formset,
            "appointment": appointment,
            "is_create": True,
        },
    )


@login_required
def prescription_update(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    if not _can_view_prescription(request.user, prescription):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    messages.error(request, "This prescription is locked and cannot be edited.")
    return redirect("prescriptions:prescription_detail", pk=prescription.pk)


@login_required
def prescription_delete(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    if not _can_view_prescription(request.user, prescription):
        messages.error(request, "Access denied.")
        return redirect("accounts:dashboard")

    messages.error(request, "This prescription is locked and cannot be deleted.")
    return redirect("prescriptions:prescription_detail", pk=prescription.pk)