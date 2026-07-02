from django import forms
from django.core.exceptions import ValidationError

from .models import Patient, MedicalHistory


class PatientForm(forms.ModelForm):

    class Meta:

        model = Patient

        fields = (

            "blood_group",

            "height",

            "weight",

            "allergies",

            "emergency_contact_name",

            "emergency_contact_phone",

            "insurance_provider",

            "insurance_number",

        )

        widgets = {

            "blood_group": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "height": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Height (cm)"
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Weight (kg)"
                }
            ),

            "allergies": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Mention allergies if any"
                }
            ),

            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Emergency Contact Name"
                }
            ),

            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Emergency Contact Phone"
                }
            ),

            "insurance_provider": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Insurance Provider"
                }
            ),

            "insurance_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Insurance Number"
                }
            ),

        }

    def clean_height(self):

        height = self.cleaned_data["height"]

        if height <= 0:
            raise ValidationError(
                "Height must be greater than zero."
            )

        return height

    def clean_weight(self):

        weight = self.cleaned_data["weight"]

        if weight <= 0:
            raise ValidationError(
                "Weight must be greater than zero."
            )

        return weight


class MedicalHistoryForm(forms.ModelForm):

    class Meta:

        model = MedicalHistory

        fields = (

            "doctor",

            "visit_date",

            "diagnosis",

            "treatment",

            "notes",

        )

        widgets = {

            "doctor": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "visit_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "diagnosis": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "treatment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

        }


class PatientSearchForm(forms.Form):

    search = forms.CharField(

        required=False,

        widget=forms.TextInput(

            attrs={
                "class": "form-control",
                "placeholder": "Search by name or email"
            }

        )

    )

    blood_group = forms.ChoiceField(

        required=False,

        choices=[("", "All Blood Groups")] +
        list(Patient.BloodGroup.choices),

        widget=forms.Select(

            attrs={
                "class": "form-select"
            }

        )

    )