from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    DoctorViewSet,
    PatientViewSet,
    AppointmentViewSet,
    PrescriptionViewSet,
    MedicalHistoryViewSet,
)

router = DefaultRouter()

router.register("doctors", DoctorViewSet)
router.register("patients", PatientViewSet)
router.register("appointments", AppointmentViewSet)
router.register("prescriptions", PrescriptionViewSet)

patient_router = NestedDefaultRouter(router, "patients", lookup="patient")

patient_router.register(
    "appointments",
    AppointmentViewSet,
    basename="patient-appointments",
)

patient_router.register(
    "prescriptions",
    PrescriptionViewSet,
    basename="patient-prescriptions",
)

patient_router.register(
    "medical-history",
    MedicalHistoryViewSet,
    basename="patient-medical-history",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(patient_router.urls)),
]