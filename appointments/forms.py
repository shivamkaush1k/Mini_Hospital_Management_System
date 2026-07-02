from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Appointment
from doctors.models import DoctorSlot


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = (
            "slot",
            "appointment_date",
            "reason",
        )
        widgets = {
            "slot": forms.Select(
                attrs={"class": "form-select"}
            ),
            "appointment_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Reason for appointment..."
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slot"].queryset = (
            DoctorSlot.objects.filter(is_active=True)
            .select_related("doctor", "doctor__user")
        )

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get("appointment_date")
        if appointment_date and appointment_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        slot = cleaned_data.get("slot")
        appointment_date = cleaned_data.get("appointment_date")

        if not slot or not appointment_date:
            return cleaned_data

        if slot.day != appointment_date.strftime("%A"):
            raise ValidationError(
                "Selected slot is not available on the chosen date."
            )

        qs = Appointment.objects.filter(
            slot=slot,
            appointment_date=appointment_date,
        )

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("This slot has already been booked.")

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

        if status == Appointment.Status.CANCELLED and not cancellation_reason:
            raise ValidationError("Cancellation reason is required.")

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
            attrs={"class": "form-select"}
        ),
    )