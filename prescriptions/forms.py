from django import forms
from django.core.exceptions import ValidationError

from appointments.models import Appointment
from .models import Prescription


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = (
            "appointment",
            "diagnosis",
            "advice",
            "follow_up_required",
            "follow_up_date",
        )
        widgets = {
            "appointment": forms.Select(
                attrs={"class": "form-select"}
            ),
            "diagnosis": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter diagnosis..."
                }
            ),
            "advice": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional advice..."
                }
            ),
            "follow_up_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "follow_up_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = (
            Appointment.objects.filter(
                status=Appointment.Status.COMPLETED
            )
            .select_related(
                "patient__user",
                "slot__doctor__user",
            )
        )

        if self.instance and self.instance.pk:
            queryset = queryset.exclude(
                prescription__isnull=False
            ) | Appointment.objects.filter(
                pk=self.instance.appointment_id
            )
        else:
            queryset = queryset.exclude(
                prescription__isnull=False
            )

        self.fields["appointment"].queryset = queryset.distinct()

    def clean(self):
        cleaned_data = super().clean()
        follow_up_required = cleaned_data.get("follow_up_required")
        follow_up_date = cleaned_data.get("follow_up_date")

        if follow_up_required and not follow_up_date:
            raise ValidationError("Please select a follow-up date.")

        return cleaned_data


class PrescriptionSearchForm(forms.Form):
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
    diagnosis = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Diagnosis",
            }
        ),
    )
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )