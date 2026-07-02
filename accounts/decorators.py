from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def patient_required(view_func):
    """
    Use on any view that assumes request.user.patient exists.
    Prevents RelatedObjectDoesNotExist ("User has no patient") for
    accounts that aren't patients (staff, doctor-only accounts, or
    accounts created before a Patient row was attached to them).
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "patient"):
            messages.error(request, "This page is only available to patient accounts.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def doctor_required(view_func):
    """
    Use on any view that assumes request.user.doctor exists.
    Prevents RelatedObjectDoesNotExist ("User has no doctor") for
    accounts that aren't doctors.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "doctor"):
            messages.error(request, "This page is only available to doctor accounts.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped