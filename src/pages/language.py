"""The language of a page and its texts: English at `/`, Vietnamese at `/vi/`."""

import importlib
import json
from collections.abc import Mapping
from types import ModuleType
from typing import Any

from django.http import HttpRequest
from django.template import Context
from django.utils.translation import get_language

EN = "en"
VI = "vi"

_PATHS = {EN: "/", VI: "/vi/"}
_CONTACT_PATHS = {EN: "/contact/", VI: "/vi/#contact"}
_OTHER = {EN: VI, VI: EN}
_THEMES = ("dawn", "day", "dusk", "night")


def normalise(code: str | None) -> str:
    """`"vi"` for Vietnamese, `"en"` for anything else."""
    return VI if code is not None and code.lower().split("-")[0] == VI else EN


def current() -> str:
    """The language active now: `"vi"` or `"en"`."""
    return normalise(get_language())


def of_request(request: HttpRequest) -> str:
    """The language the middleware chose for this request (from the address)."""
    code = getattr(request, "LANGUAGE_CODE", None)
    return normalise(code) if code else current()


def of_context(context: Context | Mapping[str, Any]) -> str:
    """The language of a template context: the request's, else its `lang`, else English."""
    request = context.get("request")
    code = getattr(request, "LANGUAGE_CODE", None) or context.get("lang")
    return normalise(code)


def texts(part: str, lang: str | None = None) -> dict[str, str]:
    """The dictionary of `pages.texts.<part>` for `lang` (default: the current language)."""
    module = importlib.import_module(f"pages.texts.{part}")
    result: dict[str, str] = module.VI if normalise(lang or current()) == VI else module.EN
    return result


def missing_keys(module: ModuleType) -> set[str]:
    """The keys present in one of `EN` and `VI` of the module and not in the other."""
    return set(module.EN) ^ set(module.VI)


def home_path(lang: str) -> str:
    return _PATHS[normalise(lang)]


def contact_path(lang: str) -> str:
    return _CONTACT_PATHS[normalise(lang)]


def switch(lang: str) -> dict[str, str]:
    """The language switch: the current language (not a link) and the link to the other."""
    code = normalise(lang)
    other = _OTHER[code]
    return {
        "current": code.upper(),
        "label": texts("shell", code)["switch_label"],
        "lang": other,
        "href": _PATHS[other],
        "name": other.upper(),
    }


def credit_for(credit: str, lang: str) -> str:
    """A credit in the page language: a leading `Photo: ` becomes `Ảnh: ` in Vietnamese."""
    if normalise(lang) == EN:
        return credit
    english = texts("shell", EN)["credit_photo"]
    if credit.startswith(english):
        return texts("shell", VI)["credit_photo"] + credit[len(english) :]
    return credit


def daypart_labels(lang: str) -> str:
    """The labels of the four themes as JSON; the template's autoescape makes it safe to show."""
    words = texts("shell", lang)
    return json.dumps({name: words[f"daypart_{name}"] for name in _THEMES}, ensure_ascii=False)
