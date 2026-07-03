from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from appointments.models import Appointment
from doctors.models import Doctor
from patients.models import Patient
from prescriptions.models import Prescription

from .decorators import admin_required
from .models import Profile
from .forms import (
    LoginForm,
    ProfileForm,
    UserRegisterForm,
    UserUpdateForm,
)


# -----------------------
# HOME
# -----------------------
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from prescriptions.models import Prescription


def home(request):

    featured_doctors = (
        Doctor.objects.filter(is_active=True)
        .select_related("user", "user__profile")
        [:4]
    )

    hero_stats = [
        {
            "value": Doctor.objects.filter(is_active=True).count(),
            "label": "Expert Doctors",
        },
        {
            "value": len(Doctor.Specialization.choices),
            "label": "Specializations",
        },
        {
            "value": Appointment.objects.count(),
            "label": "Appointments",
        },
        {
            "value": "24×7",
            "label": "Support",
        },
    ]

    services = [
        {
            "name": "Cardiology",
            "icon": "fa fa-heart-pulse",
            "description": "Expert diagnosis and treatment for heart-related conditions.",
        },
        {
            "name": "Neurology",
            "icon": "fa fa-brain",
            "description": "Advanced neurological consultation and treatment.",
        },
        {
            "name": "Orthopedics",
            "icon": "fa fa-bone",
            "description": "Bone, joint and sports injury care.",
        },
        {
            "name": "Pediatrics",
            "icon": "fa fa-baby",
            "description": "Healthcare services for infants and children.",
        },
        {
            "name": "Ophthalmology",
            "icon": "fa fa-eye",
            "description": "Comprehensive eye examinations and treatment.",
        },
        {
            "name": "Diagnostics",
            "icon": "fa fa-flask",
            "description": "Laboratory and diagnostic services.",
        },
    ]

    context = {
        # Existing counts
        "doctor_count": Doctor.objects.count(),
        "patient_count": Patient.objects.count(),
        "appointment_count": Appointment.objects.count(),
        "prescription_count": Prescription.objects.count(),

        # Homepage values
        "total_doctors": Doctor.objects.filter(is_active=True).count(),
        "total_patients": Patient.objects.count(),

        "featured_doctors": featured_doctors,

        "specializations": [
            choice[0]
            for choice in Doctor.Specialization.choices
        ],

        "hero_stats": hero_stats,

        "services": services,
    }

    return render(
        request,
        "home.html",
        context,
    )
# -----------------------
# AUTH: REGISTER
# -----------------------
def register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        # The role-card JS sends "PATIENT" / "DOCTOR" (uppercase).
        # Normalize with .upper() so the comparisons below actually match.
        role = request.POST.get("role", "PATIENT").upper()

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():

                    # -------------------
                    # Create User
                    # -------------------
                    user = user_form.save()

                    # -------------------
                    # Create/Get Profile
                    # -------------------
                    profile, _ = Profile.objects.get_or_create(user=user)

                    profile.role = (
                        Profile.Role.DOCTOR
                        if role == "DOCTOR"
                        else Profile.Role.PATIENT
                    )

                    profile.image = profile_form.cleaned_data.get("image")
                    profile.phone = profile_form.cleaned_data.get("phone")
                    profile.gender = profile_form.cleaned_data.get("gender")
                    profile.date_of_birth = profile_form.cleaned_data.get(
                        "date_of_birth"
                    )
                    profile.address = profile_form.cleaned_data.get("address")
                    profile.city = profile_form.cleaned_data.get("city")
                    profile.state = profile_form.cleaned_data.get("state")
                    profile.country = (
                        profile_form.cleaned_data.get("country")
                        or "India"
                    )
                    profile.pincode = profile_form.cleaned_data.get("pincode")

                    profile.save()

                    # -------------------
                    # Doctor
                    # -------------------
                    if role == "DOCTOR":

                        Doctor.objects.create(
                            user=user,
                            specialization=request.POST.get("specialization"),
                            # Template field is named "qualification" (singular),
                            # not "qualifications".
                            qualification=request.POST.get("qualification"),
                            # Template field is named "experience",
                            # not "experience_years".
                            experience=int(
                                request.POST.get("experience") or 0
                            ),
                            consultation_fee=float(
                                request.POST.get("consultation_fee") or 0
                            ),
                            license_number=request.POST.get("license_number"),
                            room_number=request.POST.get("room_number") or "101",
                        )

                    # -------------------
                    # Patient
                    # -------------------
                    else:

                        Patient.objects.create(
                            user=user,
                            blood_group=request.POST.get("blood_group"),
                            height=float(
                                request.POST.get("height") or 0
                            ),
                            weight=float(
                                request.POST.get("weight") or 0
                            ),
                            emergency_contact_name=request.POST.get(
                                "emergency_contact_name"
                            ),
                            emergency_contact_phone=request.POST.get(
                                "emergency_contact_phone"
                            ),
                        )

                messages.success(
                    request,
                    "Registration successful. Please login."
                )

                return redirect("accounts:login")

            except Exception as e:
                messages.error(request, str(e))

        else:
            # Display validation errors
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    return render(
        request,
        "accounts/register.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


# -----------------------
# AUTH: LOGIN
# -----------------------
def user_login(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            if user:
                login(request, user)
                return redirect("accounts:dashboard")

            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html", {"form": form})


# -----------------------
# AUTH: LOGOUT
# -----------------------
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("accounts:home")


# -----------------------
# DASHBOARD
# -----------------------
@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)
    patient = getattr(request.user, "patient", None)
    doctor = getattr(request.user, "doctor", None)

    # Route each role straight to its dedicated dashboard instead of
    # rendering a generic page for everyone.
    if patient is not None:
        return redirect("patients:dashboard")
    if doctor is not None:
        return redirect("doctors:doctor_dashboard")

    context = {
        "profile": profile,
        "patient": patient,
        "doctor": doctor,
    }
    return render(request, "accounts/dashboard.html", context)


# -----------------------
# PROFILE (VIEW + EDIT)
# -----------------------
@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    profile_obj = getattr(request.user, "profile", None)
    doctor = getattr(request.user, "doctor", None)
    patient = getattr(request.user, "patient", None)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile_obj,
        "doctor": doctor,
        "patient": patient,
    }

    # Role-specific stats + recent activity, computed here so the
    # template only ever has to render values, never query.
    if doctor is not None:
        appointments = Appointment.objects.filter(slot__doctor=doctor)

        context.update({
            "total_patients": appointments.values("patient").distinct().count(),
            "total_appointments": appointments.count(),
            "completed_appointments": appointments.filter(
                status=Appointment.Status.COMPLETED
            ).count(),
            "available_slots": doctor.slots.filter(
                is_active=True
            ).exclude(
                appointments__status__in=[
                    Appointment.Status.PENDING,
                    Appointment.Status.COMPLETED,
                ]
            ).distinct().count(),
            "recent_appointments": (
                appointments
                .select_related("patient__user")
                .order_by("-appointment_date")[:5]
            ),
        })

    elif patient is not None:
        appointments = patient.appointments.all()
        prescriptions = Prescription.objects.filter(appointment__patient=patient)

        context.update({
            "total_appointments": appointments.count(),
            "upcoming_appointments": appointments.filter(
                status=Appointment.Status.PENDING
            ).count(),
            "completed_appointments": appointments.filter(
                status=Appointment.Status.COMPLETED
            ).count(),
            "prescriptions_count": prescriptions.count(),
            "recent_appointments": (
                appointments
                .select_related("slot__doctor__user")
                .order_by("-appointment_date")[:5]
            ),
        })

    return render(request, "accounts/profile.html", context)


# -----------------------
# USER MANAGEMENT (ADMIN)
# -----------------------
@login_required
@admin_required
def users(request):
    users = User.objects.select_related("profile").all()

    return render(request, "accounts/users.html", {
        "users": users
    })


@login_required
@admin_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect("accounts:users")

    return render(request, "accounts/delete_user.html", {"object": user})


# -----------------------
# STATIC PAGES
# -----------------------
def about(request):
    return render(request, "about.html")


def contacts(request):
    return render(request, "contacts.html")


# -----------------------
# ERROR HANDLERS
# -----------------------
def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)