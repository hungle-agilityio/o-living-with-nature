"""Epic review fixes (epic #104)."""

import pytest
from django.test import Client
from django.utils import translation

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
