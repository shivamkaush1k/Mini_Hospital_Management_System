from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count, F

from .models import Appointment
from doctors.models import DoctorSlot


class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = (
            "slot",
            "appointment_time",
            "reason",
        )

        widgets = {
            "slot": forms.HiddenInput(),

            "appointment_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Reason for appointment...",
                }
            ),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)

        qs = (
            DoctorSlot.objects
            .filter(is_active=True)
            .annotate(booked=Count("appointments"))
            .filter(booked__lt=F("max_patients"))
        )

        if doctor is not None:
            qs = qs.filter(doctor=doctor)

        self.fields["slot"].queryset = qs.select_related(
            "doctor",
            "doctor__user",
        )

    def clean_slot(self):
        slot = self.cleaned_data.get("slot")

        if slot and slot.appointments.count() >= slot.max_patients:
            raise ValidationError("This slot is already full.")

        return slot

    def clean(self):
        cleaned_data = super().clean()

        slot = cleaned_data.get("slot")
        appointment_time = cleaned_data.get("appointment_time")

        if slot and appointment_time:
            if not (slot.start_time <= appointment_time < slot.end_time):
                raise ValidationError(
                    f"Appointment time must be between "
                    f"{slot.start_time.strftime('%I:%M %p')} and "
                    f"{slot.end_time.strftime('%I:%M %p')}."
                )

        return cleaned_data


class AppointmentStatusForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = (
            "status",
            "notes",
            "cancellation_reason",
        )

        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select"}
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "cancellation_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status")
        cancellation_reason = cleaned_data.get("cancellation_reason")

        if (
            status == Appointment.Status.CANCELLED
            and not cancellation_reason
        ):
            raise ValidationError(
                "Cancellation reason is required."
            )

        return cleaned_data


class AppointmentSearchForm(forms.Form):

    patient = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Patient Name",
            }
        ),
    )

    doctor = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Doctor Name",
            }
        ),
    )

    appointment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )

    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Status")] + list(Appointment.Status.choices),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )