"""The walk through the house: the blocks of the schematic floor plan (one-page spec AC16, AC17).

A schematic until the architect's plan exists: the parts of the house from the front garden to
the back garden, not their real layout. A block whose photo is in `pages.photos` (and whose file
is found) links to it. The block names live in `pages.texts.house` (keys `block_*`).
"""

from dataclasses import dataclass

from pages import photos
from pages.language import EN, texts


@dataclass(frozen=True)
class _Part:
    key: str  # the key of the block's name in `pages.texts.house`
    kind: str  # "garden", "room" or "wide" (a room drawn across the whole plan)
    photo_key: str | None = None


_PARTS = (
    _Part("block_front_garden", "garden"),
    _Part("block_living_kitchen", "wide", "kitchen"),
    _Part("block_light_well", "room", "lightwell"),
    _Part("block_bedroom_1", "room", "bedroom"),
    _Part("block_bedroom_2", "room", "bedroom"),
    _Part("block_bathroom", "room"),
    _Part("block_mezzanine", "room", "mezzanine"),
    _Part("block_veranda", "wide", "veranda"),
    _Part("block_back_garden", "garden"),
    _Part("block_laundry", "wide"),
)


@dataclass(frozen=True)
class Block:
    """One block of the plan: its name, how it is drawn, and its photo when it has one."""

    name: str
    kind: str
    photo: photos.Photo | None


def blocks(language: str = EN) -> list[Block]:
    """The blocks in walking order, front garden first, named in `language` (English by
    default); a missing photo file gives no photo."""
    names = texts("house", language)
    return [
        Block(
            name=names[part.key],
            kind=part.kind,
            photo=photos.photo(part.photo_key) if part.photo_key else None,
        )
        for part in _PARTS
    ]
