"""`{% photo "key" ratio="4 / 3" %}` and `{% area_loop %}`: media slots of `pages.photos`;
`{% floor_plan %}`: the walk through the house, a hand-drawn plan and the list of its rooms."""

from typing import Any

from django import template
from django.templatetags.static import static

from pages import floor_plan as floor_plan_service
from pages import house_drawing, language, photos
from pages.templatetags.texts import alt_text, credit_text

register = template.Library()

# Kept for the whole render of one page, across included templates (each chapter is one).
_EAGER_USED = "pages.photos.eager_used"


@register.inclusion_tag("includes/media.html", takes_context=True)
def photo(context: template.Context, key: str, ratio: str = "3 / 2") -> dict[str, Any]:
    """The slot's values for the photo of `key`; an unknown key or a missing file gives the
    empty state. The first photo of the page loads at once, the others lazily."""
    entry = photos.photo(key)
    if entry is None:
        return {"ratio": ratio}
    lang = language.of_context(context)
    return {
        "ratio": ratio,
        "lang": lang,
        "photo": static(entry.path),
        "alt": alt_text(entry, lang),
        "width": entry.width,
        "height": entry.height,
        "eager": _first_photo_of_the_page(context),
        "illustrative": entry.illustrative,
        "credit": language.credit_for(entry.credit, lang),
    }


@register.inclusion_tag("includes/media.html", takes_context=True)
def area_loop(context: template.Context, ratio: str = "16 / 9") -> dict[str, Any]:
    """The slot's values for the Hòa Xuân loop; a missing file gives the empty state. The
    poster stands in for the video under reduced motion, so it always loads lazily."""
    loop = photos.area_loop()
    if loop is None:
        return {"ratio": ratio}
    lang = language.of_context(context)
    return {
        "ratio": ratio,
        "lang": lang,
        "video": static(loop.mp4),
        "webm": static(loop.webm),
        "photo": static(loop.poster),
        "alt": alt_text(loop, lang),
        "width": loop.width,
        "height": loop.height,
        "eager": False,
        "illustrative": loop.illustrative,
        "credit": language.credit_for(loop.credit, lang),
    }


@register.inclusion_tag("includes/floor_plan.html", takes_context=True)
def floor_plan(context: template.Context) -> dict[str, Any]:
    """The values of the walk through the house: the drawing (defs, section, sideways and upright
    plan) and the rooms in walking order, each with its number and, when it has one, its photo.
    No query."""
    lang = language.of_context(context)
    words = language.texts("house", lang)
    rooms = floor_plan_service.rooms(language=lang)
    items: list[dict[str, Any]] = []
    for number, room in enumerate(rooms, 1):
        item: dict[str, Any] = {
            "key": room.key,
            "name": room.name,
            "text": room.text,
            "number": f"{number:02d} {words['room_of']} {len(rooms):02d}",
        }
        if room.photo:
            item.update(
                src=static(room.photo.path),
                alt=alt_text(room.photo, lang),
                credit=credit_text(room.photo.credit, lang),
                width=room.photo.width,
                height=room.photo.height,
                illustrative=room.photo.illustrative,
            )
        items.append(item)
    return {
        "lang": lang,
        "count": len(rooms),
        "defs": house_drawing.DEFS,
        "section": house_drawing.section_svg(words),
        "plan_h": house_drawing.plan_svg(rooms, words, "h"),
        "plan_v": house_drawing.plan_svg(rooms, words, "v"),
        "rooms": items,
    }


def _first_photo_of_the_page(context: template.Context) -> bool:
    # `render_context` gives each included template its own layer on top of the first one; the
    # first layer lives for the whole render, so the mark set there is seen by every chapter.
    page_state = context.render_context.dicts[0]
    if page_state.get(_EAGER_USED):
        return False
    page_state[_EAGER_USED] = "yes"
    return True
