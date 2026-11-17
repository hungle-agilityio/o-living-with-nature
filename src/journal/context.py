"""The context of the two journal pages: the cards of the list, one note, their search tags and
the language switch. The views only read the request and render."""

from dataclasses import dataclass
from typing import Any

from django.core.paginator import Page
from django.templatetags.static import static

from journal import reading
from journal.models import JournalPost
from journal.text import to_html
from owner_content.services import SiteSettingsValue
from pages import language, seo
from pages.photos import Photo

ARTICLE = "article"
WEBSITE = "website"


@dataclass(frozen=True)
class NoteCard:
    """One note as a page shows it, in the page language."""

    slug: str
    title: str
    summary: str
    url: str
    iso_date: str
    date_label: str
    cover: Photo | None

    @property
    def cover_src(self) -> str:
        """The address of the cover's file, or "" without a cover."""
        return static(self.cover.path) if self.cover else ""

    @property
    def cover_ratio(self) -> str:
        """The cover's aspect ratio for the media slot, for example "4 / 3"."""
        return f"{self.cover.width} / {self.cover.height}" if self.cover else ""


def list_path(lang: str) -> str:
    """`/journal/` or `/vi/journal/`."""
    return language.home_path(lang) + "journal/"


def note_path(lang: str, slug: str) -> str:
    """`/journal/<slug>/` or `/vi/journal/<slug>/`."""
    return f"{list_path(lang)}{slug}/"


def _has_journal(owner: SiteSettingsValue, lang: str) -> bool:
    return owner.journal_vi if language.normalise(lang) == language.VI else owner.journal_en


def _other(lang: str) -> str:
    return language.EN if language.normalise(lang) == language.VI else language.VI


def _alternates(en_path: str, vi_path: str) -> tuple[tuple[str, str], ...]:
    en_url = seo.canonical_url(en_path)
    return (
        (language.EN, en_url),
        (language.VI, seo.canonical_url(vi_path)),
        ("x-default", en_url),
    )


def card(post: JournalPost, lang: str) -> NoteCard:
    vietnamese = language.normalise(lang) == language.VI
    return NoteCard(
        slug=post.slug,
        title=post.title_vi if vietnamese else post.title,
        summary=post.summary_vi if vietnamese else post.summary,
        url=note_path(lang, post.slug),
        iso_date=post.date.isoformat(),
        date_label=reading.date_label(post.date, lang),
        cover=reading.cover_of(post),
    )


def _page_link(lang: str, number: int) -> str:
    return list_path(lang) if number == 1 else f"{list_path(lang)}?page={number}"


def list_context(lang: str, number: int, owner: SiteSettingsValue) -> dict[str, Any]:
    """The list page `number` of the language; `Http404` when there is nothing to show."""
    page: Page[JournalPost] = reading.list_page(lang, number)
    words = language.texts("journal", lang)
    other = _other(lang)
    both = owner.journal_en and owner.journal_vi
    lead = words["lead"].replace("{name}", owner.first_name)
    head = seo.page_head(
        lang,
        title=words["list_title"],
        description=lead,
        path=list_path(lang),
        og_type=WEBSITE,
        alternates=_alternates(list_path(language.EN), list_path(language.VI)) if both else (),
    )
    switch_href = list_path(other) if _has_journal(owner, other) else language.home_path(other)
    return {
        "seo": head,
        "owner": owner,
        "lang_switch": language.switch_to(lang, switch_href),
        "lead": lead,
        "cards": [card(post, lang) for post in page.object_list],
        "newer_url": _page_link(lang, page.number - 1) if page.has_previous() else "",
        "older_url": _page_link(lang, page.number + 1) if page.has_next() else "",
    }


def note_context(lang: str, slug: str, owner: SiteSettingsValue) -> dict[str, Any]:
    """The note at this address in the language; `Http404` when it is not published there."""
    post = reading.note(lang, slug)
    vietnamese = language.normalise(lang) == language.VI
    words = language.texts("journal", lang)
    other = _other(lang)
    note = card(post, lang)
    in_both = post.has_vietnamese
    if in_both:
        switch_href = note_path(other, post.slug)
    elif _has_journal(owner, other):
        switch_href = list_path(other)
    else:
        switch_href = language.home_path(other)
    head = seo.page_head(
        lang,
        title=words["note_title"].replace("{title}", note.title),
        description=note.summary,
        path=note.url,
        og_type=ARTICLE,
        alternates=(
            _alternates(note_path(language.EN, post.slug), note_path(language.VI, post.slug))
            if in_both
            else ()
        ),
    )
    other_post = reading.other_note(post, lang)
    price = f"{owner.price_line}. {owner.reply_line}" if owner.price_line else owner.reply_line
    return {
        "seo": head,
        "owner": owner,
        "lang_switch": language.switch_to(lang, switch_href),
        "note": note,
        "body_html": to_html(post.body_vi if vietnamese else post.body),
        "list_url": list_path(lang),
        "price_reply": price,
        "other": _link(other_post, lang) if other_post is not None else None,
    }


def _link(post: JournalPost, lang: str) -> dict[str, str]:
    """The address and title of a note in the language, for the "Another note" line."""
    title = post.title_vi if language.normalise(lang) == language.VI else post.title
    return {"url": note_path(lang, post.slug), "title": title}
