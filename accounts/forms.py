from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class UserRegisterForm(UserCreationForm):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Email already exists."
            )

        return email


class UserUpdateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = (
            "first_name",
            "last_name",
            "email",
        )

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }


class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = (

            "role",

            "image",

            "phone",

            "gender",

            "date_of_birth",

            "address",

            "city",

            "state",

            "country",

            "pincode",

        )

        widgets = {

            "role": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "country": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "pincode": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }


class LoginForm(forms.Form):

    username = forms.CharField(

        widget=forms.TextInput(

            attrs={
                "class": "form-control"
            }

        )

    )

    password = forms.CharField(

        widget=forms.PasswordInput(

            attrs={
                "class": "form-control"
            }

        )

    )