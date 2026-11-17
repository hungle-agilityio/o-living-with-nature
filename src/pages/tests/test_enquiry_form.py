"""The enquiry form in chapter 05 of `/` and `/vi/` (issue #117, rows M15 to M25).

M16 is checked by a CSS test only (the phone screenshot is the evidence); M26 is the pull
request's check output.
"""

import html as html_lib
import re
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from enquiries.models import Enquiry
from owner_content.models import SiteSettings

pytestmark = pytest.mark.django_db

NUMBER = "0945 384 500"
# 12:00 on 16 Nov 2026 in Đà Nẵng (UTC+7).
NOON = datetime(2026, 11, 16, 5, 0, tzinfo=UTC)
CSS = Path(__file__).resolve().parents[2] / "static" / "css" / "chapters" / "contact.css"

EN_MONTHS = [
    "November 2026",
    "December 2026",
    "January 2027",
    "February 2027",
    "March 2027",
    "April 2027",
    "May 2027",
    "June 2027",
    "July 2027",
    "August 2027",
    "September 2027",
    "October 2027",
]
VI_MONTHS = [f"Tháng {m}/2026" for m in (11, 12)] + [f"Tháng {m}/2027" for m in range(1, 11)]
EN_STAYS = ["1–3 months", "3–6 months", "6–12 months", "A year or more"]
VI_STAYS = ["1–3 tháng", "3–6 tháng", "6–12 tháng", "Từ một năm trở lên"]
EN_PRIVACY = "I keep your message only to reply to you, and delete it after 12 months. No cookies."
VI_PRIVACY = "Mình chỉ giữ lời nhắn để trả lời bạn, và xóa sau 12 tháng. Không dùng cookie."
EN_PAUSED = (
    "Many messages came in today, so the form rests until tomorrow. "
    "Please use Call, WhatsApp or Zalo above, or try again tomorrow."
)
EN_PAUSED_NO_CHANNEL = (
    "Many messages came in today, so the form rests until tomorrow. Please try again tomorrow."
)
VI_PAUSED = (
    "Hôm nay có nhiều lời nhắn nên form nghỉ đến mai. "
    "Bạn gọi hoặc nhắn WhatsApp, Zalo ở trên, hoặc thử lại ngày mai nhé."
)
VALID = {
    "name": "Anna K.",
    "reply_to": "anna.k@example.com",
    "move_in": "2027-01",
    "stay": "6-12",
    "message": "Hello Bún, we work remotely.",
}


@pytest.fixture(autouse=True)
def clock(mocker: MockerFixture) -> MagicMock:
    """Freeze "now" at noon on 16 Nov 2026 in Đà Nẵng."""
    mock: MagicMock = mocker.patch("django.utils.timezone.now")
    mock.return_value = NOON
    return mock


@pytest.fixture(autouse=True)
def owner_values() -> None:
    SiteSettings.objects.all().delete()
    SiteSettings.objects.create(
        price_from_million=13,
        price_to_million=14,
        phone=NUMBER,
        whatsapp=NUMBER,
        zalo=NUMBER,
        owner_first_name="Bún",
        reply_time="within an hour",
    )


def _plain(fragment: str) -> str:
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def _contact(html: str) -> str:
    match = re.search(r'<section id="contact".*?</section>', html, re.DOTALL)
    assert match
    return match.group(0)


def _enquiry(html: str) -> str:
    """The part of chapter 05 from the enquiry block to the end of the section."""
    contact = _contact(html)
    start = contact.find('id="enquiry"')
    assert start != -1, "no #enquiry block in the contact chapter"
    return contact[contact.rfind("<div", 0, start) :]


def _get(client: Client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return response.content.decode()


def _post(client: Client, path: str, data: dict[str, str], status: int) -> str:
    response = client.post(path, data)
    assert response.status_code == status
    return response.content.decode()


def _tag(html: str, pattern: str) -> str:
    match = re.search(pattern, html, re.DOTALL)
    assert match, pattern
    return match.group(0)


def _field_html(block: str, control_id: str) -> str:
    """The `div.field` that holds the control with this id."""
    for field in re.findall(
        r'<div class="field[^"]*".*?(?=<div class="field|<div class="enquiry__trap)',
        block,
        re.DOTALL,
    ):
        if f'id="{control_id}"' in field:
            return str(field)
    raise AssertionError(f"no field for {control_id}")


def _options(block: str, select_id: str) -> list[str]:
    select = _tag(block, rf'<select[^>]*id="{select_id}".*?</select>')
    return [_plain(o) for o in re.findall(r"<option[^>]*>(.*?)</option>", select, re.DOTALL)]


# M15 (AC1)


def test_m15_english_form_sits_after_the_contact_row_with_every_text(client: Client) -> None:
    html = _get(client, "/")

    contact = _contact(html)
    assert contact.index('class="contact__row') < contact.index('id="enquiry"')
    block = _enquiry(html)
    assert 'class="enquiry reveal"' in block
    text = _plain(block)
    for expected in [
        "Or leave me a message",
        "Your name",
        "How can I reply?",
        "When would you move in? (optional)",
        "For how long? (optional)",
        "Your message",
        EN_PRIVACY,
        "Send message",
    ]:
        assert expected in text
    assert 'placeholder="Email, or a WhatsApp / Zalo number"' in block
    assert 'placeholder="Who will live here, what matters to you…"' in block
    assert _options(block, "enq-month") == ["Not sure yet", *EN_MONTHS]
    assert _options(block, "enq-stay") == ["Not sure yet", *EN_STAYS]
    form = _tag(block, r"<form[^>]*>")
    assert 'method="post"' in form
    assert 'action="/enquiry/#enquiry"' in form
    assert 'class="enquiry-form"' in form
    assert "novalidate" in form
    assert "csrfmiddlewaretoken" not in block


# M16 (AC9): CSS check only


def test_m16_narrow_screen_block_sets_one_column_and_a_full_width_button() -> None:
    css = CSS.read_text()
    starts = [m.start() for m in re.finditer(r"@media \(max-width: 760px\) \{", css)]
    assert len(starts) >= 2, "no second 760px block in contact.css"
    block = css[starts[1] :]
    # The second block ends at the next @media or the end of the file.
    nxt = block.find("@media", 1)
    block = block if nxt == -1 else block[:nxt]
    grid = _tag(block, r"\.enquiry__grid\s*\{[^}]*\}")
    assert re.search(r"grid-template-columns:\s*1fr\s*;", grid)
    button = _tag(block, r"\.enquiry[^{]*\.button[^{]*\{[^}]*\}")
    assert "width: 100%" in button


# M17 (AC2)


def test_m17_vietnamese_form_texts_months_and_action(client: Client) -> None:
    html = _get(client, "/vi/")

    block = _enquiry(html)
    text = _plain(block)
    for expected in [
        "Hoặc để lại lời nhắn cho mình",
        "Tên của bạn",
        "Mình liên lạc lại bằng cách nào?",
        "Bạn định vào ở tháng nào? (không bắt buộc)",
        "Ở trong bao lâu? (không bắt buộc)",
        "Lời nhắn",
        VI_PRIVACY,
        "Gửi lời nhắn",
    ]:
        assert expected in text
    assert 'placeholder="Email, hoặc số WhatsApp / Zalo"' in block
    assert 'placeholder="Ai sẽ ở, điều gì quan trọng với bạn…"' in block
    assert _options(block, "enq-month") == ["Chưa chắc", *VI_MONTHS]
    assert _options(block, "enq-stay") == ["Chưa chắc", *VI_STAYS]
    assert 'action="/vi/enquiry/#enquiry"' in _tag(block, r"<form[^>]*>")


# M18 (AC3)


def test_m18_three_errors_summary_aria_and_value_written_back(client: Client) -> None:
    data = {**VALID, "name": "", "reply_to": "0905 12", "message": ""}

    html = _post(client, "/enquiry/", data, 400)

    block = _enquiry(html)
    text = _plain(block)
    assert 'role="alert"' in block
    assert "3 things need a look before I can read your message." in text
    assert "Please tell me your name." in text
    assert "That doesn’t look like an email or a phone number." in text
    assert "Please write a few words." in text
    for control, error_id in [
        ("enq-name", "enq-name-error"),
        ("enq-reply", "enq-reply-error"),
        ("enq-message", "enq-message-error"),
    ]:
        field = _field_html(block, control)
        assert "field--error" in field
        assert 'aria-invalid="true"' in field
        assert f'aria-describedby="{error_id}"' in field
        assert f'id="{error_id}"' in field
    assert 'value="0905 12"' in _field_html(block, "enq-reply")


def test_m18_one_error_uses_the_singular_summary(client: Client) -> None:
    html = _post(client, "/enquiry/", {**VALID, "name": ""}, 400)

    assert "1 thing needs a look before I can read your message." in _plain(_enquiry(html))


def test_m18_vietnamese_errors(client: Client) -> None:
    data = {**VALID, "name": "", "reply_to": "0905 12", "message": ""}

    html = _post(client, "/vi/enquiry/", data, 400)

    text = _plain(_enquiry(html))
    assert "Còn 3 chỗ cần xem lại trước khi gửi." in text
    assert "Bạn cho mình biết tên nhé." in text
    assert "Email hoặc số điện thoại này có vẻ chưa đúng." in text
    assert "Bạn viết vài dòng nhé." in text


def test_m18_fields_without_error_keep_their_values_and_selection(client: Client) -> None:
    html = _post(client, "/enquiry/", {**VALID, "name": ""}, 400)

    block = _enquiry(html)
    assert "field--error" not in _field_html(block, "enq-reply")
    assert 'value="anna.k@example.com"' in _field_html(block, "enq-reply")
    assert re.search(r'<option[^>]*value="2027-01"[^>]*selected', block) or re.search(
        r'<option[^>]*selected[^>]*value="2027-01"', block
    )
    assert "Hello Bún, we work remotely." in _field_html(block, "enq-message")


# M19 (AC4)


def test_m19_empty_reply_to_line(client: Client) -> None:
    html = _post(client, "/enquiry/", {**VALID, "reply_to": ""}, 400)

    assert "Please leave an email or a phone number so I can reply." in _plain(_enquiry(html))


def test_m19_message_over_1000_characters_line(client: Client) -> None:
    html = _post(client, "/enquiry/", {**VALID, "message": "x" * 1001}, 400)

    assert "Please keep this under 1000 characters." in _plain(_enquiry(html))


def test_m19_invalid_choice_line(client: Client) -> None:
    html = _post(client, "/enquiry/", {**VALID, "stay": "2-4"}, 400)

    assert "Please pick from the list." in _plain(_enquiry(html))


def test_m19_other_error_code_uses_the_wrong_value_text(client: Client) -> None:
    html = _post(client, "/enquiry/", {**VALID, "name": "Anna\x00"}, 400)

    assert "Please tell me your name." in _plain(_enquiry(html))


# M20 (AC5)


def test_m20_sent_state_in_english(client: Client) -> None:
    html = _get(client, "/?enquiry=sent")

    block = _enquiry(html)
    assert 'role="status"' in _tag(block, r"<div[^>]*>")
    assert "enquiry--sent" in _tag(block, r"<div[^>]*>")
    text = _plain(block)
    assert "Message sent" in text
    assert "Thank you, your message is with me. I usually reply within an hour." in text
    assert '<span class="accent">I usually reply within an hour.</span>' in block
    assert '<form class="enquiry-form"' not in html


def test_m20_sent_state_in_vietnamese(client: Client) -> None:
    html = _get(client, "/vi/?enquiry=sent")

    block = _enquiry(html)
    assert 'role="status"' in _tag(block, r"<div[^>]*>")
    text = _plain(block)
    assert "Đã gửi" in text
    assert "Cảm ơn bạn, mình đã nhận được lời nhắn. Mình thường trả lời trong vòng một giờ." in text
    assert '<form class="enquiry-form"' not in html


# M21 (AC5)


def test_m21_accent_follows_the_owners_reply_time(client: Client) -> None:
    SiteSettings.objects.update(reply_time="within a day")

    html = _get(client, "/?enquiry=sent")

    assert '<span class="accent">I usually reply within a day.</span>' in _enquiry(html)


# M22 (AC6)


def _fill_today() -> None:
    Enquiry.objects.bulk_create(
        [
            Enquiry(name=f"N{i}", reply_to="old@example.com", message="Hi", language="en")
            for i in range(20)
        ]
    )


def test_m22_paused_in_english_with_channels(client: Client) -> None:
    _fill_today()

    html = _post(client, "/enquiry/", VALID, 429)

    block = _enquiry(html)
    assert 'role="status"' in _tag(block, r"<div[^>]*>")
    assert "enquiry--paused" in _tag(block, r"<div[^>]*>")
    text = _plain(block)
    assert "Messages paused for today" in text
    assert EN_PAUSED in text
    assert "<form" not in block


def test_m22_paused_in_english_without_channels(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")
    _fill_today()

    html = _post(client, "/enquiry/", VALID, 429)

    block = _enquiry(html)
    assert EN_PAUSED_NO_CHANNEL in _plain(block)
    assert "Call, WhatsApp or Zalo above" not in block
    assert "<form" not in block


def test_m22_paused_in_vietnamese(client: Client) -> None:
    _fill_today()

    html = _post(client, "/vi/enquiry/", VALID, 429)

    block = _enquiry(html)
    text = _plain(block)
    assert "Hôm nay tạm dừng nhận lời nhắn" in text
    assert VI_PAUSED in text
    assert "<form" not in block


# M23 (AC7)


def test_m23_no_channel_shows_the_empty_line_and_the_form(client: Client) -> None:
    SiteSettings.objects.update(phone="", whatsapp="", zalo="")

    html = _get(client, "/")

    contact = _contact(html)
    assert "Contact details are on their way." in contact
    assert contact.index("Contact details are on their way.") < contact.index('id="enquiry"')
    assert '<form class="enquiry-form"' in contact
    assert "Send message" in _plain(_enquiry(html))


# M24 (AC8)


def test_m24_sensitive_values_trap_and_no_link_after_a_refused_post(client: Client) -> None:
    data = {**VALID, "message": ""}

    html = _post(client, "/enquiry/", data, 400)

    block = _enquiry(html)
    name = _tag(_field_html(block, "enq-name"), r"<input[^>]*>")
    reply = _tag(_field_html(block, "enq-reply"), r"<input[^>]*>")
    assert "data-sensitive" in name and 'value="Anna K."' in name
    assert "data-sensitive" in reply
    assert "data-sensitive" in _tag(block, r"<textarea[^>]*>")
    trap_block = _tag(block, r'<div class="enquiry__trap"[^>]*>.*?</div>')
    assert 'aria-hidden="true"' in trap_block
    trap = _tag(trap_block, r"<input[^>]*>")
    assert 'tabindex="-1"' in trap and 'autocomplete="off"' in trap
    assert 'name="website"' in trap
    assert "value=" not in trap
    assert "<a " not in block
    assert "<script" not in block


def test_m24_the_home_page_links_the_same_scripts_in_the_same_order(client: Client) -> None:
    html = _get(client, "/")

    assert re.findall(r'<script[^>]*src="([^"]+)"', html) == [
        "/static/js/reveal.js",
        "/static/js/daypart.js",
        *re.findall(r'<script[^>]*src="([^"]+)"', html)[2:],
    ]
    assert "enquiry" not in " ".join(re.findall(r'<script[^>]*src="([^"]+)"', html))
    assert '<div class="enquiry reveal" id="enquiry">' in html


# M25 (AC10)


@pytest.mark.parametrize("path", ["/", "/vi/", "/?enquiry=sent"])
def test_m25_one_query_each(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, path: str
) -> None:
    with django_assert_num_queries(1):
        response = client.get(path)

    assert response.status_code == 200
    assert 'id="enquiry"' in response.content.decode()
