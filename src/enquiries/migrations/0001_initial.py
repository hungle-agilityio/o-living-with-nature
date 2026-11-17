from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Enquiry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("name", models.CharField(max_length=80)),
                ("reply_to", models.CharField(max_length=120)),
                ("move_in", models.CharField(blank=True, max_length=7)),
                (
                    "stay",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("1-3", "1–3 months"),
                            ("3-6", "3–6 months"),
                            ("6-12", "6–12 months"),
                            ("12+", "A year or more"),
                        ],
                        max_length=4,
                    ),
                ),
                ("message", models.TextField(max_length=1000)),
                (
                    "language",
                    models.CharField(
                        choices=[("en", "English"), ("vi", "Vietnamese")], max_length=2
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "New"), ("replied", "Replied")],
                        default="new",
                        max_length=7,
                    ),
                ),
            ],
            options={
                "verbose_name": "Enquiry",
                "verbose_name_plural": "Enquiries",
                "ordering": ["-created_at"],
            },
        ),
    ]
