"""The journal notes (journal spec, issue #136)."""

import counter.services
from django.db import migrations, models

TEXT_HELP = (
    "A blank line starts a new paragraph. A line that starts with ## is a subheading. "
    "Web addresses become links by themselves."
)


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JournalPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=120, verbose_name="Title")),
                (
                    "slug",
                    models.SlugField(
                        help_text=(
                            "The page is /journal/ followed by this address. Made from the "
                            "title; change it only before you publish."
                        ),
                        max_length=80,
                        unique=True,
                        verbose_name="Address",
                    ),
                ),
                (
                    "summary",
                    models.CharField(
                        help_text="One or two sentences, shown in the list.",
                        max_length=240,
                        verbose_name="Summary",
                    ),
                ),
                (
                    "body",
                    models.TextField(help_text=TEXT_HELP, max_length=8000, verbose_name="Text"),
                ),
                (
                    "title_vi",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Leave the Vietnamese empty and the note shows only on the "
                            "English pages."
                        ),
                        max_length=120,
                        verbose_name="Title (Vietnamese)",
                    ),
                ),
                (
                    "summary_vi",
                    models.CharField(
                        blank=True, max_length=240, verbose_name="Summary (Vietnamese)"
                    ),
                ),
                (
                    "body_vi",
                    models.TextField(
                        blank=True,
                        help_text=TEXT_HELP,
                        max_length=8000,
                        verbose_name="Text (Vietnamese)",
                    ),
                ),
                (
                    "cover",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("beach-sunset", "photos/beach-sunset.jpg"),
                            ("bedroom", "photos/bedroom.jpg"),
                            ("corner", "photos/corner.jpg"),
                            ("first-light", "photos/first-light.jpg"),
                            ("garden-evening", "photos/garden-evening.jpg"),
                            ("kitchen", "photos/kitchen.jpg"),
                            ("leaves", "photos/leaves.jpg"),
                            ("lightwell", "photos/lightwell.jpg"),
                            ("lit-window", "photos/lit-window.jpg"),
                            ("market", "photos/market.jpg"),
                            ("mezzanine", "photos/mezzanine.jpg"),
                            ("street", "photos/street.jpg"),
                            ("tea", "photos/tea.jpg"),
                            ("veranda", "photos/veranda.jpg"),
                        ],
                        help_text=(
                            "One of the site's photos (they show the Illustrative label), "
                            "or none. Uploading is not possible."
                        ),
                        max_length=40,
                        verbose_name="Cover photo",
                    ),
                ),
                (
                    "date",
                    models.DateField(
                        default=counter.services.today_in_da_nang,
                        help_text="Shown on the note; the list is newest first.",
                        verbose_name="Date",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published")],
                        default="draft",
                        help_text="Only published notes are on the site.",
                        max_length=9,
                        verbose_name="status",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "journal post",
                "verbose_name_plural": "journal posts",
                "ordering": ["-date", "-pk"],
            },
        ),
    ]
