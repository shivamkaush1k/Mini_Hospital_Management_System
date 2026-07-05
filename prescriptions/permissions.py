from rest_framework.permissions import BasePermission


class CanViewPrescriptions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.is_staff or hasattr(user, "doctor") or hasattr(user, "patient"))
        )


class CanManagePrescriptions(BasePermission):
    """Only doctors and staff may create/update/delete prescriptions."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.is_staff or hasattr(user, "doctor"))
        )


class IsPrescriptionOwnerDoctorPatientOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        if hasattr(user, "doctor"):
            return obj.appointment.slot.doctor.user_id == user.id
        if hasattr(user, "patient"):
            return obj.appointment.patient.user_id == user.id
        return False