"""Epic review fixes (epic #104)."""

import json

import pytest
from django.test import Client, RequestFactory
from django.utils import translation
from django.utils.safestring import SafeString

from pages import language
from pages.context_processors import page_language
from pages.photos import PHOTOS
from pages.templatetags.texts import alt_text, credit_text


def test_empty_lang_means_english_even_when_vi_is_active() -> None:
    photo = next(p for p in PHOTOS.values() if p.alt_vi)
    with translation.override("vi"):
        assert alt_text(photo, "") == photo.alt
        assert credit_text("Photo: X", "") == "Photo: X"


def test_explicit_lang_is_kept() -> None:
    photo = next(p for p in PHOTOS.values() if p.alt_vi)
    assert alt_text(photo, "vi") == photo.alt_vi
    assert alt_text(photo, "en") == photo.alt
    assert credit_text("Photo: X", "vi") != "Photo: X"


@pytest.mark.django_db
@pytest.mark.parametrize(("path", "label"), [("/", "Language"), ("/vi/", "Ngôn ngữ")])
def test_language_switch_is_a_named_group(client: Client, path: str, label: str) -> None:
    # aria-label on a plain <p> is not announced; a group role carries the name (AC6).
    html = client.get(path).content.decode()
    assert f'<p class="lang-switch label" role="group" aria-label="{label}">' in html


def test_daypart_labels_are_plain_json_left_to_autoescape(rf: RequestFactory) -> None:
    # The template's autoescape escapes the attribute; no hand-written escaper, no mark_safe.
    value = page_language(rf.get("/vi/"))["daypart_labels"]
    assert isinstance(value, str)
    assert not isinstance(value, SafeString)
    assert json.loads(value) == json.loads(language.daypart_labels("vi"))


@pytest.mark.django_db
def test_daypart_labels_attribute_is_escaped_by_the_template(client: Client) -> None:
    html = client.get("/vi/").content.decode()
    assert "data-labels='{&quot;dawn&quot;:" in html
