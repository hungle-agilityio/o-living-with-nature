"""`{% photo "key" ratio="4 / 3" %}` and `{% area_loop %}`: media slots of `pages.photos`;
`{% floor_plan %}`: the walk through the house, whose blocks link to those photos."""

from typing import Any

from django import template
from django.templatetags.static import static

from pages import floor_plan as floor_plan_service
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


@register.inclusion_tag("includes/media.html")
def area_loop(ratio: str = "16 / 9") -> dict[str, Any]:
    """The slot's values for the Hòa Xuân loop; a missing file gives the empty state. The
    poster stands in for the video under reduced motion, so it always loads lazily."""
    loop = photos.area_loop()
    if loop is None:
        return {"ratio": ratio}
    return {
        "ratio": ratio,
        "video": static(loop.mp4),
        "webm": static(loop.webm),
        "photo": static(loop.poster),
        "alt": loop.label,
        "width": loop.width,
        "height": loop.height,
        "eager": False,
        "illustrative": loop.illustrative,
        "credit": loop.credit,
    }


@register.inclusion_tag("includes/floor_plan.html")
def floor_plan() -> dict[str, Any]:
    """The blocks of the walk through the house, each with the address of its photo, if any."""
    return {
        "blocks": [
            {
                "name": block.name,
                "kind": block.kind,
                "photo": block.photo,
                "href": static(block.photo.path) if block.photo else None,
            }
            for block in floor_plan_service.blocks()
        ]
    }


def _first_photo_of_the_page(context: template.Context) -> bool:
    # `render_context` gives each included template its own layer on top of the first one; the
    # first layer lives for the whole render, so the mark set there is seen by every chapter.
    page_state = context.render_context.dicts[0]
    if page_state.get(_EAGER_USED):
        return False
    page_state[_EAGER_USED] = "yes"
    return True
