from django.contrib import admin
from .models import Patient, MedicalHistory


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "blood_group",
        "emergency_contact_name",
        "emergency_contact_phone",
        "created_at",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "emergency_contact_name",
        "emergency_contact_phone",
    )
    list_filter = (
        "blood_group",
    )


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor",
        "visit_date",
    )
    list_filter = (
        "visit_date",
    )
    search_fields = (
        "patient__user__first_name",
        "patient__user__last_name",
        "doctor__user__first_name",
        "doctor__user__last_name",
        "diagnosis",
    )