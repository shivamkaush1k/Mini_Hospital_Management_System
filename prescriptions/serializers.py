from rest_framework import serializers

from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer

from .models import Prescription, PrescriptionMedicine


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = ("id", "name", "dosage", "frequency", "duration", "instructions")
        read_only_fields = ("id",)


class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Single serializer used for both read and write, mirroring the
    `slot` / `slot_id` pattern in `AppointmentSerializer`: `appointment`
    is a nested read-only representation, `appointment_id` is the
    write-only primary key used on create.

    `appointment_id` is intentionally `required=False` so PATCH/PUT on
    an existing prescription doesn't force the client to resend it --
    the appointment never changes after creation. Nested `medicines` are
    fully replaced on write (existing lines are deleted and the payload's
    lines are recreated), which keeps this simple but means a client
    must resend the complete list of medicines on every update, not just
    the ones that changed.
    """

    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(
            status=Appointment.Status.COMPLETED, prescription__isnull=True
        ),
        source="appointment",
        write_only=True,
        required=False,
    )
    medicines = PrescriptionMedicineSerializer(many=True, required=False)

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
        read_only_fields = ("id", "created_at", "updated_at")

    def get_patient_name(self, obj):
        return obj.appointment.patient.user.get_full_name().strip()

    def get_doctor_name(self, obj):
        return obj.appointment.slot.doctor.user.get_full_name().strip()

    def validate(self, attrs):
        appointment = attrs.get("appointment") or getattr(self.instance, "appointment", None)
        request = self.context.get("request")
        user = getattr(request, "user", None) if request else None

        if appointment is None:
            raise serializers.ValidationError({"appointment_id": "This field is required."})

        if user is not None and hasattr(user, "doctor"):
            if appointment.slot.doctor_id != user.doctor.id:
                raise serializers.ValidationError(
                    "You can only create prescriptions for your own appointments."
                )

        follow_up_required = attrs.get(
            "follow_up_required", getattr(self.instance, "follow_up_required", False)
        )
        follow_up_date = attrs.get(
            "follow_up_date", getattr(self.instance, "follow_up_date", None)
        )
        if follow_up_required and not follow_up_date:
            raise serializers.ValidationError(
                {"follow_up_date": "Follow-up date is required when follow-up is marked as required."}
            )

        return attrs

    def create(self, validated_data):
        medicines_data = validated_data.pop("medicines", [])
        prescription = Prescription.objects.create(**validated_data)
        for medicine_data in medicines_data:
            PrescriptionMedicine.objects.create(prescription=prescription, **medicine_data)
        return prescription

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop("medicines", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if medicines_data is not None:
            instance.medicines.all().delete()
            for medicine_data in medicines_data:
                PrescriptionMedicine.objects.create(prescription=instance, **medicine_data)

        return instance