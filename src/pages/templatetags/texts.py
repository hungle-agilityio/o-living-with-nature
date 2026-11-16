"""`{% text "shell" "key" name=value %}`, `{{ photo|alt_text:lang }}` and
`{{ credit|credit_text:lang }}`: the texts of the page in its language."""

from django import template
from django.utils.safestring import SafeString, mark_safe

from pages import language
from pages.photos import AreaLoop, Photo

register = template.Library()


def _escape(value: str) -> str:
    # `'` stays as written: a text such as "isn't" is read as it is.
    return (
        value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


@register.simple_tag(takes_context=True)
def text(context: template.Context, part: str, key: str, **values: object) -> SafeString:
    """The text of `key` in the language of the page; each `{name}` is replaced by the value
    given as `name=...`. Everything is escaped."""
    words = language.texts(part, language.of_context(context))
    result = _escape(words[key])
    for name, value in values.items():
        result = result.replace("{" + name + "}", _escape(str(value)))
    return mark_safe(result)  # noqa: S308 (escaped above)


@register.filter
def alt_text(entry: Photo | AreaLoop, lang: str = "") -> str:
    """The alt text of a photo (or label of the loop), Vietnamese on `/vi/` when it has one."""
    english: str = entry.alt if isinstance(entry, Photo) else entry.label
    vietnamese: str = entry.alt_vi if isinstance(entry, Photo) else entry.label_vi
    return (
        vietnamese
        if language.normalise(lang or language.current()) == "vi" and vietnamese
        else english
    )


@register.filter
def credit_text(credit: str, lang: str = "") -> str:
    """A credit in the page language (`Photo: ` becomes `Ảnh: ` on `/vi/`)."""
    return language.credit_for(str(credit), lang or language.current())
