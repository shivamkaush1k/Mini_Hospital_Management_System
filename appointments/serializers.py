from rest_framework import serializers

from patients.serializers import PatientSerializer
from .models import Appointment
from doctors.models import DoctorSlot


class DoctorSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorSlot
        fields = (
            "id",
            "doctor",
            "doctor_name",
            "day",
            "start_time",
            "end_time",
            "is_active",
            "is_booked",
        )

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name().strip()


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    slot = DoctorSlotSerializer(read_only=True)

    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    slot_id = serializers.PrimaryKeyRelatedField(
        queryset=DoctorSlot.objects.filter(is_active=True, ),
        source="slot",
        write_only=True,
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "slot",
            "slot_id",
            "appointment_number",
            "appointment_date",
            "status",
            "reason",
            "notes",
            "created_at",
            "updated_at",
            "doctor_name",
            "patient_name",
        )
        read_only_fields = ("appointment_number", "appointment_date")

    def get_doctor_name(self, obj):
        return obj.slot.doctor.user.get_full_name().strip()

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name().strip()