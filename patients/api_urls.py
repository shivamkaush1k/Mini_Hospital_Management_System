from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .api_views import PatientViewSet, MedicalHistoryViewSet

app_name = "patients_api"

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")

patients_router = NestedDefaultRouter(router, r"patients", lookup="patient")
patients_router.register(r"medical-history", MedicalHistoryViewSet, basename="patient-medical-history")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(patients_router.urls)),
]