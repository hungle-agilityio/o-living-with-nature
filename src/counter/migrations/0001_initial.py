from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DailyCount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("day", models.DateField()),
                (
                    "kind",
                    models.CharField(choices=[("view", "View"), ("click", "Click")], max_length=5),
                ),
                (
                    "channel",
                    models.CharField(
                        blank=True,
                        choices=[("call", "Call"), ("whatsapp", "WhatsApp"), ("zalo", "Zalo")],
                        max_length=8,
                    ),
                ),
                (
                    "place",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("bar", "Phone bar"),
                            ("rent", "Rent chapter"),
                            ("contact", "Contact chapter"),
                        ],
                        max_length=7,
                    ),
                ),
                ("count", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Daily count",
                "verbose_name_plural": "Contact counts",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("day", "kind", "channel", "place"),
                        name="counter_one_row_per_day",
                    )
                ],
            },
        ),
    ]
