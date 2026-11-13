"""Daily totals of page views and contact-button presses.

One row per day (in Đà Nẵng), kind, channel and place. Nothing about the visitor is stored:
no IP address, user agent, referrer, cookie or visitor id.
"""

from django.db import models


class DailyCount(models.Model):
    class Kind(models.TextChoices):
        VIEW = "view", "View"
        CLICK = "click", "Click"

    class Channel(models.TextChoices):
        CALL = "call", "Call"
        WHATSAPP = "whatsapp", "WhatsApp"
        ZALO = "zalo", "Zalo"

    class Place(models.TextChoices):
        BAR = "bar", "Phone bar"
        RENT = "rent", "Rent chapter"
        CONTACT = "contact", "Contact chapter"

    day = models.DateField()
    kind = models.CharField(max_length=5, choices=Kind.choices)
    # A view has an empty channel and place.
    channel = models.CharField(max_length=8, choices=Channel.choices, blank=True)
    place = models.CharField(max_length=7, choices=Place.choices, blank=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Daily count"
        verbose_name_plural = "Contact counts"
        constraints = [
            models.UniqueConstraint(
                fields=["day", "kind", "channel", "place"], name="counter_one_row_per_day"
            )
        ]

    def __str__(self) -> str:
        return f"{self.day} {self.kind} {self.channel} {self.place}: {self.count}"
