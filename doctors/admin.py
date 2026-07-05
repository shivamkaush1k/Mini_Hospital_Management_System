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
    # Only real model fields and real properties/methods on DoctorSlot.
    # No max_patients, is_booked, capacity, buffer_time, or booked_count —
    # those fields don't exist anymore.
    list_display = (
        "doctor",
        "date",
        "start_time",
        "end_time",
        "consultation_duration",
        "buffer_duration",
        "total_slots",
        "booked_slots",
        "available_slots",
        "current_status",
        "is_active",
    )

    list_filter = (
        "date",
        "is_active",
    )

    search_fields = (
        "doctor__user__username",
        "doctor__user__first_name",
        "doctor__user__last_name",
        "doctor__specialization",
    )

    ordering = (
        "date",
        "start_time",
    )

    date_hierarchy = "date"