from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def patient_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "patient"):
            messages.error(request, "This page is only available to patients.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "doctor"):
            messages.error(request, "This page is only available to doctors.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not (request.user.is_staff or (profile and profile.role == "ADMIN")):
            messages.error(request, "You do not have permission to view this page.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapped