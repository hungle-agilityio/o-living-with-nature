"""Keeping the site settings' journal flags in step with the published notes."""

from journal.models import JournalPost, vietnamese_complete
from owner_content.models import SiteSettings


def refresh_flags() -> None:
    """Set `journal_en` and `journal_vi` on the first site settings record (created if none).

    The Vietnamese test is Python's `strip()`, the rule of `JournalPost.has_vietnamese`.
    """
    rows = list(
        JournalPost.objects.filter(status=JournalPost.Status.PUBLISHED).values_list(
            "title_vi", "summary_vi", "body_vi"
        )
    )
    record = SiteSettings.objects.order_by("pk").first() or SiteSettings()
    record.journal_en = bool(rows)
    record.journal_vi = any(vietnamese_complete(*row) for row in rows)
    if record.pk is None:
        record.save()
    else:  # only the flags: a full save could overwrite a value the owner saved meanwhile
        record.save(update_fields=["journal_en", "journal_vi"])
