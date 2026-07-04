from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Patient, MedicalHistory
from .forms import (PatientForm, MedicalHistoryForm, PatientSearchForm,)

from appointments.models import Appointment
from prescriptions.models import Prescription
from accounts.decorators import patient_required


@login_required
def patient_list(request):
    patients = Patient.objects.select_related("user", "user__profile")

    form = PatientSearchForm(request.GET or None)

    if form.is_valid():
        search = form.cleaned_data.get("search")
        blood_group = form.cleaned_data.get("blood_group")
        if search:
            patients = patients.filter(
                user__first_name__icontains=search
            ) | patients.filter(
                user__last_name__icontains=search
            ) | patients.filter(
                user__email__icontains=search
            )

        if blood_group:
            patients = patients.filter(
                blood_group=blood_group
            )

    return render(
        request,
        "patients/patient_list.html",
        {
            "patients": patients,
            "form": form,
        },
    )


@login_required
def patient_detail(request, pk):

    patient = get_object_or_404(
        Patient.objects.select_related(
            "user",
            "user__profile",
        ),
        pk=pk,
    )

    history = patient.medical_records.all()

    appointments = patient.appointments.all()

    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    )

    return render(
        request,
        "patients/patient_detail.html",
        {
            "patient": patient,
            "history": history,
            "appointments": appointments,
            "prescriptions": prescriptions,
        },
    )


@login_required
@patient_required
def patient_dashboard(request):

    patient = request.user.patient

    appointments = patient.appointments.all()

    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    )

    context = {
        "patient": patient,
        "appointments": appointments,
        "prescriptions": prescriptions,
        "appointment_count": appointments.count(),
        "prescription_count": prescriptions.count(),
        "history_count": patient.medical_records.count(),
    }

    return render(
        request,
        "patients/dashboard.html",
        context,
    )


@login_required
@patient_required
def patient_update(request):
    patient = request.user.patient
    form = PatientForm(request.POST or None, instance=patient)

    if form.is_valid():
        form.save()
        messages.success(request, "Patient profile updated successfully.")
        return redirect("patients:dashboard")

    return render(request, "patients/patient_form.html", {"form": form})


@login_required
@patient_required
def medical_history(request):

    patient = request.user.patient

    records = patient.medical_records.all()

    return render(
        request,
        "patients/medical_history.html",
        {
            "records": records,
        },
    )


@login_required
@patient_required
def add_medical_record(request):
    patient = request.user.patient
    form = MedicalHistoryForm(request.POST or None)

    if form.is_valid():
        record = form.save(commit=False)
        record.patient = patient
        record.save()
        messages.success(request, "Medical history added.")
        return redirect("patients:medical_history")

    return render(request, "patients/medical_history_form.html", {"form": form})


@login_required
@patient_required
def edit_medical_record(request, pk):
    record = get_object_or_404(MedicalHistory, pk=pk, patient=request.user.patient)
    form = MedicalHistoryForm(request.POST or None, instance=record)

    if form.is_valid():
        form.save()
        messages.success(request, "Medical history updated.")
        return redirect("patients:medical_history")

    return render(request, "patients/medical_history_form.html", {"form": form, "record": record})


@login_required
@patient_required
def delete_medical_record(request, pk):

    record = get_object_or_404(
        MedicalHistory,
        pk=pk,
        patient=request.user.patient,
    )

    if request.method == "POST":

        record.delete()

        messages.success(
            request,
            "Medical history deleted."
        )

        # FIX: was redirect("medical_history") — un-namespaced, would raise
        # NoReverseMatch given this project's namespaced URLconf.
        return redirect("patients:medical_history")

    return render(
        request,
        "patients/medical_history_confirm_delete.html",
        {
            "record": record,
        },
    )

from django.contrib import messages
from django.shortcuts import redirect




@login_required
def prescription_history(request):

    prescriptions = Prescription.objects.filter(
        appointment__patient=request.user.patient
    )

    return render(
        request,
        "patients/prescription_history.html",
        {
            "prescriptions": prescriptions,
        },
    )

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from appointments.models import Appointment


@login_required
def appointment_history(request):

    if not hasattr(request.user, "patient"):
        messages.error(request, "Only patients can view appointment history.")
        return redirect("accounts:dashboard")

    patient = request.user.patient

    base_qs = patient.appointments.select_related(
        "slot",
        "slot__doctor",
        "slot__doctor__user",
    )

    status = request.GET.get("status", "all")

    appointments = base_qs.order_by("-appointment_date", "-slot__start_time")

    if status == "upcoming":
        # "Upcoming" isn't a stored status value — it means the appointment
        # hasn't been completed or cancelled yet.
        appointments = appointments.filter(
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ]
        )
    elif status == "completed":
        appointments = appointments.filter(status=Appointment.Status.COMPLETED)
    elif status == "cancelled":
        appointments = appointments.filter(status=Appointment.Status.CANCELLED)
    # status == "all" (or anything unrecognized) -> no filter applied

    upcoming_count = base_qs.filter(
        status__in=[
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
        ]
    ).count()

    paginator = Paginator(appointments, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "patients/appointment_history.html",
        {
            "appointments": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
            "upcoming_count": upcoming_count,
        },
    )