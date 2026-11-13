"""The page reports views and button presses to the counter (contact-counter spec AC9 to AC12).

What the script does in a browser is shown by the browser check of the issue (AC5). These tests
pin where the script is linked, and what the file holds and must not hold.
"""

import re

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import Client
from pytest_django import DjangoAssertNumQueries, Settings

from counter.models import DailyCount
from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

SCRIPT = settings.SRC_DIR / "static" / "js" / "count.js"
TAG = '<script src="/static/js/count.js" defer></script>'


def _home(client: Client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.content.decode()


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _code() -> str:
    """The script without its comments, so a word in a comment does not count as code."""
    without_blocks = re.sub(r"/\*.*?\*/", "", _script(), flags=re.DOTALL)
    return re.sub(r"(?m)^\s*//.*$", "", without_blocks)


# AC1


def test_home_links_the_script_once_as_the_last_script(client: Client) -> None:
    html = _home(client)

    assert html.count(TAG) == 1
    scripts = re.findall(r"<script[^>]*>", html)
    assert scripts[-1] == '<script src="/static/js/count.js" defer>'


def test_script_is_linked_also_when_the_owner_has_no_channel(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")

    html = _home(client)

    assert "data-channel" not in html
    assert html.count(TAG) == 1
    assert re.findall(r"<script[^>]*>", html)[-1] == '<script src="/static/js/count.js" defer>'


def test_script_file_is_a_static_file() -> None:
    assert finders.find("js/count.js")


def test_base_template_does_not_link_the_script() -> None:
    base = (settings.SRC_DIR / "templates" / "base.html").read_text(encoding="utf-8")

    assert "count.js" not in base


def test_not_found_page_does_not_load_the_script(client: Client, settings: Settings) -> None:
    settings.DEBUG = False

    response = client.get("/no-such-page/")

    assert response.status_code == 404
    assert "count.js" not in response.content.decode()


def test_admin_does_not_load_the_script(client: Client) -> None:
    login = client.get("/owner/login/")
    assert login.status_code == 200
    assert "count.js" not in login.content.decode()

    owner = get_user_model().objects.create_superuser("owner-test", password="pass-for-test")
    client.force_login(owner)
    index = client.get("/owner/")
    assert index.status_code == 200
    assert "count.js" not in index.content.decode()


# AC2


def test_script_sends_one_view_with_a_beacon_or_a_keepalive_fetch() -> None:
    code = _code()

    assert 'kind: "view"' in code
    assert "navigator.sendBeacon" in code
    assert "URLSearchParams" in code
    assert re.search(r'fetch\(\s*ADDRESS\s*,\s*\{\s*method:\s*"POST",\s*keepalive:\s*true', code)
    assert 'var ADDRESS = "/count/";' in code
    # A beacon the browser refuses (sendBeacon returns false) falls back to the keepalive fetch.
    assert "!beacon(body)" in code
    # A beacon that throws also falls back to the fetch.
    assert re.search(r"function beacon\(body\) \{\s*var taken = false;\s*try \{", code)


def test_a_prerendered_page_counts_its_view_only_once_shown() -> None:
    code = _code()

    # Chrome may prerender / before the visitor goes there; the view waits until it is shown.
    assert "document.prerendering" in code
    assert 'document.addEventListener("prerenderingchange", view, { once: true })' in code


def test_script_keeps_nothing_in_the_browser() -> None:
    code = _code()

    for sign in ("document.cookie", "localStorage", "sessionStorage", "indexedDB"):
        assert sign not in code, sign


# AC3


def test_one_listener_on_the_document_handles_every_button() -> None:
    code = _code()

    assert code.count('document.addEventListener("click", press)') == 1
    assert code.count('document.addEventListener("auxclick", press)') == 1
    # The third listener is the one-time prerendering change of the view, not a button.
    assert code.count("addEventListener") == 3
    assert 'closest("a[data-channel]")' in code
    assert "event.button !== 1" in code
    # A click with another button than the main one is left to auxclick, so it counts once.
    assert 'event.type === "click" && event.button !== 0' in code
    assert 'kind: "click"' in code
    assert 'getAttribute("data-channel")' in code
    assert 'getAttribute("data-place")' in code


def test_script_never_stops_or_delays_the_link() -> None:
    code = _code()

    for sign in (
        "preventDefault",
        "stopPropagation",
        "returnValue",
        "location",
        "setTimeout",
        "window.open",
        "return false",
    ):
        assert sign not in code, sign


def test_buttons_are_links_with_no_script_of_their_own(client: Client) -> None:
    html = _home(client)

    buttons = re.findall(r"<a [^>]*data-channel=[^>]*>", html)
    assert buttons
    for button in buttons:
        assert "onclick" not in button
        assert 'href="' in button
        if 'data-channel="call"' in button:
            assert 'href="tel:' in button
            assert "target=" not in button
        else:
            assert 'target="_blank" rel="noopener"' in button


# AC5 (the server half: what the script sends for a press on WhatsApp in #contact)


def test_the_body_the_script_sends_for_a_press_is_answered_204(client: Client) -> None:
    html = _home(client)
    button = re.search(r'<a [^>]*data-channel="whatsapp" data-place="contact"[^>]*>', html)
    assert button, "no WhatsApp button in #contact"

    # URLSearchParams({kind, channel, place}) as sendBeacon and fetch send it, from the page itself.
    response = client.post(
        "/count/",
        "kind=click&channel=whatsapp&place=contact",
        content_type="application/x-www-form-urlencoded;charset=UTF-8",
        headers={"Origin": "http://testserver"},
    )

    assert response.status_code == 204
    stored = DailyCount.objects.get(kind="click", channel="whatsapp", place="contact")
    assert stored.count == 1


def test_the_body_the_script_sends_on_load_is_answered_204(client: Client) -> None:
    response = client.post(
        "/count/",
        "kind=view",
        content_type="application/x-www-form-urlencoded;charset=UTF-8",
        headers={"Origin": "http://testserver"},
    )

    assert response.status_code == 204
    assert DailyCount.objects.get(kind="view", channel="", place="").count == 1


# AC6 (the script adds no query and no cookie to the page)


def test_home_with_the_script_still_makes_one_query_and_sets_no_cookie(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(1):
        response = client.get("/")

    assert TAG in response.content.decode()
    assert not response.cookies


# AC4


def test_errors_are_swallowed() -> None:
    code = _code()

    assert code.count("try {") >= 2
    assert ".catch(function () {})" in code
    assert "console." not in code
    assert "throw " not in code


def test_script_is_small_and_talks_only_to_the_counter() -> None:
    script = _script()
    code = _code()

    assert len(script.encode()) < 3_000
    for sign in (
        "import ",
        "require(",
        "http://",
        "https://",
        "eval(",
        "Function(",
        "jQuery",
    ):
        assert sign not in code, sign
    # The only address in the file is the counter's.
    assert re.findall(r'"(/[^"]*)"', code) == ["/count/"]
