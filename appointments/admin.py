from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "appointment_number",
        "doctor",
        "patient",
        "appointment_date",
        "slot",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "appointment_date",
    )
    search_fields = (
        "appointment_number",
        "slot__doctor__user__first_name",
        "slot__doctor__user__last_name",
        "patient__user__first_name",
        "patient__user__last_name",
    )
    date_hierarchy = "appointment_date"
    ordering = (
        "-appointment_date",
        "slot",
    )