from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Doctor, DoctorSlot


class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor

        fields = (
            "specialization",
            "qualification",
            "experience",
            "consultation_fee",
            "department",
            "license_number",
            "room_number",
            "bio",
            "rating",
            "is_active",
        )

        widgets = {
            "specialization": forms.Select(
                attrs={"class": "form-select"}
            ),

            "qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "MBBS, MD, MS..."
                }
            ),

            "experience": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0
                }
            ),

            "consultation_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "department": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "license_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "room_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": 0,
                    "max": 5
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def clean_experience(self):
        experience = self.cleaned_data["experience"]

        if experience < 0:
            raise ValidationError(
                "Experience cannot be negative."
            )

        return experience

    def clean_consultation_fee(self):
        fee = self.cleaned_data["consultation_fee"]

        if fee <= 0:
            raise ValidationError(
                "Consultation fee must be greater than zero."
            )

        return fee

    def clean_rating(self):
        rating = self.cleaned_data["rating"]

        if rating < 0 or rating > 5:
            raise ValidationError(
                "Rating must be between 0 and 5."
            )

        return rating

class DoctorSlotForm(forms.ModelForm):

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor

    class Meta:
        model = DoctorSlot

        fields = (
            "date",
            "start_time",
            "end_time",
            "consultation_duration",
            "buffer_duration",
            "is_active",
        )

        widgets = {

            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "consultation_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "buffer_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        consultation = cleaned_data.get("consultation_duration")
        buffer = cleaned_data.get("buffer_duration")

        if date and date < timezone.localdate():
            raise ValidationError(
                "Slot date cannot be in the past."
            )

        if start and end and start >= end:
            raise ValidationError(
                "End time must be after start time."
            )

        if consultation is not None and consultation <= 0:
            raise ValidationError(
                "Consultation duration must be greater than zero."
            )

        if buffer is not None and buffer < 0:
            raise ValidationError(
                "Buffer duration cannot be negative."
            )

        doctor = self.doctor

        if doctor and date and start and end:

            qs = DoctorSlot.objects.filter(
                doctor=doctor,
                date=date,
                start_time__lt=end,
                end_time__gt=start,
            )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    "This working session overlaps with another session."
                )

        return cleaned_data
    
class DoctorSearchForm(forms.Form):

    specialization = forms.ChoiceField(
        required=False,
        choices=[("", "All Specializations")] + list(Doctor.Specialization.choices),
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        ),
    )

    department = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Department"
            }
        ),
    )

    min_experience = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 0
            }
        ),
    )

    max_fee = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control"
            }
        ),
    )

    available_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input"
            }
        ),
    )