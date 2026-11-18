"""The full-screen photo viewer of the home page (issue #156, AC1 to AC5)."""

import re

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings
from pages.texts import shell

pytestmark = pytest.mark.django_db

CSS_PATH = settings.SRC_DIR / "static" / "css" / "photo-viewer.css"
JS_PATH = settings.SRC_DIR / "static" / "js" / "photo-viewer.js"
SCRIPT_TAG = '<script src="/static/js/photo-viewer.js" defer></script>'
LINK_TAG = '<link rel="stylesheet" href="/static/css/photo-viewer.css">'
CONTACT_LINK = "/static/css/chapters/contact.css"

LABELS = {
    "/": {
        "label": "Photo viewer",
        "open": "Open photo full screen: ",
        "close": "Close",
        "previous": "Previous photo",
        "next": "Next photo",
    },
    "/vi/": {
        "label": "Xem ảnh",
        "open": "Mở ảnh toàn màn hình: ",
        "close": "Đóng",
        "previous": "Ảnh trước",
        "next": "Ảnh sau",
    },
}


def _page(client: Client, path: str = "/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def _js() -> str:
    return JS_PATH.read_text(encoding="utf-8")


def _rule(css: str, selector: str) -> str:
    match = re.search(r"(?:^|[\s}])" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert match, f"no rule for {selector}"
    return match.group(1)


def _check_dialog(html: str, path: str) -> None:
    t = LABELS[path]
    assert html.count('<dialog class="viewer"') == 1
    start = html.index('<dialog class="viewer"')
    dialog = html[start : html.index("</dialog>", start)]
    assert f'aria-label="{t["label"]}"' in dialog
    assert f'data-open-label="{t["open"]}"' in dialog
    assert '<div class="viewer__top">' in dialog
    assert '<span class="viewer__count" aria-live="polite"></span>' in dialog
    assert f'class="viewer__close" aria-label="{t["close"]}"' in dialog
    assert '<div class="viewer__track"></div>' in dialog
    assert '<div class="viewer__bottom">' in dialog
    assert f'data-step="-1" aria-label="{t["previous"]}"' in dialog
    assert f'data-step="1" aria-label="{t["next"]}"' in dialog


# M1, M2: the page carries the dialog, the script and the stylesheet once


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_home_page_holds_one_viewer_dialog_in_the_page_language(client: Client, path: str) -> None:
    """M1 (English) and M2 (Vietnamese)."""
    html = _page(client, path)

    _check_dialog(html, path)
    dialog_at = html.index('<dialog class="viewer"')
    assert html.index('id="contact"') < dialog_at < html.index('class="contact-bar"')
    assert html.count(SCRIPT_TAG) == 1
    assert html.index(SCRIPT_TAG) > dialog_at
    assert "<script" not in html[dialog_at : html.index(SCRIPT_TAG)]
    assert html.count(LINK_TAG) == 1
    assert html.index(LINK_TAG) > html.index(CONTACT_LINK)


# M3: no owner channel


def test_viewer_is_still_there_once_without_owner_channels(client: Client) -> None:
    """M3."""
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")
    html = _page(client)

    assert 'class="contact-bar"' not in html
    assert html.count('<dialog class="viewer"') == 1
    assert html.count(SCRIPT_TAG) == 1
    assert html.index('<dialog class="viewer"') < html.index(SCRIPT_TAG)
    assert html.index(SCRIPT_TAG) < html.index("/static/js/lang-switch.js")


# M4: one query, the photo slots are untouched


@pytest.mark.parametrize("path", ["/", "/vi/"])
def test_home_pages_make_one_query_and_leave_photo_slots_plain(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    """M4."""
    with django_assert_num_queries(1):
        html = _page(client, path)

    dialog_at = html.index('<dialog class="viewer"')
    outside = html[:dialog_at] + html[html.index("</dialog>", dialog_at) :]
    assert "photo-open" not in outside
    boxes = re.findall(r'<[^>]*class="[^"]*media__box[^"]*"[^>]*>', outside)
    assert boxes
    for box in boxes:
        assert "role=" not in box


# M5: the stylesheet


def test_stylesheet_holds_the_rules_and_values() -> None:
    """M5."""
    css = _css()

    assert "display: none" in _rule(css, ".viewer:not([open])")
    opened = _rule(css, ".viewer[open]")
    assert "position: fixed" in opened
    assert "inset: 0" in opened
    assert "rgba(12, 13, 11, 0.96)" in _rule(css, ".viewer")
    assert "rgba(12, 13, 11, 0.96)" in _rule(css, ".viewer::backdrop")
    slide = _rule(css, ".viewer__slide")
    assert "margin: 0" in slide
    assert "scroll-snap-align: center" in slide
    assert "scroll-snap-type: x mandatory" in _rule(css, ".viewer__track")
    assert "object-fit: contain" in css
    assert "cursor: zoom-in" in _rule(css, ".photo-open")
    phone = css.split("@media (max-width: 760px)", 1)
    assert len(phone) == 2, "no phone rules"
    assert re.search(r"\.viewer__step\s*\{[^}]*display:\s*none", phone[1])
    assert ".viewer--single" in css
    assert "visibility: hidden" in css
    reduced = css.split("@media (prefers-reduced-motion: reduce)", 1)
    assert len(reduced) == 2, "no reduced-motion rule"
    assert "animation" in reduced[1]
    assert "100vw" not in css


# M6: the script opens the viewer


def test_script_holds_the_groups_and_the_opening_behaviour() -> None:
    """M6."""
    script = _js()

    groups = [".house__collage", ".hoa-xuan__photos", ".rent__photo"]
    positions = [script.find(g) for g in groups]
    assert all(p >= 0 for p in positions)
    assert positions == sorted(positions)
    for word in (
        "photo-open",
        "role",
        "tabindex",
        "data-open-label",
        "Enter",
        "showModal",
        "history.pushState",
        "viewer--single",
        "ArrowLeft",
        "ArrowRight",
        "prefers-reduced-motion",
    ):
        assert word in script, word


# M7: nothing is added without a dialog or showModal


def test_script_returns_before_adding_anything_without_dialog_or_show_modal() -> None:
    """M7."""
    script = _js()

    assert '"use strict"' in script
    guard = script.index("showModal")
    assert "dialog.viewer" in script[:guard]
    assert "typeof" in script[:guard]
    assert "return" in script[:guard]
    assert guard < script.index("photo-open")


# M8: closing


def test_script_closes_on_every_route_and_returns_focus() -> None:
    """M8."""
    script = _js()

    for word in (
        "popstate",
        "history.back()",
        ".focus(",
        "viewer__close",
        "cancel",
        '"close"',
        "viewer__track",
        "viewer__slide",
    ):
        assert word in script, word


# M9: size, forbidden words, texts


def test_script_is_small_and_uses_no_forbidden_word() -> None:
    """M9."""
    script = _js()

    assert len(script.encode("utf-8")) < 6000
    for word in (
        "import",
        "require(",
        "http",
        "eval(",
        "localStorage",
        "sessionStorage",
        "fetch(",
        "sendBeacon",
    ):
        assert word not in script, word


def test_the_five_viewer_texts_exist_in_both_languages() -> None:
    """M9."""
    english = {
        "viewer_label": "Photo viewer",
        "viewer_open": "Open photo full screen: ",
        "viewer_close": "Close",
        "viewer_previous": "Previous photo",
        "viewer_next": "Next photo",
    }
    vietnamese = {
        "viewer_label": "Xem ảnh",
        "viewer_open": "Mở ảnh toàn màn hình: ",
        "viewer_close": "Đóng",
        "viewer_previous": "Ảnh trước",
        "viewer_next": "Ảnh sau",
    }
    for key, value in english.items():
        assert shell.EN.get(key) == value, key
    for key, value in vietnamese.items():
        assert shell.VI.get(key) == value, key
