from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Profile
from doctors.models import Doctor
from patients.models import Patient, MedicalHistory
from appointments.models import Appointment
from prescriptions.models import Prescription

from doctors.serializers import DoctorSerializer
from patients.serializers import PatientSerializer, MedicalHistorySerializer
from appointments.serializers import AppointmentSerializer
from prescriptions.serializers import PrescriptionSerializer

from accounts.permissions import (
    IsAuthenticatedAndActive,
    IsDoctor,
    IsPatient,
    IsDoctorOrAdmin,
    IsPatientOrAdmin,
    IsAdminUserCustom,
)
from doctors.permissions import (
    CanViewDoctors,
    CanManageDoctors,
    IsOwnDoctorProfileOrAdmin,
)
from patients.permissions import (
    CanViewPatients,
    CanManagePatients,
    IsOwnPatientProfileOrStaff,
    IsOwnMedicalRecordOrDoctorOrAdmin,
)
from appointments.permissions import (
    CanCreateAppointment,
    CanViewAppointments,
    IsAppointmentOwnerDoctorOrAdmin,
    CanUpdateAppointment,
)
from prescriptions.permissions import (
    CanViewPrescriptions,
    CanManagePrescriptions,
    IsPrescriptionOwnerDoctorPatientOrAdmin,
)


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.select_related("user")
    permission_classes = [IsAuthenticatedAndActive, CanViewDoctors]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticatedAndActive(), CanManageDoctors()]
        if self.action in ["retrieve"]:
            return [IsAuthenticatedAndActive(), IsOwnDoctorProfileOrAdmin()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        qs = Doctor.objects.select_related("user")

        if user.is_staff:
            return qs

        if hasattr(user, "doctor"):
            return qs.filter(user=user)

        return qs

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        if not hasattr(request.user, "doctor"):
            return Response(
                {"detail": "You are not a doctor."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(request.user.doctor)
        return Response(serializer.data)


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    queryset = Patient.objects.select_related("user")
    permission_classes = [IsAuthenticatedAndActive, CanViewPatients]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticatedAndActive(), CanManagePatients()]
        if self.action in ["retrieve"]:
            return [IsAuthenticatedAndActive(), IsOwnPatientProfileOrStaff()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        qs = Patient.objects.select_related("user")

        if user.is_staff or hasattr(user, "doctor"):
            return qs

        if hasattr(user, "patient"):
            return qs.filter(user=user)

        return qs.none()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        if not hasattr(request.user, "patient"):
            return Response(
                {"detail": "You are not a patient."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(request.user.patient)
        return Response(serializer.data)


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalHistorySerializer
    queryset = MedicalHistory.objects.select_related(
        "patient__user",
        "doctor__user",
    )
    permission_classes = [IsAuthenticatedAndActive]

    def get_queryset(self):
        user = self.request.user
        qs = MedicalHistory.objects.select_related(
            "patient__user",
            "doctor__user",
        )

        if user.is_staff or hasattr(user, "doctor"):
            return qs

        if hasattr(user, "patient"):
            return qs.filter(patient=user.patient)

        return qs.none()

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticatedAndActive(), IsOwnMedicalRecordOrDoctorOrAdmin()]
        return [IsAuthenticatedAndActive()]

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, "patient"):
            serializer.save(patient=user.patient)
        else:
            serializer.save()


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.select_related(
        "patient__user",
        "slot__doctor__user",
    )
    permission_classes = [IsAuthenticatedAndActive, CanViewAppointments]

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related(
            "patient__user",
            "slot__doctor__user",
        )

        if user.is_staff:
            return qs

        if hasattr(user, "doctor"):
            return qs.filter(slot__doctor=user.doctor)

        if hasattr(user, "patient"):
            return qs.filter(patient=user.patient)

        return qs.none()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedAndActive(), CanCreateAppointment()]
        if self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [IsAuthenticatedAndActive(), IsAppointmentOwnerDoctorOrAdmin()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        if hasattr(self.request.user, "patient"):
            serializer.save(patient=self.request.user.patient)
        else:
            serializer.save()

    @action(detail=False, methods=["get"], url_path="my")
    def my_appointments(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    queryset = Prescription.objects.select_related(
        "appointment__patient__user",
        "appointment__slot__doctor__user",
    )
    permission_classes = [IsAuthenticatedAndActive, CanViewPrescriptions]

    def get_queryset(self):
        user = self.request.user
        qs = Prescription.objects.select_related(
            "appointment__patient__user",
            "appointment__slot__doctor__user",
        )

        if user.is_staff:
            return qs

        if hasattr(user, "doctor"):
            return qs.filter(appointment__slot__doctor=user.doctor)

        if hasattr(user, "patient"):
            return qs.filter(appointment__patient=user.patient)

        return qs.none()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticatedAndActive(), CanManagePrescriptions()]
        if self.action in ["retrieve"]:
            return [IsAuthenticatedAndActive(), IsPrescriptionOwnerDoctorPatientOrAdmin()]
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=["get"], url_path="my")
    def my_prescriptions(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)