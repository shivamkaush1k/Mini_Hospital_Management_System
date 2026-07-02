import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_phone(value):

    pattern = r"^\+?\d{10,15}$"

    if not re.match(pattern, value):
        raise ValidationError(
            "Invalid phone number."
        )


def validate_future_date(value):

    if value <= timezone.localdate():

        raise ValidationError(
            "Date must be in future."
        )


def validate_not_future(value):

    if value > timezone.localdate():

        raise ValidationError(
            "Future date not allowed."
        )


def validate_positive(value):

    if value < 0:
        raise ValidationError(
            "Value cannot be negative."
        )