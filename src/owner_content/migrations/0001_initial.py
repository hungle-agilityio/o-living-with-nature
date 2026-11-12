import django.core.validators
from django.db import migrations, models

import owner_content.phones

PHONE_HELP = "A Vietnamese number like 0945 384 500 or +84 945 384 500. Empty hides the button."


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "price_from_million",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="The lower end of the monthly rent, in million VND.",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(999),
                        ],
                        verbose_name="Price from (million VND a month)",
                    ),
                ),
                (
                    "price_to_million",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="The upper end. Leave empty for one price.",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(999),
                        ],
                        verbose_name="Price to (million VND a month)",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        help_text=PHONE_HELP,
                        max_length=30,
                        validators=[owner_content.phones.validate_vietnamese_number],
                        verbose_name="Phone (Call button)",
                    ),
                ),
                (
                    "whatsapp",
                    models.CharField(
                        blank=True,
                        help_text=PHONE_HELP,
                        max_length=30,
                        validators=[owner_content.phones.validate_vietnamese_number],
                        verbose_name="WhatsApp",
                    ),
                ),
                (
                    "zalo",
                    models.CharField(
                        blank=True,
                        help_text=PHONE_HELP,
                        max_length=30,
                        validators=[owner_content.phones.validate_vietnamese_number],
                        verbose_name="Zalo",
                    ),
                ),
                (
                    "owner_first_name",
                    models.CharField(
                        default="Bún",
                        help_text='Shown as "Hi, I\'m …".',
                        max_length=40,
                        verbose_name="Your first name",
                    ),
                ),
                (
                    "reply_time",
                    models.CharField(
                        default="within an hour",
                        help_text='Shown as "I usually reply …", for example "within an hour".',
                        max_length=60,
                        verbose_name="Usual reply time",
                    ),
                ),
            ],
            options={
                "verbose_name": "Site settings",
                "verbose_name_plural": "Site settings",
            },
        ),
    ]
