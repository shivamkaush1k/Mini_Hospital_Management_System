from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from appointments.models import Appointment

from .forms import (
    DoctorForm,
    DoctorSearchForm,
    DoctorSlotForm,
)

from .models import (
    Doctor,
    DoctorSlot,
)


@login_required
def doctor_list(request):

    doctors = Doctor.objects.select_related(
        "user",
        "user__profile",
    ).all()

    form = DoctorSearchForm(
        request.GET or None
    )

    if form.is_valid():

        specialization = form.cleaned_data.get("specialization")
        department = form.cleaned_data.get("department")
        experience = form.cleaned_data.get("min_experience")
        fee = form.cleaned_data.get("max_fee")
        available = form.cleaned_data.get("available_only")

        if specialization:
            doctors = doctors.filter(specialization=specialization)

        if department:
            doctors = doctors.filter(department__icontains=department)

        if experience:
            doctors = doctors.filter(experience__gte=experience)

        if fee:
            doctors = doctors.filter(consultation_fee__lte=fee)

        if available:
            doctors = doctors.filter(is_active=True)

    return render(
        request,
        "doctors/doctors_list.html",
        {
            "form": form,
            "doctors": doctors,
        }
    )


@login_required
def doctor_detail(request, pk):

    doctor = get_object_or_404(
        Doctor.objects.select_related(
            "user",
            "user__profile",
        ),
        pk=pk,
    )

    slots = doctor.slots.filter(is_active=True)

    appointments = Appointment.objects.filter(slot__doctor=doctor)

    return render(
        request,
        "doctors/doctor_detail.html",
        {
            "doctor": doctor,
            "slots": slots,
            "appointments": appointments,
        }
    )


@login_required
def doctor_create(request):
    form = DoctorForm(request.POST or None)

    if form.is_valid():
        doctor = form.save(commit=False)
        doctor.user = request.user
        doctor.save()
        messages.success(request, "Doctor profile created successfully.")
        return redirect("doctors:doctor_detail", pk=doctor.pk)

    return render(request, "doctors/doctor_form.html", {"form": form})


@login_required
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)

    if form.is_valid():
        form.save()
        messages.success(request, "Doctor updated successfully.")
        return redirect("doctors:doctor_detail", pk=doctor.pk)

    return render(request, "doctors/doctor_form.html", {"form": form, "doctor": doctor})


@login_required
def doctor_delete(request, pk):

    doctor = get_object_or_404(Doctor, pk=pk)

    if request.method == "POST":

        doctor.delete()

        messages.success(request, "Doctor deleted successfully.")

        return redirect("doctors:doctor_list")

    return render(
        request,
        "doctors/doctor_confirm_delete.html",
        {"doctor": doctor}
    )


@login_required
def doctor_dashboard(request):

    doctor = request.user.doctor

    appointments = Appointment.objects.filter(slot__doctor=doctor)

    context = {
        "doctor": doctor,
        "appointments": appointments,
        "total_appointments": appointments.count(),
        "completed": appointments.filter(status=Appointment.Status.COMPLETED).count(),
        "pending": appointments.filter(status=Appointment.Status.PENDING).count(),
        "cancelled": appointments.filter(status=Appointment.Status.CANCELLED).count(),
        "total_patients": appointments.values("patient").distinct().count(),
        "revenue": (
            appointments.filter(status=Appointment.Status.COMPLETED).count()
            * doctor.consultation_fee
        ),
    }

    return render(
        request,
        "doctors/dashboard.html",
        context,
    )


@login_required
def slot_list(request):

    doctor = request.user.doctor

    slots = doctor.slots.all()

    return render(
        request,
        "doctors/slot_list.html",
        {"slots": slots}
    )


@login_required
def slot_create(request):
    form = DoctorSlotForm(request.POST or None,doctor=request.user.doctor,)

    if form.is_valid():
        slot = form.save(commit=False)
        slot.doctor = request.user.doctor
        slot.save()
        messages.success(request, "Slot created successfully.")
        return redirect("doctors:slot_list")

    return render(request, "doctors/slot_form.html", {"form": form})


@login_required
def slot_update(request, pk):

    slot = get_object_or_404(
        DoctorSlot,
        pk=pk,
        doctor=request.user.doctor,
    )

    form = DoctorSlotForm(request.POST or None,instance=slot,doctor=request.user.doctor,)

    if form.is_valid():

        form.save()

        messages.success(request, "Slot updated.")

        # FIX: was redirect("slot_list") — un-namespaced.
        return redirect("doctors:slot_list")

    return render(
        request,
        "doctors/slot_form.html",
        {"form": form}
    )


@login_required
def slot_delete(request, pk):

    slot = get_object_or_404(
        DoctorSlot,
        pk=pk,
        doctor=request.user.doctor,
    )

    if request.method == "POST":

        slot.delete()

        messages.success(request, "Slot deleted.")

        # FIX: was redirect("slot_list") — un-namespaced.
        return redirect("doctors:slot_list")

    return render(
        request,
        "doctors/slot_confirm_delete.html",
        {"slot": slot}
    )


@login_required
def appointment_history(request):
    if not hasattr(request.user, "doctor"):
        messages.error(request, "Only doctors can access appointment history.")
        return redirect("patients:dashboard")

    doctor = request.user.doctor

    appointments = (
        Appointment.objects
        .filter(slot__doctor=doctor)
        .select_related("patient__user")
    )

    return render(
        request,
        "doctors/appointment_history.html",
        {"appointments": appointments},
    )

@login_required
def slot_toggle(request, pk):

    slot = get_object_or_404(
        DoctorSlot,
        pk=pk,
        doctor=request.user.doctor,
    )

    # Don't allow disabling a booked slot
    if slot.is_booked:
        messages.warning(
            request,
            "Booked slots cannot be disabled."
        )
        return redirect("doctors:slot_list")

    slot.is_active = not slot.is_active
    slot.save()

    if slot.is_active:
        messages.success(request, "Slot enabled successfully.")
    else:
        messages.success(request, "Slot disabled successfully.")

    return redirect("doctors:slot_list")