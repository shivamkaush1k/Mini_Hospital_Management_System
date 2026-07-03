from django.urls import path
from . import views
import uuid
app_name = "prescriptions"

urlpatterns = [
    path("", views.prescription_list, name="prescription_list"),
    path("create/", views.prescription_create, name="prescription_create"),
    path("my/", views.my_prescriptions, name="my_prescriptions"),
    path("doctor/", views.doctor_prescriptions, name="doctor_prescriptions"),

    path("<uuid:pk>/", views.prescription_detail, name="prescription_detail"),
    path("<uuid:pk>/update/", views.prescription_update, name="prescription_update"),
    path("<uuid:pk>/delete/", views.prescription_delete, name="prescription_delete"),
    path("<uuid:pk>/print/", views.print_prescription, name="print_prescription"),
]