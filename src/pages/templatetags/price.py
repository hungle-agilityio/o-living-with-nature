"""`{{ owner.price_line|price_accents }}`: the price line with "million" and "a month" in the
accent (design-match design.md, "03 ở lâu"). The text itself stays as written."""

import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

_ACCENT_WORDS = re.compile(r"\b(million|a month)\b")


@register.filter
def price_accents(line: str | None) -> SafeString:
    """The escaped line, each accent word wrapped in `<span class="accent">`; empty for None."""
    if not line:
        return mark_safe("")
    escaped = str(conditional_escape(line))
    return mark_safe(_ACCENT_WORDS.sub(r'<span class="accent">\1</span>', escaped))  # noqa: S308
