from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import Appointment
from doctors.models import DoctorSlot


class AppointmentForm(forms.ModelForm):

    # Rendered as an empty <select>; the booking page's JS fills in the
    # actual options after the patient picks a date (see book.html).
    # We also rebuild the choices here so server-side validation works
    # even if JS is disabled or the request is replayed.
    appointment_time = forms.ChoiceField(
        choices=[],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    class Meta:
        model = Appointment
        fields = (
            "slot",
            "appointment_time",
            "reason",
        )

        widgets = {
            "slot": forms.HiddenInput(),

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

        qs = DoctorSlot.objects.filter(is_active=True)

        if doctor is not None:
            qs = qs.filter(doctor=doctor)

        self.fields["slot"].queryset = qs.select_related(
            "doctor",
            "doctor__user",
        )

        self.fields["appointment_time"].choices = []

        slot = None

        if self.is_bound:
            slot_id = self.data.get("slot")
            if slot_id:
                try:
                    slot = DoctorSlot.objects.get(pk=slot_id)
                except DoctorSlot.DoesNotExist:
                    pass
        elif self.initial.get("slot"):
            slot = self.initial.get("slot")

        if slot:
            self.fields["appointment_time"].choices = [
                (t.strftime("%H:%M"), t.strftime("%I:%M %p"))
                for t in slot.available_times()
            ]

    def clean_slot(self):
        slot = self.cleaned_data.get("slot")

        if slot and slot.is_full:
            raise ValidationError("This working session is already full.")

        return slot

    def clean_appointment_time(self):
        value = self.cleaned_data["appointment_time"]

        return datetime.strptime(
            value,
            "%H:%M",
        ).time()

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

            if appointment_time not in slot.available_times():
                raise ValidationError(
                    "That time is no longer available. Please choose another."
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