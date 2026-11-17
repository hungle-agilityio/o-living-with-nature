"""What the journal pages read: the published notes of a language, one page of them, one note,
the note to suggest next, a date in the page language and a note's cover photo."""

from datetime import date

from django.core.paginator import EmptyPage, Page, Paginator
from django.db.models import Case, IntegerField, Q, QuerySet, Value, When
from django.http import Http404

from journal.models import JournalPost
from pages import language
from pages.photos import Photo, photo

PER_PAGE = 12

_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def published(lang: str) -> QuerySet[JournalPost]:
    """The published notes of the language, newest first; in Vietnamese only the notes whose
    Vietnamese title, summary and text are all filled."""
    notes = JournalPost.objects.filter(status=JournalPost.Status.PUBLISHED)
    if language.normalise(lang) == language.VI:
        notes = notes.exclude(title_vi="").exclude(summary_vi="").exclude(body_vi="")
    return notes.order_by("-date", "-pk")


def list_page(lang: str, number: int) -> Page[JournalPost]:
    """Page `number` (from 1) of the list; `Http404` when the language has no published note
    or the page is out of range."""
    paginator = Paginator(published(lang), PER_PAGE, allow_empty_first_page=False)
    try:
        return paginator.page(number)
    except EmptyPage as error:
        raise Http404("No such journal page") from error


def note(lang: str, slug: str) -> JournalPost:
    """The published note at this address in the language, else `Http404`."""
    try:
        return published(lang).get(slug=slug)
    except JournalPost.DoesNotExist as error:
        raise Http404("No such journal note") from error


def other_note(post: JournalPost, lang: str) -> JournalPost | None:
    """The next older published note of the language, else the newest other one, else None
    (one query)."""
    older = Q(date__lt=post.date) | Q(date=post.date, pk__lt=post.pk)
    return (
        published(lang)
        .exclude(pk=post.pk)
        .annotate(
            older=Case(When(older, then=Value(1)), default=Value(0), output_field=IntegerField())
        )
        .order_by("-older", "-date", "-pk")
        .first()
    )


def date_label(day: date, lang: str) -> str:
    """ "16 November 2026" in English (whatever the active locale), "16/11/2026" in Vietnamese."""
    if language.normalise(lang) == language.VI:
        return f"{day.day:02d}/{day.month:02d}/{day.year}"
    return f"{day.day} {_MONTHS[day.month - 1]} {day.year}"


def cover_of(post: JournalPost) -> Photo | None:
    """The note's cover photo; None without a cover, with an unknown key or a missing file."""
    return photo(post.cover) if post.cover else None
