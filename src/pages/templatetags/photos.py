"""`{% photo "key" ratio="4 / 3" %}`: the media slot of a photo of `pages.photos`."""

from typing import Any

from django import template
from django.templatetags.static import static

from pages import photos

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
    return {
        "ratio": ratio,
        "photo": static(entry.path),
        "alt": entry.alt,
        "width": entry.width,
        "height": entry.height,
        "eager": _first_photo_of_the_page(context),
        "illustrative": entry.illustrative,
        "credit": entry.credit,
    }


def _first_photo_of_the_page(context: template.Context) -> bool:
    # `render_context` gives each included template its own layer on top of the first one; the
    # first layer lives for the whole render, so the mark set there is seen by every chapter.
    page_state = context.render_context.dicts[0]
    if page_state.get(_EAGER_USED):
        return False
    page_state[_EAGER_USED] = "yes"
    return True
