"""The Vietnamese reply time the owner writes in the admin (vietnamese spec, task T3, issue #106).

Rows M26 (the field, its migration and its place in the admin) and M27 (an empty value is refused).
"""

import re
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models import CharField
from django.test import Client

from owner_content.models import SiteSettings

CHANGELIST = "/owner/owner_content/sitesettings/"
BEFORE = [("owner_content", "0002_owner_values")]
AFTER = [("owner_content", "0003_sitesettings_reply_time_vi")]
VI_HELP = (
    'Shown on the Vietnamese page as "Mình thường trả lời …", for example "trong vòng một giờ".'
)
EN_HELP = 'Shown on the English page as "I usually reply …", for example "within an hour".'
REQUIRED = "This field is required."


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
        "reply_time_vi": "trong vòng một giờ",
    }
    data.update(changes)
    return data


# M26 (AC1)


def test_m26_the_field_has_its_label_length_default_and_help_text() -> None:
    field = SiteSettings._meta.get_field("reply_time_vi")

    assert isinstance(field, CharField)
    assert field.verbose_name == "Usual reply time (Vietnamese)"
    assert field.max_length == 60
    assert field.default == "trong vòng một giờ"
    assert field.help_text == VI_HELP
    assert not field.blank


def test_m26_the_english_reply_time_help_names_the_english_page() -> None:
    assert SiteSettings._meta.get_field("reply_time").help_text == EN_HELP


def test_m26_the_field_is_declared_right_after_reply_time() -> None:
    names = [field.name for field in SiteSettings._meta.get_fields()]

    assert names.index("reply_time_vi") == names.index("reply_time") + 1


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_m26_a_record_made_before_the_migration_gets_the_default() -> None:
    executor = MigrationExecutor(connection)
    try:
        executor.migrate(BEFORE)
        old_model = executor.loader.project_state(BEFORE).apps.get_model(
            "owner_content", "SiteSettings"
        )
        old_model.objects.all().delete()
        old_model.objects.create(owner_first_name="Hưng", reply_time="the same day")

        executor = MigrationExecutor(connection)
        executor.migrate(AFTER)
        new_model = executor.loader.project_state(AFTER).apps.get_model(
            "owner_content", "SiteSettings"
        )

        record = new_model.objects.get()
        assert record.reply_time_vi == "trong vòng một giờ"
        assert (record.owner_first_name, record.reply_time) == ("Hưng", "the same day")
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db
def test_m26_the_admin_page_lists_the_field_right_under_the_usual_reply_time(
    owner_client: Client,
) -> None:
    record = SiteSettings.objects.get()

    response = owner_client.get(f"{CHANGELIST}{record.pk}/change/")

    html = response.content.decode()
    assert response.status_code == 200
    assert "Usual reply time (Vietnamese)" in html
    assert VI_HELP in html.replace("&quot;", '"').replace("&#x27;", "'")
    inputs = re.findall(r'<(?:input|select|textarea)\b[^>]*\bname="([a-z_]+)"', html)
    names = [name for name in inputs if name != "csrfmiddlewaretoken"]
    assert names[names.index("reply_time") + 1] == "reply_time_vi"
    assert html.index('for="id_reply_time"') < html.index('for="id_reply_time_vi"')


# M27 (AC2)


@pytest.mark.django_db
def test_m27_an_empty_vietnamese_reply_time_is_refused_and_nothing_is_saved(
    owner_client: Client,
) -> None:
    record = SiteSettings.objects.get()

    response = owner_client.post(
        f"{CHANGELIST}{record.pk}/change/",
        form_data(reply_time_vi="", owner_first_name="Hưng"),
    )

    assert response.status_code == 200
    assert REQUIRED in response.content.decode()
    saved = SiteSettings.objects.get()
    assert saved.reply_time_vi == "trong vòng một giờ"
    assert saved.owner_first_name == "Bún"


@pytest.mark.django_db
def test_m27_a_filled_vietnamese_reply_time_is_saved(owner_client: Client) -> None:
    record = SiteSettings.objects.get()

    response = owner_client.post(
        f"{CHANGELIST}{record.pk}/change/", form_data(reply_time_vi="trong ngày")
    )

    assert response.status_code == 302
    assert SiteSettings.objects.get().reply_time_vi == "trong ngày"
