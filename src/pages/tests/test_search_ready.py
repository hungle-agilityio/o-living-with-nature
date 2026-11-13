"""The home page ready for Google Search Console (issue #97; search-ready AC1 to AC12)."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

from owner_content.models import SiteSettings
from owner_content.services import site_settings
from pages import seo

pytestmark = pytest.mark.django_db

SRC = Path(settings.SRC_DIR)
RENDER_YAML = SRC.parent / "render.yaml"
VERIFICATION = "abc123-XYZ_9"
TAG = re.compile(r'<meta name="google-site-verification"[^>]*>')
LD_OPEN = '<script type="application/ld+json">'
SITE_NAME_TAG = re.compile(r'<meta property="og:site_name" content="[^"]*">\s*')
BASE = "https://o.example"
PROBE = (
    "import json; from django.conf import settings; "
    "print(json.dumps(settings.GOOGLE_SITE_VERIFICATION))"
)


def _setting_in_fresh_process(**extra: str) -> str:
    """The settings are read once per process, so each case loads them in a fresh one."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("DJANGO_") and key not in {"PYTHONPATH", "GOOGLE_SITE_VERIFICATION"}
    }
    env.update({"DJANGO_SETTINGS_MODULE": "config.settings", "PYTHONPATH": str(SRC), **extra})
    done = subprocess.run(
        [sys.executable, "-c", PROBE], env=env, capture_output=True, text=True, check=True
    )
    value = json.loads(done.stdout.strip().splitlines()[-1])
    assert isinstance(value, str)
    return value


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _head(html: str) -> str:
    match = re.search(r"<head\b.*?</head>", html, re.DOTALL)
    assert match, "no <head> in the page"
    return match.group(0)


def _blocks(html: str) -> list[str]:
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)


def _data(html: str) -> dict[str, object]:
    blocks = _blocks(html)
    assert len(blocks) == 1
    data = json.loads(blocks[0])
    assert isinstance(data, dict)
    return data


def _set_owner(
    price_from: int | None = 13,
    price_to: int | None = 14,
    phone: str = "0905 123 456",
    zalo: str = "",
) -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        price_from_million=price_from, price_to_million=price_to, phone=phone, zalo=zalo
    )


def _not_found(client: Client, settings: Settings) -> str:
    settings.DEBUG = False
    response = client.get("/this-page-does-not-exist/")
    assert response.status_code == 404
    return response.content.decode()


def _login(client: Client) -> str:
    response = client.get("/owner/login/")
    assert response.status_code == 200
    return response.content.decode()


# AC1


def test_setting_is_read_from_the_environment_without_surrounding_spaces() -> None:
    assert _setting_in_fresh_process(GOOGLE_SITE_VERIFICATION=" abc123 ") == "abc123"


def test_setting_is_empty_when_the_variable_is_unset_or_blank() -> None:
    assert _setting_in_fresh_process() == ""
    assert _setting_in_fresh_process(GOOGLE_SITE_VERIFICATION="") == ""
    assert _setting_in_fresh_process(GOOGLE_SITE_VERIFICATION="   ") == ""


# AC2 to AC4


def test_home_has_exactly_one_verification_tag_with_the_value(
    client: Client, settings: Settings
) -> None:
    settings.GOOGLE_SITE_VERIFICATION = VERIFICATION

    html = _home(client)

    assert TAG.findall(_head(html)) == [
        f'<meta name="google-site-verification" content="{VERIFICATION}">'
    ]
    assert html.count("google-site-verification") == 1


def test_home_has_no_verification_tag_when_the_setting_is_empty(
    client: Client, settings: Settings
) -> None:
    settings.GOOGLE_SITE_VERIFICATION = ""

    assert "google-site-verification" not in _home(client)


def test_verification_value_is_escaped_and_adds_no_script_tag(
    client: Client, settings: Settings
) -> None:
    settings.GOOGLE_SITE_VERIFICATION = ""
    scripts_without_tag = _home(client).count("<script")
    settings.GOOGLE_SITE_VERIFICATION = 'a"><script>'

    html = _home(client)

    assert TAG.findall(html) == [
        '<meta name="google-site-verification" content="a&quot;&gt;&lt;script&gt;">'
    ]
    assert html.count("<script") == scripts_without_tag


# AC5


def test_not_found_and_login_pages_have_no_verification_tag(
    client: Client, settings: Settings
) -> None:
    settings.GOOGLE_SITE_VERIFICATION = "abc123"

    assert "google-site-verification" not in _not_found(client, settings)
    assert "google-site-verification" not in _login(client)


# AC6


def test_render_yaml_lists_the_verification_variable_as_set_by_hand() -> None:
    lines = [line.strip() for line in RENDER_YAML.read_text(encoding="utf-8").splitlines()]

    index = lines.index("- key: GOOGLE_SITE_VERIFICATION")
    assert lines[index + 1] == "sync: false"


# AC7


def test_home_has_one_structured_data_block_right_after_the_site_name_tag(client: Client) -> None:
    _set_owner()
    html = _home(client)

    assert len(_blocks(_head(html))) == 1
    assert len(_blocks(html)) == 1
    match = SITE_NAME_TAG.search(html)
    assert match
    assert html[match.end() :].startswith(LD_OPEN)


def test_structured_data_describes_the_house_exactly(client: Client, settings: Settings) -> None:
    settings.SITE_BASE_URL = BASE
    _set_owner()

    assert _data(_home(client)) == {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "name": "Ở — Living with Nature",
        "description": seo.PAGES["home"].description,
        "url": BASE + "/",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Hòa Xuân",
            "addressRegion": "Đà Nẵng",
            "addressCountry": "VN",
        },
        "priceRange": "From 13–14 million VND a month",
        "telephone": "+84905123456",
    }


def test_structured_data_matches_the_meta_description_and_canonical_link(client: Client) -> None:
    _set_owner()
    html = _home(client)
    data = _data(html)

    description = re.search(r'<meta name="description" content="([^"]*)">', html)
    canonical = re.search(r'<link rel="canonical" href="([^"]*)">', html)
    assert description and canonical
    assert data["description"] == description.group(1)
    assert data["url"] == canonical.group(1)


# AC8


def test_structured_data_has_no_price_range_without_a_price(client: Client) -> None:
    _set_owner(price_from=None, price_to=None)

    data = _data(_home(client))

    assert "priceRange" not in data
    assert data["telephone"] == "+84905123456"


def test_structured_data_has_no_telephone_without_a_call_number(client: Client) -> None:
    _set_owner(phone="", zalo="0945 384 500")

    data = _data(_home(client))

    assert "telephone" not in data
    assert data["priceRange"] == "From 13–14 million VND a month"


def test_structured_data_is_still_there_without_a_settings_record(client: Client) -> None:
    SiteSettings.objects.all().delete()

    data = _data(_home(client))

    assert data["@type"] == "LodgingBusiness"
    assert data["name"] == "Ở — Living with Nature"
    assert data["address"]
    assert "priceRange" not in data
    assert "telephone" not in data


# AC9


def test_structured_data_has_nothing_that_is_not_real_yet(client: Client) -> None:
    _set_owner()

    data = _data(_home(client))

    for key in ("image", "geo", "aggregateRating", "review"):
        assert key not in data
    address = data["address"]
    assert isinstance(address, dict)
    assert "streetAddress" not in address
    assert "postalCode" not in address


# AC10


def _head_with(description: str) -> seo.Head:
    return seo.Head(
        title="T", description=description, canonical=BASE + "/", robots=seo.ROBOTS_NOINDEX
    )


def test_structured_data_text_cannot_close_the_script() -> None:
    description = "</script><b>&"

    text = seo.structured_data(_head_with(description), site_settings())

    for char in "<>&":
        assert char not in text
    assert json.loads(text)["description"] == description


def test_structured_data_keeps_vietnamese_letters_readable() -> None:
    text = seo.structured_data(_head_with("x"), site_settings())

    assert "Ở — Living with Nature" in text
    assert "Hòa Xuân" in text


# AC11


def test_home_makes_exactly_one_query_with_the_structured_data(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    _set_owner()

    with django_assert_num_queries(1):
        response = client.get("/")

    assert response.status_code == 200
    assert len(_blocks(response.content.decode())) == 1


# AC12


def test_not_found_and_login_pages_have_no_structured_data(
    client: Client, settings: Settings
) -> None:
    assert "application/ld+json" not in _not_found(client, settings)
    assert "application/ld+json" not in _login(client)


@pytest.mark.parametrize("indexing", [True, False])
def test_home_has_the_structured_data_with_indexing_on_and_off(
    client: Client, settings: Settings, indexing: bool
) -> None:
    settings.INDEXING_ENABLED = indexing

    assert len(_blocks(_home(client))) == 1
