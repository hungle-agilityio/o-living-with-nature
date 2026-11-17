"""The two first notes, stored as drafts (journal spec "First notes", issue #136)."""

from datetime import date
from typing import Any

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

TEN_MINUTES = "ten-minutes-from-everything"
STAYING = "staying-a-month-or-longer"

_NOTES: list[dict[str, Any]] = [
    {
        "slug": TEN_MINUTES,
        "title": "Ten minutes from everything",
        "date": date(2026, 11, 16),
        "cover": "market",
        "summary": (
            "A supermarket across the road, the market and the beach about ten minutes away, "
            "the airport about fifteen."
        ),
        "body": "\n\n".join(
            [
                "People often ask me what is near the house. Here is the short version.",
                "## Every day",
                "There is a supermarket right across the road, so water, fruit and the small "
                "things are a few steps away. The market is about ten minutes away.",
                "## The sea",
                "The beach is about ten minutes away.",
                "## Arriving and leaving",
                "The airport is about fifteen minutes away.",
                "If you would like to see exactly where the house is, ask me and I will send "
                "you the location.",
            ]
        ),
        "title_vi": "Mười phút là tới mọi thứ",
        "summary_vi": (
            "Siêu thị ngay bên kia đường, chợ và biển khoảng mười phút, sân bay khoảng "
            "mười lăm phút."
        ),
        "body_vi": "\n\n".join(
            [
                "Nhiều bạn hỏi mình quanh nhà có gì. Đây là bản ngắn gọn.",
                "## Hằng ngày",
                "Siêu thị ở ngay bên kia đường, nước, trái cây và đồ lặt vặt chỉ cách vài "
                "bước. Chợ cách khoảng mười phút.",
                "## Biển",
                "Biển cách khoảng mười phút.",
                "## Đi và về",
                "Sân bay cách khoảng mười lăm phút.",
                "Nếu bạn muốn biết chính xác nhà ở đâu, cứ hỏi, mình gửi vị trí cho bạn.",
            ]
        ),
        "status": "draft",
    },
    {
        "slug": STAYING,
        "title": "Staying a month or longer",
        "date": date(2026, 11, 12),
        "cover": "",
        "summary": "What the rent includes, and what I take care of for you.",
        "body": "\n\n".join(
            [
                "The house is rented whole, by the month. The minimum stay is one month, "
                "with two months' deposit.",
                "## Included",
                "Basic furniture. Up to 300 kWh of electricity and 10 m³ of water each month; "
                "anything above is charged at the official rate. Garden care once a week. "
                "Cleaning can be arranged.",
                "## Paperwork",
                "I take care of temporary residence registration for you.",
                "## Pets",
                "Let's talk.",
            ]
        ),
        "title_vi": "",
        "summary_vi": "",
        "body_vi": "",
        "status": "draft",
    },
]


def add_first_drafts(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    model = apps.get_model("journal", "JournalPost")
    for note in _NOTES:
        if not model.objects.filter(slug=note["slug"]).exists():
            model.objects.create(**note)


def remove_first_drafts(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    model = apps.get_model("journal", "JournalPost")
    model.objects.filter(slug__in=[TEN_MINUTES, STAYING], status="draft").delete()


class Migration(migrations.Migration):
    dependencies = [("journal", "0001_initial")]

    operations = [migrations.RunPython(add_first_drafts, remove_first_drafts)]
