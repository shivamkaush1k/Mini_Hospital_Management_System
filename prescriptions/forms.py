from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Prescription, PrescriptionMedicine


class PrescriptionForm(forms.ModelForm):
    """
    `appointment` is never exposed as a field here -- it's fixed by the
    URL the doctor arrived from (`prescriptions:prescription_create`)
    and assigned directly on the instance in the view, the same way
    `record.patient` is set in `patients.views.add_medical_record`.
    """

    class Meta:
        model = Prescription
        fields = (
            "diagnosis",
            "advice",
            "follow_up_required",
            "follow_up_date",
        )

        widgets = {
            "diagnosis": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Diagnosis"}
            ),
            "advice": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Advice for the patient"}
            ),
            "follow_up_required": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "follow_up_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def clean_follow_up_date(self):
        follow_up_date = self.cleaned_data.get("follow_up_date")

        if follow_up_date and follow_up_date < timezone.localdate():
            raise forms.ValidationError("Follow-up date cannot be before today.")

        return follow_up_date

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("follow_up_required") and not cleaned_data.get("follow_up_date"):
            raise forms.ValidationError(
                "Please provide a follow-up date since follow-up is marked as required."
            )

        return cleaned_data


class PrescriptionMedicineForm(forms.ModelForm):
    class Meta:
        model = PrescriptionMedicine
        fields = ("name", "dosage", "frequency", "duration", "instructions")

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Medicine name"}
            ),
            "dosage": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. 500mg"}
            ),
            "frequency": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Twice a day"}
            ),
            "duration": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. 5 days"}
            ),
            "instructions": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. After food"}
            ),
        }


PrescriptionMedicineFormSet = inlineformset_factory(
    Prescription,
    PrescriptionMedicine,
    form=PrescriptionMedicineForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class PrescriptionSearchForm(forms.Form):

    patient = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Patient Name"}
        ),
    )

    doctor = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Doctor Name"}
        ),
    )

    follow_up_required = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )