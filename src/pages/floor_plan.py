"""The walk through the house: the seven rooms of the hand-drawn plan (house-plan-2d spec, T1).

The plot is 6 x 18 m, in plan units of one decimetre: `u` runs from the gate (0) to the back fence
(`LENGTH`), `v` across the plot (0 to `WIDTH`). Each room has its outline as (u, v) points, its
kind, its name and text (`pages.texts.house`, keys `block_*` and `about_*`) and its photo when
`pages.photos` has one and the file is found. `pages.house_drawing` draws the rooms.
"""

from dataclasses import dataclass

from pages import photos
from pages.language import EN, texts

LENGTH = 180
WIDTH = 60


@dataclass(frozen=True)
class Room:
    """One room of the plan: kind is "garden", "room" or "wet"; shape its (u, v) outline."""

    key: str
    kind: str
    shape: tuple[tuple[int, int], ...]
    name: str
    text: str
    photo: photos.Photo | None


def _rect(u0: int, u1: int, v0: int, v1: int) -> tuple[tuple[int, int], ...]:
    return ((u0, v0), (u1, v0), (u1, v1), (u0, v1))


# key, kind, shape, photo key (None: the room has no photo), in walking order
_ROOMS: tuple[tuple[str, str, tuple[tuple[int, int], ...], str | None], ...] = (
    ("front-garden", "garden", _rect(0, 90, 0, 35), None),
    ("kitchen", "room", _rect(0, 90, 35, WIDTH), "kitchen"),
    ("bathroom", "wet", _rect(90, 112, 0, 25), None),
    ("laundry", "wet", _rect(90, 112, 35, WIDTH), None),
    ("bedroom-1", "room", ((112, 0), (LENGTH, 0), (LENGTH, 15), (168, 30), (112, 30)), "bedroom"),
    ("bedroom-2", "room", ((112, 30), (168, 30), (145, WIDTH), (112, WIDTH)), "bedroom"),
    ("back-garden", "garden", ((LENGTH, 15), (LENGTH, WIDTH), (145, WIDTH)), "garden-evening"),
)


def rooms(language: str = EN) -> list[Room]:
    """The rooms in walking order, front garden first, named and told in `language` (English by
    default); a missing photo file gives no photo."""
    words = texts("house", language)
    result: list[Room] = []
    for key, kind, shape, photo_key in _ROOMS:
        suffix = key.replace("-", "_")
        result.append(
            Room(
                key=key,
                kind=kind,
                shape=shape,
                name=words["block_" + suffix],
                text=words["about_" + suffix],
                photo=photos.photo(photo_key) if photo_key else None,
            )
        )
    return result
