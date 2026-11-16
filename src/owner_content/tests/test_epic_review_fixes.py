"""Epic review fixes (epic #104): the owner's lines follow any spelling of Vietnamese."""

import pytest

from owner_content.services import site_settings


@pytest.mark.django_db
@pytest.mark.parametrize("code", ["vi", "vi-VN", "VI", "vi-vn"])
def test_vietnamese_codes_give_vietnamese_lines(code: str) -> None:
    assert site_settings(code).greeting == site_settings("vi").greeting
    assert site_settings(code).greeting.startswith("Chào bạn")


@pytest.mark.django_db
@pytest.mark.parametrize("code", ["en", "en-US", "", "fr"])
def test_other_codes_give_english_lines(code: str) -> None:
    assert site_settings(code).greeting.startswith("Hi, I'm")
