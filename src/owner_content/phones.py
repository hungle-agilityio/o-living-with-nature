"""Vietnamese phone numbers as the owner types them: the one rule for what is valid."""

import re

from django.core.exceptions import ValidationError

PHONE_ERROR = "Enter a Vietnamese number like 0945 384 500 or +84 945 384 500."

# An optional +84 or 0, then 9 to 11 digits; only spaces, dots or dashes between them.
# Digits are 0 to 9 only: a full-width or Arabic digit would give a link that does not dial.
_NUMBER = re.compile(r"(?:\+84|0)?((?:[ .-]*[0-9]){9,11})")
_SEPARATORS = re.compile(r"[ .-]")


def national_number(raw: str) -> str | None:
    """The digits after the +84 or the 0 (`945384500`), or None when the number is not valid."""
    match = _NUMBER.fullmatch(raw.strip())
    return _SEPARATORS.sub("", match.group(1)) if match else None


def validate_vietnamese_number(value: str) -> None:
    if national_number(value) is None:
        raise ValidationError(PHONE_ERROR, code="invalid")
