"""The contact buttons live in one place (issue #170, contact-one-place spec)."""

import html as html_lib
import re

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from counter.models import DailyCount
from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

CONTACT_CSS = settings.SRC_DIR / "static" / "css" / "chapters" / "contact.css"
SCRIPT = settings.SRC_DIR / "static" / "js" / "contact-bar.js"
NOSCRIPT = "<noscript><style>.contact-bar { transform: none !important; }</style></noscript>"
PHONE_RULE = "html.contact-bar-ready .chapter--contact .contact__row .contact-buttons"

PATHS = ["/", "/vi/"]


@pytest.fixture(autouse=True)
def owner_values() -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        price_from_million=13,
        price_to_million=14,
        phone="0945 384 500",
        whatsapp="0945 384 500",
        zalo="0945 384 500",
        owner_first_name="Bún",
        reply_time="within an hour",
    )


def _page(client: Client, path: str = "/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _section(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.DOTALL)
    assert match, pattern
    return match.group(0)


def _chapter(html: str, name: str) -> str:
    return _section(html, rf'<section id="{name}".*?</section>')


def _without_bar(html: str) -> str:
    return re.sub(r'<nav class="contact-bar".*?</nav>', "", html, flags=re.DOTALL)


def _phone_part(css: str) -> str:
    parts = css.split("@media (max-width: 760px)", 1)
    assert len(parts) == 2, "no phone rules"
    return parts[1].split("@media (prefers-reduced-motion", 1)[0]


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _links(fragment: str) -> list[str]:
    return re.findall(r"<a [^>]*data-channel=[^>]*>", fragment)


# M1, M2: one set of buttons outside the bar, in chapter 05


@pytest.mark.parametrize("path", PATHS)
def test_one_set_of_buttons_outside_the_bar_in_the_contact_chapter(
    client: Client, path: str
) -> None:
    outside = _without_bar(_page(client, path))

    assert outside.count('<div class="contact-buttons"') == 1
    contact = _chapter(outside, "contact")
    assert contact.count('<div class="contact-buttons"') == 1
    links = _links(outside)
    assert len(links) == 3
    assert all('data-place="contact"' in link for link in links)
    assert 'data-place="rent"' not in outside
    assert 'data-place="faq"' not in outside


# M3: the rent chapter and the FAQ lose their buttons


@pytest.mark.parametrize(
    ("path", "line"),
    [("/", "Hi, I'm Bún."), ("/vi/", "Chào bạn, mình là Bún.")],
)
def test_faq_invite_keeps_the_line_and_no_buttons_and_rent_has_none(
    client: Client, path: str, line: str
) -> None:
    html = _page(client, path)

    faq = _chapter(html, "faq")
    invite = _section(faq, r'<div class="faq-side__invite".*?<div class="faq-list')
    assert "faq-side__line" in invite
    assert "contact-buttons" not in invite
    assert line in html_lib.unescape(invite)
    rent = _chapter(html, "rent")
    assert "rent__buttons" not in rent
    assert "data-channel" not in rent


# M4: the script


def test_script_watches_chapter_02_with_one_observer_and_is_small() -> None:
    script = _script()

    assert 'getElementById("hoa-xuan")' in script
    assert script.count("new IntersectionObserver") == 1
    assert 'rootMargin: "100000px 0px 0px 0px"' in script
    assert "contact-bar--away" in script
    assert 'getElementById("hero")' not in script
    assert 'getElementById("contact")' not in script
    assert 'querySelectorAll(".contact-buttons")' not in script
    assert len(script.encode("utf-8")) < 4000


# M6: phone CSS hides chapter 05's buttons only once the script has run


def test_phone_css_hides_chapter_05_buttons_only_when_the_bar_script_is_ready() -> None:
    css = CONTACT_CSS.read_text(encoding="utf-8")
    phone = _phone_part(css)

    match = re.search(re.escape(PHONE_RULE) + r"\s*\{([^}]*)\}", phone)
    assert match, "no hiding rule in the phone block"
    assert "display: none" in match.group(1)
    bare = [
        rule
        for rule in re.findall(r"([^{}]+)\{([^}]*)\}", css)
        if ".chapter--contact .contact__row .contact-buttons" in rule[0]
        and "html.contact-bar-ready" not in rule[0]
        and "display: none" in rule[1]
    ]
    assert bare == []


@pytest.mark.parametrize("path", PATHS)
def test_contact_chapter_still_holds_the_three_buttons_in_the_html(
    client: Client, path: str
) -> None:
    contact = _chapter(_page(client, path), "contact")

    assert len(_links(contact)) == 3


# M7: the form focus


def test_script_steps_the_bar_away_while_a_form_field_has_focus() -> None:
    script = _script()

    assert 'querySelector("form.enquiry-form")' in script
    assert '"focusin"' in script
    assert '"focusout"' in script
    assert "document.activeElement" in script


# M9: no JavaScript, no observer, no chapter 02


def test_noscript_style_stays_before_the_end_of_the_head(client: Client) -> None:
    html = _page(client)

    assert NOSCRIPT in html
    assert html.index(NOSCRIPT) < html.index("</head>")


def test_missing_observer_and_missing_chapter_02_mark_the_page_ready_and_stop() -> None:
    script = _script()

    observer_branch = _section(script, r"if \(!window\.IntersectionObserver\) \{.*?return;\s*\}")
    assert 'document.documentElement.classList.add("contact-bar-ready")' in observer_branch
    created = script.index("new IntersectionObserver")
    after_branch = script[script.index(observer_branch) + len(observer_branch) : created]
    chapter_branch = _section(after_branch, r"if \(![A-Za-z_]+\) \{.*?return;\s*\}")
    assert 'document.documentElement.classList.add("contact-bar-ready")' in chapter_branch


# M10: what stays


def test_css_keeps_the_rule_for_a_page_where_the_script_has_not_run() -> None:
    css = CONTACT_CSS.read_text(encoding="utf-8")

    assert "html:not(.contact-bar-ready) .contact-bar" in css


@pytest.mark.parametrize(("path", "label"), [("/", "Contact"), ("/vi/", "Liên hệ")])
def test_bar_markup_is_unchanged(client: Client, path: str, label: str) -> None:
    assert f'<nav class="contact-bar" aria-label="{label}">' in _page(client, path)


# M11: no channel


def test_no_channel_means_no_bar_no_script_no_buttons_no_noscript(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")

    html = _page(client)

    assert "contact-bar" not in html
    assert "contact-bar.js" not in html
    assert "contact-buttons" not in html
    assert "<noscript>" not in html
    assert 'class="contact__empty"' in _chapter(html, "contact")


# M12: the counter keeps its places, no migration


def test_counter_places_are_unchanged_and_no_migration_is_needed() -> None:
    assert sorted(DailyCount.Place.values) == sorted(["bar", "rent", "contact", "faq", "journal"])

    call_command("makemigrations", "--check", "--dry-run")


# M21: one query


@pytest.mark.parametrize("path", PATHS)
def test_page_makes_one_query(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        _page(client, path)
