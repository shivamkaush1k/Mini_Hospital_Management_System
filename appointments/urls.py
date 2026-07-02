from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="appointment_list"),

    path(
        "book/<int:doctor_id>/",
        views.book_appointment_form,
        name="book_appointment_form",
    ),

    path(
        "book/",
        views.book_appointment,
        name="book_appointment",
    ),

    path(
        "<int:pk>/",
        views.appointment_detail,
        name="appointment_detail",
    ),

    path(
        "<int:pk>/status/",
        views.update_status,
        name="update_status",
    ),

    path(
        "<int:pk>/cancel/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),

    path(
        "<int:pk>/delete/",
        views.delete_appointment,
        name="delete_appointment",
    ),

    path(
        "doctor-queue/",
        views.doctor_queue,
        name="doctor_queue",
    ),

    path(
        "my/",
        views.my_appointments,
        name="my_appointments",
    ),

    path(
        "today/",
        views.today_appointments,
        name="today_appointments",
    ),
    path("book/<int:doctor_id>/", views.book_appointment_form, name="book_appointment_form"),
    path("doctor-slots/<int:doctor_id>/", views.doctor_slots_ajax, name="doctor_slots_ajax"),
]