"""An enquiry a visitor leaves through the form: what they wrote, nothing that identifies them."""

from django.db import models


class Stay(models.TextChoices):
    ONE_TO_THREE = "1-3", "1–3 months"
    THREE_TO_SIX = "3-6", "3–6 months"
    SIX_TO_TWELVE = "6-12", "6–12 months"
    YEAR_OR_MORE = "12+", "A year or more"


class Status(models.TextChoices):
    NEW = "new", "New"
    REPLIED = "replied", "Replied"


LANGUAGES = [("en", "English"), ("vi", "Vietnamese")]


class Enquiry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    name = models.CharField(max_length=80)
    reply_to = models.CharField(max_length=120)
    move_in = models.CharField(max_length=7, blank=True)  # YYYY-MM
    stay = models.CharField(max_length=4, blank=True, choices=Stay.choices)
    message = models.TextField(max_length=1000)
    language = models.CharField(max_length=2, choices=LANGUAGES)
    status = models.CharField(max_length=7, choices=Status.choices, default=Status.NEW)

    class Meta:
        verbose_name = "Enquiry"
        verbose_name_plural = "Enquiries"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        # No personal data: the admin, logs and errors show only the number.
        return f"Enquiry {self.pk}"
