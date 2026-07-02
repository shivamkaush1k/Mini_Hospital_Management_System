from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("<int:pk>/", views.doctor_detail, name="doctor_detail"),

    path("create/", views.doctor_create, name="doctor_create"),
    path("<int:pk>/edit/", views.doctor_update, name="doctor_update"),
    path("<int:pk>/delete/", views.doctor_delete, name="doctor_delete"),

    path("dashboard/", views.doctor_dashboard, name="doctor_dashboard"),

    path("slots/", views.slot_list, name="slot_list"),
    path("slots/add/", views.slot_create, name="slot_create"),
    path("slots/<int:pk>/edit/", views.slot_update, name="slot_update"),
    path("slots/<int:pk>/delete/", views.slot_delete, name="slot_delete"),

    path(
        "appointments/history/",
        views.appointment_history,
        name="appointment_history",
    ),
]