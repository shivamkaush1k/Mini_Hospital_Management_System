from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanCreateAppointment(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and hasattr(user, "patient")
        )


class CanViewAppointments(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.is_staff or hasattr(user, "doctor") or hasattr(user, "patient"))
        )


class IsAppointmentOwnerDoctorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        if hasattr(user, "patient"):
            return obj.patient.user == user
        if hasattr(user, "doctor"):
            return obj.slot.doctor.user == user
        return False


class CanUpdateAppointment(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        if hasattr(user, "patient"):
            return obj.patient.user == user
        if hasattr(user, "doctor"):
            return obj.slot.doctor.user == user
        return False