from rest_framework import serializers

from accounts.serializers import UserSerializer
from doctors.serializers import DoctorSerializer
from .models import Patient, MedicalHistory


class MedicalHistorySerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalHistory
        fields = "__all__"

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name().strip()

    def get_doctor_name(self, obj):
        if obj.doctor and obj.doctor.user:
            return obj.doctor.user.get_full_name().strip()
        return None


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    medical_records = MedicalHistorySerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = "__all__"

    def get_full_name(self, obj):
        return obj.user.get_full_name().strip()