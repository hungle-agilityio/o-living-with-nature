"""The enquiry form and the `?enquiry=` state of the home page.

The error codes (`required`, `max_length`, `invalid_choice`, `invalid_reply`) are what the page
turns into the visitor's texts; the messages of this form are never shown as they are.
"""

import re
from datetime import date
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from enquiries.models import Stay
from enquiries.months import NOT_SURE, STAY_LABELS, month_label, move_in_months

# What a phone number may hold besides its digits: spaces, +, -, . and brackets.
_PHONE_PUNCTUATION = re.compile(r"[ +\-.()]")


def _is_phone(value: str) -> bool:
    digits = _PHONE_PUNCTUATION.sub("", value)
    return digits.isascii() and digits.isdigit() and 8 <= len(digits) <= 15


def _is_email(value: str) -> bool:
    try:
        validate_email(value)
    except ValidationError:
        return False
    return True


class MessageField(forms.CharField):
    """A browser sends a textarea's line break as CRLF; count it as the one the visitor typed."""

    def to_python(self, value: Any) -> str:
        if isinstance(value, str):
            value = value.replace("\r\n", "\n")
        return super().to_python(value) or ""


class EnquiryForm(forms.Form):
    name = forms.CharField(max_length=80, strip=True)
    reply_to = forms.CharField(max_length=120, strip=True)
    move_in = forms.ChoiceField(required=False)
    stay = forms.ChoiceField(required=False)
    message = MessageField(max_length=1000, strip=True, widget=forms.Textarea)
    website = forms.CharField(required=False)  # the trap: people leave it empty

    def __init__(self, data: Any = None, *, language: str, today: date) -> None:
        super().__init__(data)
        not_sure = ("", NOT_SURE[language])
        move_in = self.fields["move_in"]
        stay = self.fields["stay"]
        assert isinstance(move_in, forms.ChoiceField)
        assert isinstance(stay, forms.ChoiceField)
        move_in.choices = [not_sure] + [
            (value, month_label(value, language)) for value in move_in_months(today)
        ]
        labels = STAY_LABELS[language]
        stay.choices = [not_sure] + [(value, labels[value]) for value in Stay.values]

    def clean_reply_to(self) -> str:
        value: str = self.cleaned_data["reply_to"]
        if _is_email(value) or _is_phone(value):
            return value
        raise ValidationError("Enter an email address or a phone number.", code="invalid_reply")


class EnquiryStateForm(forms.Form):
    """`?enquiry=` of the home page: only `sent` means something."""

    enquiry = forms.ChoiceField(choices=[("sent", "sent")], required=False)
