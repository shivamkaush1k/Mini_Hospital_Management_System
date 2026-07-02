from django.contrib import admin
from .models import Doctor, DoctorSlot


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "specialization",
        "experience",
        "consultation_fee",
        "room_number",
        "rating",
        "is_active",
    )
    list_filter = (
        "specialization",
        "is_active",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "qualification",
        "department",
        "license_number",
        "room_number",
    )
    ordering = (
        "specialization",
        "user__first_name",
    )


@admin.register(DoctorSlot)
class DoctorSlotAdmin(admin.ModelAdmin):
    list_display = (
        "doctor",
        "day",
        "start_time",
        "end_time",
        "max_patients",
        "is_active",
    )
    list_filter = (
        "day",
        "is_active",
    )
    search_fields = (
        "doctor__user__first_name",
        "doctor__user__last_name",
        "doctor__specialization",
    )