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
def home(request):
    context = {
        "doctor_count": Doctor.objects.count(),
        "patient_count": Patient.objects.count(),
        "appointment_count": Appointment.objects.count(),
        "prescription_count": Prescription.objects.count(),
    }
    return render(request, "home.html", context)


# -----------------------
# AUTH: REGISTER
# -----------------------
def register(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        # The template posts a hidden "role" field plus role-specific
        # fields (blood_group/gender for patients, specialization/
        # experience_years/consultation_fee/license_number/qualifications
        # for doctors) that are NOT part of ProfileForm.Meta.fields.
        # We read them directly from POST and build the matching
        # Patient/Doctor row so they aren't silently dropped.
        role = request.POST.get("role", "patient")

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Only commit the User once we know the rest of the
                    # registration will succeed, so we never end up with
                    # an orphaned User + missing profile/role row.
                    user = user_form.save(commit=False)
                    user.save()

                    profile = user.profile  # created via signal, or:
                    # profile, _ = Profile.objects.get_or_create(user=user)

                    profile.role = (
                        Profile.Role.DOCTOR if role == "doctor" else Profile.Role.PATIENT
                    )
                    profile.image = profile_form.cleaned_data.get("image")
                    profile.phone = profile_form.cleaned_data.get("phone", "")
                    profile.gender = (
                        profile_form.cleaned_data.get("gender")
                        or request.POST.get("gender", "")
                    )
                    profile.date_of_birth = profile_form.cleaned_data.get("date_of_birth")
                    profile.address = profile_form.cleaned_data.get("address", "")
                    profile.city = profile_form.cleaned_data.get("city", "")
                    profile.state = profile_form.cleaned_data.get("state", "")
                    profile.country = profile_form.cleaned_data.get("country") or "India"
                    profile.pincode = profile_form.cleaned_data.get("pincode", "")
                    profile.save()

                    if role == "doctor":
                        Doctor.objects.create(
                            user=user,
                            specialization=request.POST.get("specialization", ""),
                            experience=request.POST.get("experience_years") or 0,
                            consultation_fee=request.POST.get("consultation_fee") or 0,
                            license_number=request.POST.get("license_number", ""),
                            qualifications=request.POST.get("qualifications", ""),
                        )
                    else:
                        Patient.objects.create(
                            user=user,
                            blood_group=request.POST.get("blood_group", ""),
                        )

                messages.success(request, "Registration successful.")
                return redirect("accounts:login")

            except IntegrityError:
                messages.error(
                    request,
                    "Something went wrong creating your account. Please try again.",
                )

    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    return render(request, "accounts/register.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


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

    context = {
        "profile": profile,
        "patient": patient,
        "doctor": doctor,
    }
    return render(request, "accounts/dashboard.html", context)


# -----------------------
# PROFILE UPDATE
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

    return render(request, "accounts/profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


# -----------------------
# USER MANAGEMENT (ADMIN)
# -----------------------
@login_required
def users(request):
    users = User.objects.select_related("profile").all()

    return render(request, "accounts/users.html", {
        "users": users
    })


@login_required
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