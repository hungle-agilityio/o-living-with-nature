"""Epic review fixes (epic #104)."""

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
