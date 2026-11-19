"""The phone contact bar shows the buttons once (issue #142; mobile-smoothness AC7 to AC18)."""

import re

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

CONTACT_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "contact.css"
SCRIPT = settings.SRC_DIR / "static" / "js" / "contact-bar.js"
NOSCRIPT = "<noscript><style>.contact-bar { transform: none !important; }</style></noscript>"


def _page(client: Client, path: str = "/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _no_channels() -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")


def _phone_part(css: str) -> str:
    parts = css.split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no phone rules"
    return parts[1].split("@media (prefers-reduced-motion", 1)[0]


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


# M9: the script watches every set of contact buttons


def test_script_watches_chapter_02_and_the_form() -> None:
    script = _script()

    assert 'getElementById("hoa-xuan")' in script
    assert 'querySelector("form.enquiry-form")' in script
    assert '"focusin"' in script
    assert '"focusout"' in script
    assert 'getElementById("hero")' not in script
    assert 'querySelectorAll(".contact-buttons")' not in script
    assert "IntersectionObserver" in script
    assert "contact-bar--away" in script


def test_script_uses_one_observer_for_all_watched_elements() -> None:
    script = _script()

    assert script.count("new IntersectionObserver") == 1


# M11: no flash before the first check, and the bar shows without JavaScript


def test_phone_css_keeps_the_bar_out_of_view_until_the_script_is_ready() -> None:
    phone = _phone_part(CONTACT_CSS.read_text(encoding="utf-8"))

    match = re.search(r"html:not\(\.contact-bar-ready\)\s+\.contact-bar\s*\{([^}]*)\}", phone)
    assert match, "no html:not(.contact-bar-ready) .contact-bar rule in the phone block"
    assert "transform: translateY(110%)" in match.group(1)


def test_script_marks_the_page_ready_and_does_so_when_observer_is_missing() -> None:
    script = _script()

    assert "contact-bar-ready" in script
    assert "document.documentElement" in script
    missing = re.search(r"!\s*window\.IntersectionObserver|typeof\s+IntersectionObserver", script)
    assert missing, "the script does not test for a missing IntersectionObserver"
    # The ready class is added in the missing-observer branch, before the observer is created.
    assert "contact-bar-ready" in script[: script.index("new IntersectionObserver")]


def test_observer_callback_marks_the_page_ready() -> None:
    script = _script()
    callback = script[script.index("new IntersectionObserver") :]

    # The bar shows only after the script's first check (AC2, AC3): the callback adds the class.
    assert 'document.documentElement.classList.add("contact-bar-ready")' in callback


def test_missing_observer_marks_the_page_ready_at_once() -> None:
    script = _script()
    branch = re.search(r"if \(!window\.IntersectionObserver\) \{(.*?)\}", script, re.S)

    # Without IntersectionObserver the bar shows at once (AC3), as it does without the script.
    assert branch, "no branch for a missing IntersectionObserver"
    assert 'document.documentElement.classList.add("contact-bar-ready")' in branch.group(1)
    assert "return" in branch.group(1)


def test_home_holds_the_noscript_style_before_the_end_of_the_head(client: Client) -> None:
    html = _page(client)

    assert html.count(NOSCRIPT) == 1
    assert html.index(NOSCRIPT) < html.index("</head>")


def test_nav_markup_is_unchanged(client: Client) -> None:
    assert '<nav class="contact-bar" aria-label="Contact">' in _page(client)
    assert '<nav class="contact-bar" aria-label="Liên hệ">' in _page(client, "/vi/")


def test_script_is_under_4000_bytes() -> None:
    assert len(_script().encode()) < 4_000


# M12: no channel, nothing of the bar


def test_no_channel_means_no_bar_no_script_and_no_noscript(client: Client) -> None:
    _no_channels()

    html = _page(client)

    assert "contact-bar" not in html
    assert "contact-bar.js" not in html
    assert "<noscript>" not in html


# M21: still one query


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_home_pages_make_one_query_each(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        _page(client, path)
