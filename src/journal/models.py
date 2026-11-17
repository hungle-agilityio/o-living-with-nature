"""The owner's journal notes, written in the admin at /owner/."""

from django.core.exceptions import ValidationError
from django.db import models

from counter.services import today_in_da_nang
from pages.photos import PHOTOS

TEXT_HELP = (
    "A blank line starts a new paragraph. A line that starts with ## is a subheading. "
    "Web addresses become links by themselves."
)
VIETNAMESE_ERROR = "Fill the Vietnamese title, summary and text, or leave all three empty."
COVER_CHOICES = [(key, f"photos/{key}.jpg") for key in sorted(PHOTOS)]


def vietnamese_complete(title_vi: str, summary_vi: str, body_vi: str) -> bool:
    """True when the Vietnamese title, summary and text are all filled (Python `strip()`)."""
    return all(value.strip() for value in (title_vi, summary_vi, body_vi))


class JournalPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField("Title", max_length=120)
    slug = models.SlugField(
        "Address",
        max_length=80,
        unique=True,
        help_text="The page is /journal/ followed by this address. Made from the title; "
        "change it only before you publish.",
    )
    summary = models.CharField(
        "Summary", max_length=240, help_text="One or two sentences, shown in the list."
    )
    body = models.TextField("Text", max_length=8000, help_text=TEXT_HELP)
    title_vi = models.CharField(
        "Title (Vietnamese)",
        max_length=120,
        blank=True,
        help_text="Leave the Vietnamese empty and the note shows only on the English pages.",
    )
    summary_vi = models.CharField("Summary (Vietnamese)", max_length=240, blank=True)
    body_vi = models.TextField(
        "Text (Vietnamese)", max_length=8000, blank=True, help_text=TEXT_HELP
    )
    cover = models.CharField(
        "Cover photo",
        max_length=40,
        blank=True,
        choices=COVER_CHOICES,
        help_text="One of the site's photos (they show the Illustrative label), or none. "
        "Uploading is not possible.",
    )
    date = models.DateField(
        "Date",
        default=today_in_da_nang,
        help_text="Shown on the note; the list is newest first.",
    )
    status = models.CharField(
        "status",
        max_length=9,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text="Only published notes are on the site.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "journal post"
        verbose_name_plural = "journal posts"
        ordering = ["-date", "-pk"]

    def __str__(self) -> str:
        return self.title

    def _vietnamese_filled(self) -> list[bool]:
        return [bool(v.strip()) for v in (self.title_vi, self.summary_vi, self.body_vi)]

    def clean(self) -> None:
        super().clean()
        if 0 < sum(self._vietnamese_filled()) < 3:
            raise ValidationError(VIETNAMESE_ERROR)

    @property
    def has_vietnamese(self) -> bool:
        return vietnamese_complete(self.title_vi, self.summary_vi, self.body_vi)

    def get_absolute_url(self) -> str:
        return f"/journal/{self.slug}/"
