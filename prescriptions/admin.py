from django.contrib import admin
from .models import Prescription, PrescriptionMedicine


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return obj is None

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return False
        return super().has_change_permission(request, obj)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_patient",
        "get_doctor",
        "follow_up_required",
        "follow_up_date",
        "created_at",
    )
    list_filter = ("follow_up_required", "follow_up_date", "created_at")
    search_fields = (
        "appointment__patient__user__first_name",
        "appointment__patient__user__last_name",
        "appointment__slot__doctor__user__first_name",
        "appointment__slot__doctor__user__last_name",
        "diagnosis",
    )
    readonly_fields = (
        "id",
        "appointment",
        "diagnosis",
        "advice",
        "follow_up_required",
        "follow_up_date",
        "created_at",
        "updated_at",
    )
    inlines = [PrescriptionMedicineInline]
    date_hierarchy = "created_at"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def get_patient(self, obj):
        return obj.patient
    get_patient.short_description = "Patient"
    get_patient.admin_order_field = "appointment__patient"

    def get_doctor(self, obj):
        return obj.doctor
    get_doctor.short_description = "Doctor"
    get_doctor.admin_order_field = "appointment__slot__doctor"