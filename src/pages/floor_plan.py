"""The walk through the house: the blocks of the schematic floor plan (one-page spec AC16, AC17).

A schematic until the architect's plan exists: the parts of the house from the front garden to
the back garden, not their real layout. A block whose photo is in `pages.photos` (and whose file
is found) links to it.
"""

from dataclasses import dataclass

from pages import photos


@dataclass(frozen=True)
class _Part:
    name: str
    kind: str  # "garden", "room" or "wide" (a room drawn across the whole plan)
    photo_key: str | None = None


_PARTS = (
    _Part("Front garden", "garden"),
    _Part("Living room and kitchen", "wide", "kitchen"),
    _Part("Light well", "room", "lightwell"),
    _Part("Bedroom 1", "room", "bedroom"),
    _Part("Bedroom 2", "room", "bedroom"),
    _Part("Bathroom", "room"),
    _Part("Mezzanine", "room", "mezzanine"),
    _Part("Covered veranda", "wide", "veranda"),
    _Part("Back garden", "garden"),
    _Part("Laundry, drying and storage", "wide"),
)


@dataclass(frozen=True)
class Block:
    """One block of the plan: its name, how it is drawn, and its photo when it has one."""

    name: str
    kind: str
    photo: photos.Photo | None


def blocks() -> list[Block]:
    """The blocks in walking order, front garden first; a missing photo file gives no photo."""
    return [
        Block(
            name=part.name,
            kind=part.kind,
            photo=photos.photo(part.photo_key) if part.photo_key else None,
        )
        for part in _PARTS
    ]
