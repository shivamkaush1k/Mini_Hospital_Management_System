from django.urls import path

from . import views

app_name = "prescriptions"

urlpatterns = [
    path("", views.prescription_list, name="prescription_list"),
    path("<uuid:pk>/", views.prescription_detail, name="prescription_detail"),
    path("create/<uuid:appointment_id>/", views.prescription_create, name="prescription_create"),
    path("<uuid:pk>/edit/", views.prescription_update, name="prescription_update"),
    path("<uuid:pk>/delete/", views.prescription_delete, name="prescription_delete"),
]