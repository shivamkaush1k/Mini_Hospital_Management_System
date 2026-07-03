from django.urls import path
import uuid
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="appointment_list"),
    path("book/<uuid:doctor_id>/",views.book_appointment_form,name="book_appointment_form",),
    path("book/",views.book_appointment,name="book_appointment",),
    path("<uuid:pk>/",views.appointment_detail,name="appointment_detail",),
    path("<uuid:pk>/status/",views.update_status,name="update_status",),
    path("<uuid:pk>/cancel/",views.cancel_appointment,name="cancel_appointment",),
    path("<uuid:pk>/delete/",views.delete_appointment,name="delete_appointment",),
    path("doctor-queue/",views.doctor_queue,name="doctor_queue",),
    path("my/",views.my_appointments,name="my_appointments",),
    path("today/",views.today_appointments,name="today_appointments",),
    path("book/<uuid:doctor_id>/", views.book_appointment_form, name="book_appointment_form"),
    path("doctor-slots/<uuid:doctor_id>/", views.doctor_slots_ajax, name="doctor_slots_ajax"),
]