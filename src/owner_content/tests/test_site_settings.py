"""The site settings the owner edits (owner-content AC7 to AC12; issue #28 AC1 to AC6)."""

import importlib
from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from django.apps import apps as django_apps
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db.models import Field
from django.test import Client
from pytest_django import DjangoAssertNumQueries

from owner_content.models import SiteSettings
from owner_content.services import Channel, site_settings

PHONE_ERROR = "Enter a Vietnamese number like 0945 384 500 or +84 945 384 500."
PRICE_ERROR = "Price to cannot be lower than Price from."
PHONE_HELP = "A Vietnamese number like 0945 384 500 or +84 945 384 500. Empty hides the button."
OWNER_CHANNELS = (
    Channel(key="call", label="Call", link="tel:+84945384500"),
    Channel(key="whatsapp", label="WhatsApp", link="https://wa.me/84945384500"),
    Channel(key="zalo", label="Zalo", link="https://zalo.me/0945384500"),
)
PUBLIC_ADDRESSES = ["/", "/house/", "/hoa-xuan/", "/faq/", "/contact/"]
CHANGELIST = "/owner/owner_content/sitesettings/"


def the_record() -> SiteSettings:
    return SiteSettings.objects.get()


@pytest.fixture
def owner_client(client: Client) -> Client:
    owner = User.objects.create_superuser("owner", password="a-long-enough-pass")
    client.force_login(owner)
    return client


def form_data(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "price_from_million": "13",
        "price_to_million": "14",
        "phone": "0945 384 500",
        "whatsapp": "0945 384 500",
        "zalo": "0945 384 500",
        "owner_first_name": "Bún",
        "reply_time": "within an hour",
    }
    data.update(changes)
    return data


# AC1: the fields, their labels, rules and help texts


@pytest.mark.parametrize(
    ("name", "label", "help_text"),
    [
        (
            "price_from_million",
            "Price from (million VND a month)",
            "The lower end of the monthly rent, in million VND.",
        ),
        (
            "price_to_million",
            "Price to (million VND a month)",
            "The upper end. Leave empty for one price.",
        ),
        ("phone", "Phone (Call button)", PHONE_HELP),
        ("whatsapp", "WhatsApp", PHONE_HELP),
        ("zalo", "Zalo", PHONE_HELP),
        ("owner_first_name", "Your first name", 'Shown as "Hi, I\'m …".'),
        (
            "reply_time",
            "Usual reply time",
            'Shown as "I usually reply …", for example "within an hour".',
        ),
    ],
)
def test_field_has_its_admin_label_and_help_text(name: str, label: str, help_text: str) -> None:
    field = SiteSettings._meta.get_field(name)

    assert isinstance(field, Field)
    assert field.verbose_name == label
    assert field.help_text == help_text


def test_a_new_record_has_the_default_name_and_reply_time_and_nothing_else() -> None:
    record = SiteSettings()

    assert record.owner_first_name == "Bún"
    assert record.reply_time == "within an hour"
    assert record.price_from_million is None
    assert record.price_to_million is None
    assert (record.phone, record.whatsapp, record.zalo) == ("", "", "")
    record.full_clean()  # every optional field may stay empty


@pytest.mark.parametrize("field", ["price_from_million", "price_to_million"])
@pytest.mark.parametrize("value", [0, 1000, -3])
def test_price_outside_1_to_999_is_refused(field: str, value: int) -> None:
    record = SiteSettings(**{field: value})

    with pytest.raises(ValidationError) as error:
        record.full_clean()

    assert field in error.value.message_dict


@pytest.mark.parametrize(("price_from", "price_to"), [(1, 999), (13, 13), (13, None), (None, None)])
def test_price_inside_the_rules_is_accepted(price_from: int | None, price_to: int | None) -> None:
    SiteSettings(price_from_million=price_from, price_to_million=price_to).full_clean()


def test_price_to_below_price_from_is_refused_with_the_message() -> None:
    record = SiteSettings(price_from_million=14, price_to_million=13)

    with pytest.raises(ValidationError) as error:
        record.full_clean()

    assert error.value.message_dict == {"price_to_million": [PRICE_ERROR]}


@pytest.mark.parametrize("field", ["phone", "whatsapp", "zalo"])
@pytest.mark.parametrize(
    "number",
    [
        "0945 384 500",
        "+84 945 384 500",
        "0945384500",
        "+84945384500",
        "0945.384.500",
        "0945-384-500",
        "945384500",  # 9 digits, no prefix
        "0 123 456 789 01",  # 11 digits after the 0
    ],
)
def test_vietnamese_number_is_accepted(field: str, number: str) -> None:
    SiteSettings(**{field: number}).full_clean()


@pytest.mark.parametrize("field", ["phone", "whatsapp", "zalo"])
@pytest.mark.parametrize(
    "number",
    [
        "12345678",  # 8 digits
        "+84 123 456 789 012",  # 12 digits after +84
        "0945 384 50a",
        "0945/384/500",
        "(0945) 384 500",
        "+1 945 384 500",
        "0945 384 500 ext 2",
        "call me",
        "０９４５ ３８４ ５００",  # full-width digits
        "٠٩٤٥٣٨٤٥٠٠",  # Arabic-Indic digits
    ],
)
def test_other_number_is_refused_with_the_message(field: str, number: str) -> None:
    record = SiteSettings(**{field: number})

    with pytest.raises(ValidationError) as error:
        record.full_clean()

    assert error.value.message_dict == {field: [PHONE_ERROR]}


@pytest.mark.parametrize(("field", "limit"), [("owner_first_name", 40), ("reply_time", 60)])
def test_name_and_reply_time_are_required_and_limited(field: str, limit: int) -> None:
    SiteSettings(**{field: "x" * limit}).full_clean()

    for value in ("", "x" * (limit + 1)):
        with pytest.raises(ValidationError) as error:
            SiteSettings(**{field: value}).full_clean()
        assert field in error.value.message_dict


@pytest.mark.django_db
def test_admin_refuses_a_wrong_number_and_keeps_the_record(owner_client: Client) -> None:
    record = the_record()

    response = owner_client.post(f"{CHANGELIST}{record.pk}/change/", form_data(zalo="12345"))

    assert response.status_code == 200
    assert PHONE_ERROR in response.content.decode()
    assert the_record().zalo == "0945 384 500"


@pytest.mark.django_db
def test_admin_refuses_a_price_to_below_price_from(owner_client: Client) -> None:
    record = the_record()

    response = owner_client.post(
        f"{CHANGELIST}{record.pk}/change/",
        form_data(price_from_million="14", price_to_million="13"),
    )

    assert response.status_code == 200
    assert PRICE_ERROR in response.content.decode()
    assert the_record().price_from_million == 13


@pytest.mark.django_db
def test_admin_saves_the_owners_changes(owner_client: Client) -> None:
    record = the_record()

    response = owner_client.post(
        f"{CHANGELIST}{record.pk}/change/",
        form_data(
            price_from_million="15", price_to_million="", phone="+84 945 384 500", whatsapp=""
        ),
    )

    assert response.status_code == 302
    saved = the_record()
    assert (saved.price_from_million, saved.price_to_million) == (15, None)
    assert (saved.phone, saved.whatsapp, saved.zalo) == ("+84 945 384 500", "", "0945 384 500")


# AC2: the admin shows one record, with no Add and no delete


@pytest.mark.django_db
def test_admin_index_lists_site_settings_under_owner_content(owner_client: Client) -> None:
    html = owner_client.get("/owner/").content.decode()

    assert "Owner content" in html
    assert "Site settings" in html
    assert CHANGELIST in html


@pytest.mark.django_db
def test_with_a_record_there_is_no_add_and_no_delete(owner_client: Client) -> None:
    record = the_record()

    index = owner_client.get("/owner/").content.decode()
    changelist = owner_client.get(CHANGELIST)
    change = owner_client.get(f"{CHANGELIST}{record.pk}/change/")

    assert f"{CHANGELIST}add/" not in index
    assert changelist.status_code == 200
    assert f"{CHANGELIST}add/" not in changelist.content.decode()
    assert "delete_selected" not in changelist.content.decode()
    assert change.status_code == 200
    assert "/delete/" not in change.content.decode()
    assert owner_client.get(f"{CHANGELIST}add/").status_code == 403
    assert owner_client.post(f"{CHANGELIST}add/", form_data()).status_code == 403
    assert owner_client.post(f"{CHANGELIST}{record.pk}/delete/", {"post": "yes"}).status_code == 403
    assert SiteSettings.objects.count() == 1


@pytest.mark.django_db
def test_without_a_record_the_owner_can_add_the_one_record(owner_client: Client) -> None:
    SiteSettings.objects.all().delete()

    assert f"{CHANGELIST}add/" in owner_client.get(CHANGELIST).content.decode()
    assert owner_client.post(f"{CHANGELIST}add/", form_data()).status_code == 302
    assert SiteSettings.objects.count() == 1
    assert owner_client.get(f"{CHANGELIST}add/").status_code == 403


@pytest.mark.django_db
def test_signed_out_visitor_cannot_reach_the_settings(client: Client) -> None:
    response = client.get(CHANGELIST)

    assert response.status_code == 302
    assert response["Location"].startswith("/owner/login/")


# AC3: the data migration


def create_owner_values() -> None:
    migration = importlib.import_module("owner_content.migrations.0002_owner_values")
    migration.create_owner_values(django_apps, None)


@pytest.mark.django_db
def test_migration_created_the_record_with_the_owners_values() -> None:
    record = the_record()

    assert (record.price_from_million, record.price_to_million) == (13, 14)
    assert (record.phone, record.whatsapp, record.zalo) == ("0945 384 500",) * 3
    assert record.owner_first_name == "Bún"
    assert record.reply_time == "within an hour"


@pytest.mark.django_db
def test_migration_leaves_an_existing_record_as_it_is() -> None:
    SiteSettings.objects.update(price_from_million=20, price_to_million=None, phone="")

    create_owner_values()

    record = the_record()
    assert (record.price_from_million, record.price_to_million, record.phone) == (20, None, "")


@pytest.mark.django_db
def test_migration_creates_the_record_when_there_is_none() -> None:
    SiteSettings.objects.all().delete()

    create_owner_values()

    record = the_record()
    assert (record.price_from_million, record.price_to_million) == (13, 14)
    assert (record.phone, record.whatsapp, record.zalo) == ("0945 384 500",) * 3


@pytest.mark.django_db
def test_migrations_match_the_model() -> None:
    call_command("makemigrations", "owner_content", check=True, dry_run=True, verbosity=0)


# AC4: the service


@pytest.mark.django_db
def test_service_gives_the_owners_lines_and_links() -> None:
    value = site_settings()

    assert value.price_line == "From 13–14 million VND a month"
    assert "–" in value.price_line  # an en dash, not a hyphen
    assert value.channels == OWNER_CHANNELS
    assert value.greeting == "Hi, I'm Bún."
    assert value.reply_line == "I usually reply within an hour."


@pytest.mark.django_db
def test_service_value_is_frozen() -> None:
    value = site_settings()

    with pytest.raises(FrozenInstanceError):
        value.greeting = "Hello"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        value.channels[0].link = "tel:0"  # type: ignore[misc]
    assert isinstance(value.channels, tuple)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("price_from", "price_to", "line"),
    [
        (13, 14, "From 13–14 million VND a month"),
        (13, None, "From 13 million VND a month"),
        (13, 13, "From 13 million VND a month"),
        (None, None, None),
        (None, 14, None),
    ],
)
def test_price_line(price_from: int | None, price_to: int | None, line: str | None) -> None:
    SiteSettings.objects.update(price_from_million=price_from, price_to_million=price_to)

    assert site_settings().price_line == line


@pytest.mark.django_db
@pytest.mark.parametrize(
    "number", ["0945 384 500", "+84 945 384 500", "0945.384.500", "+84-945-384-500", "945384500"]
)
def test_every_way_to_write_the_number_gives_the_same_links(number: str) -> None:
    SiteSettings.objects.update(phone=number, whatsapp=number, zalo=number)

    assert site_settings().channels == OWNER_CHANNELS


@pytest.mark.django_db
def test_only_filled_channels_are_given_in_the_order_call_whatsapp_zalo() -> None:
    SiteSettings.objects.update(phone="", whatsapp="0945 384 500", zalo="0901 234 567")

    assert site_settings().channels == (
        Channel(key="whatsapp", label="WhatsApp", link="https://wa.me/84945384500"),
        Channel(key="zalo", label="Zalo", link="https://zalo.me/0901234567"),
    )

    SiteSettings.objects.update(phone="0945 384 500", whatsapp="", zalo="")

    assert site_settings().channels == (OWNER_CHANNELS[0],)


@pytest.mark.django_db
def test_a_stored_number_that_is_not_valid_gives_no_channel() -> None:
    SiteSettings.objects.update(phone="call me", whatsapp="   ", zalo="0945 384 500")

    assert site_settings().channels == (OWNER_CHANNELS[2],)


@pytest.mark.django_db
def test_greeting_and_reply_line_follow_the_record() -> None:
    SiteSettings.objects.update(owner_first_name="Hưng", reply_time="the same day")

    value = site_settings()

    assert value.greeting == "Hi, I'm Hưng."
    assert value.reply_line == "I usually reply the same day."


# AC5: one query, and no record is not an error


@pytest.mark.django_db
def test_service_makes_exactly_one_query(django_assert_num_queries: DjangoAssertNumQueries) -> None:
    with django_assert_num_queries(1):
        site_settings()


@pytest.mark.django_db
def test_without_a_record_the_service_gives_the_defaults_in_one_query(
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    SiteSettings.objects.all().delete()

    with django_assert_num_queries(1):
        value = site_settings()

    assert value.price_line is None
    assert value.channels == ()
    assert value.greeting == "Hi, I'm Bún."
    assert value.reply_line == "I usually reply within an hour."


# AC6, as changed by the one page (issue #38): `/` shows the values in one query


@pytest.mark.django_db
@pytest.mark.parametrize("address", PUBLIC_ADDRESSES)
def test_no_page_shows_the_values_or_asks_the_database(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    # `/` reads the site settings in one query; the old addresses redirect to it (one-page AC5).
    with django_assert_num_queries(1):
        response = client.get(address, follow=True)

    html = response.content.decode()
    assert response.status_code == 200
    # The price line, and the Call, WhatsApp and Zalo links in the rent chapter, the contact
    # chapter and the phone bar.
    assert "From 13–14 million VND a month" in html
    for channel in OWNER_CHANNELS:
        for place in ("rent", "contact", "bar"):
            assert (
                f'href="{channel.link}" data-channel="{channel.key}" data-place="{place}"' in html
            ), f"{address} has no {channel.label} link in {place}"
