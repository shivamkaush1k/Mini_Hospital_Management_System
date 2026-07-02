from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("", views.patient_list, name="patient_list"),
    path("dashboard/", views.patient_dashboard, name="dashboard"),
    path("update/", views.patient_update, name="patient_update"),

    path("medical-history/", views.medical_history, name="medical_history"),
    path("medical-history/add/", views.add_medical_record, name="add_medical_record"),
    path("medical-history/<uuid:pk>/edit/", views.edit_medical_record, name="edit_medical_record"),
    path("medical-history/<uuid:pk>/delete/", views.delete_medical_record, name="delete_medical_record"),

    path("appointments/", views.appointment_history, name="appointment_history"),
    path("prescriptions/", views.prescription_history, name="prescription_history"),

    path("<uuid:pk>/", views.patient_detail, name="patient_detail"),
]