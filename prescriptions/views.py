from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from appointments.models import Appointment
from .forms import (
    PrescriptionForm,
    PrescriptionSearchForm,
)
from .models import Prescription

@login_required
def prescription_list(request):

    prescriptions = (
        Prescription.objects
        .select_related(
            "appointment__patient__user",
            "appointment__slot__doctor__user",
        )
        .all()
    )

    form = PrescriptionSearchForm(
        request.GET or None
    )

    if form.is_valid():

        patient = form.cleaned_data.get("patient")
        doctor = form.cleaned_data.get("doctor")
        diagnosis = form.cleaned_data.get("diagnosis")
        from_date = form.cleaned_data.get("from_date")
        to_date = form.cleaned_data.get("to_date")

        if patient:
            prescriptions = prescriptions.filter(
                appointment__patient__user__first_name__icontains=patient
            )

        if doctor:
            prescriptions = prescriptions.filter(
                appointment__slot__doctor__user__first_name__icontains=doctor
            )

        if diagnosis:
            prescriptions = prescriptions.filter(
                diagnosis__icontains=diagnosis
            )

        if from_date:
            prescriptions = prescriptions.filter(
                created_at__date__gte=from_date
            )

        if to_date:
            prescriptions = prescriptions.filter(
                created_at__date__lte=to_date
            )

    context = {
        "prescriptions": prescriptions,
        "form": form,
    }

    return render(
        request,
        "prescriptions/prescription_list.html",
        context,
    )

@login_required
def prescription_detail(request, pk):

    prescription = get_object_or_404(

        Prescription.objects.select_related(

            "appointment__patient__user",

            "appointment__slot__doctor__user",

        ),

        pk=pk,

    )

    return render(

        request,

        "prescriptions/prescription_detail.html",

        {

            "prescription": prescription,

        },

    )

@login_required
def prescription_create(request):
    form = PrescriptionForm(request.POST or None)

    if form.is_valid():
        prescription = form.save()
        messages.success(request, "Prescription created successfully.")
        return redirect("prescriptions:prescription_detail", pk=prescription.pk)

    return render(request, "prescriptions/prescription_form.html", {"form": form})

@login_required
def prescription_update(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    form = PrescriptionForm(request.POST or None, instance=prescription)

    if form.is_valid():
        form.save()
        messages.success(request, "Prescription updated successfully.")
        return redirect("prescriptions:prescription_detail", pk=prescription.pk)

    return render(request, "prescriptions/prescription_form.html", {
        "form": form,
        "prescription": prescription,
    })

@login_required
def prescription_delete(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    if request.method == "POST":
        prescription.delete()
        messages.success(request, "Prescription deleted successfully.")
        return redirect("prescriptions:prescription_list")

    return render(request, "prescriptions/prescription_confirm_delete.html", {
        "prescription": prescription,
    })

@login_required
def my_prescriptions(request):

    patient = request.user.patient

    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).select_related(
        "appointment__slot__doctor__user"
    )

    return render(

        request,

        "prescriptions/my_prescriptions.html",

        {

            "prescriptions": prescriptions,

        },

    )


@login_required
def doctor_prescriptions(request):

    doctor = request.user.doctor

    prescriptions = Prescription.objects.filter(
        appointment__slot__doctor=doctor
    ).select_related(
        "appointment__patient__user"
    )

    return render(

        request,

        "prescriptions/doctor_prescriptions.html",

        {

            "prescriptions": prescriptions,

        },

    )

@login_required
def print_prescription(request, pk):

    prescription = get_object_or_404(

        Prescription.objects.select_related(

            "appointment__patient__user",

            "appointment__slot__doctor__user",

        ),

        pk=pk,

    )

    return render(

        request,

        "prescriptions/print_prescription.html",

        {

            "prescription": prescription,

        },

    )