from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor",
        "created_at",
        "follow_up_date",
    )
    list_filter = (
        "created_at",
        "follow_up_date",
    )
    search_fields = (
        "appointment__patient__user__first_name",
        "appointment__patient__user__last_name",
        "appointment__slot__doctor__user__first_name",
        "appointment__slot__doctor__user__last_name",
        "diagnosis",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)