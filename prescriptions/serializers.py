from rest_framework import serializers

from appointments.serializers import AppointmentSerializer
from .models import Prescription, PrescriptionMedicine


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = "__all__"


class PrescriptionSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Prescription._meta.get_field("appointment").related_model.objects.all(),
        source="appointment",
        write_only=True
    )
    medicines = PrescriptionMedicineSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = (
            "id",
            "appointment",
            "appointment_id",
            "diagnosis",
            "advice",
            "follow_up_required",
            "follow_up_date",
            "created_at",
            "updated_at",
            "medicines",
            "patient_name",
            "doctor_name",
        )

    def get_patient_name(self, obj):
        return obj.appointment.patient.user.get_full_name().strip()

    def get_doctor_name(self, obj):
        return obj.appointment.slot.doctor.user.get_full_name().strip()