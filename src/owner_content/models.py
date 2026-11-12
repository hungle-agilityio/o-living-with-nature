"""The one record of site settings the owner edits in the admin at /owner/."""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from owner_content.phones import validate_vietnamese_number

PRICE_ERROR = "Price to cannot be lower than Price from."
PHONE_HELP = "A Vietnamese number like 0945 384 500 or +84 945 384 500. Empty hides the button."
PRICE_RULES = [MinValueValidator(1), MaxValueValidator(999)]


class SiteSettings(models.Model):
    price_from_million = models.PositiveSmallIntegerField(
        "Price from (million VND a month)",
        null=True,
        blank=True,
        validators=PRICE_RULES,
        help_text="The lower end of the monthly rent, in million VND.",
    )
    price_to_million = models.PositiveSmallIntegerField(
        "Price to (million VND a month)",
        null=True,
        blank=True,
        validators=PRICE_RULES,
        help_text="The upper end. Leave empty for one price.",
    )
    phone = models.CharField(
        "Phone (Call button)",
        max_length=30,
        blank=True,
        validators=[validate_vietnamese_number],
        help_text=PHONE_HELP,
    )
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=30,
        blank=True,
        validators=[validate_vietnamese_number],
        help_text=PHONE_HELP,
    )
    zalo = models.CharField(
        "Zalo",
        max_length=30,
        blank=True,
        validators=[validate_vietnamese_number],
        help_text=PHONE_HELP,
    )
    owner_first_name = models.CharField(
        "Your first name",
        max_length=40,
        default="Bún",
        help_text='Shown as "Hi, I\'m …".',
    )
    reply_time = models.CharField(
        "Usual reply time",
        max_length=60,
        default="within an hour",
        help_text='Shown as "I usually reply …", for example "within an hour".',
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:
        return "Site settings"

    def clean(self) -> None:
        super().clean()
        if (
            self.price_from_million is not None
            and self.price_to_million is not None
            and self.price_to_million < self.price_from_million
        ):
            raise ValidationError({"price_to_million": PRICE_ERROR})
