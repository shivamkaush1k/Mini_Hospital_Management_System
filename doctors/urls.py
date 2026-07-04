from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),

    path("<uuid:pk>/", views.doctor_detail, name="doctor_detail"),

    path("create/", views.doctor_create, name="doctor_create"),
    path("<uuid:pk>/edit/", views.doctor_update, name="doctor_update"),
    path("<uuid:pk>/delete/", views.doctor_delete, name="doctor_delete"),
    path("slots/<uuid:pk>/toggle/",views.slot_toggle,name="slot_toggle",),
    path("dashboard/", views.doctor_dashboard, name="doctor_dashboard"),

    path("slots/", views.slot_list, name="slot_list"),
    path("slots/add/", views.slot_create, name="slot_create"),
    path("slots/<uuid:pk>/edit/", views.slot_update, name="slot_update"),
    path("slots/<uuid:pk>/delete/", views.slot_delete, name="slot_delete"),

    path(
        "appointments/history/",
        views.appointment_history,
        name="appointment_history",
    ),
]