"""`{% enquiry_error form "name" %}` and `{% enquiry_summary form %}`: the lines the enquiry
form shows after a refused post, in the language of the page."""

from django import forms, template
from django.utils.safestring import SafeString, mark_safe

from pages import language

# The one escaping of the page texts; importing the private helper keeps a single rule.
from pages.templatetags.texts import _escape

register = template.Library()

_REQUIRED = {"name": "error_name", "reply_to": "error_reply_empty", "message": "error_message"}
_WRONG = {
    "name": "error_name",
    "message": "error_message",
    "reply_to": "error_reply_invalid",
    "move_in": "error_choice",
    "stay": "error_choice",
}


def error_text(form: forms.Form, field: str, lang: str) -> str:
    """The first error of `field` as a line in `lang`, or "" when it has none."""
    errors = form.errors.as_data().get(field)
    if not errors:
        return ""
    code = errors[0].code
    words = language.texts("enquiry", lang)
    if code == "required" and field in _REQUIRED:
        return words[_REQUIRED[field]]
    if code == "invalid_reply":
        return words["error_reply_invalid"]
    if code == "max_length":
        limit = getattr(form.fields[field], "max_length", None)
        return words["error_too_long"].replace("{n}", str(limit))
    if code == "invalid_choice":
        return words["error_choice"]
    return words[_WRONG.get(field, "error_choice")]


def summary_text(form: forms.Form, lang: str) -> str:
    """ "1 thing needs a look" or "{n} things need a look", n being the fields in error."""
    words = language.texts("enquiry", lang)
    count = len(form.errors)
    if count == 1:
        return words["summary_one"]
    return words["summary_many"].replace("{n}", str(count))


@register.simple_tag(takes_context=True)
def enquiry_error(context: template.Context, form: forms.Form, field: str) -> SafeString:
    return mark_safe(  # noqa: S308 (escaped)
        _escape(error_text(form, field, language.of_context(context)))
    )


@register.simple_tag(takes_context=True)
def enquiry_summary(context: template.Context, form: forms.Form) -> SafeString:
    return mark_safe(  # noqa: S308 (escaped)
        _escape(summary_text(form, language.of_context(context)))
    )
