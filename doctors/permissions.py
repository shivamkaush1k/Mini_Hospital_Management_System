from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanViewDoctors(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanManageDoctors(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.is_staff
        )


class IsOwnDoctorProfileOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.is_staff or obj.user == user)
        )


class IsOwnDoctorDataOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.is_staff or obj.doctor.user == user or obj.user == user)
        )