from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "appointment_number",
        "get_doctor",
        "patient",
        "appointment_date",
        "appointment_time",
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

    def get_doctor(self, obj):
        return obj.slot.doctor
    get_doctor.short_description = "Doctor"
    get_doctor.admin_order_field = "slot__doctor"