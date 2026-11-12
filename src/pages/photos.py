"""The illustrative photos and the Hòa Xuân loop: sizes, words, credits and sources.

Stock media that stands in until the owner's own photos exist. The list repeats
`docs/specs/owner-content/media-credits.md`; a test keeps the two the same.
"""

from dataclasses import dataclass

from django.contrib.staticfiles import finders

LICENCE = "Pexels License"

_PHOTOS_FOLDER = "media/photos"
_AREA_FOLDER = "media/area"
_PEXELS = "https://www.pexels.com"


@dataclass(frozen=True)
class Photo:
    """One illustrative photo: its size in pixels, alt text, credit and source page."""

    key: str
    width: int
    height: int
    alt: str
    credit: str
    source: str
    illustrative: bool = True
    licence: str = LICENCE

    @property
    def path(self) -> str:
        """The static path of the file."""
        return f"{_PHOTOS_FOLDER}/{self.key}.jpg"


@dataclass(frozen=True)
class AreaLoop:
    """The Hòa Xuân loop: its size in pixels, label, credit and source page."""

    key: str
    width: int
    height: int
    label: str
    credit: str
    source: str
    illustrative: bool = True
    licence: str = LICENCE

    @property
    def mp4(self) -> str:
        """The static path of the mp4 (H.264) file."""
        return f"{_AREA_FOLDER}/{self.key}.mp4"

    @property
    def webm(self) -> str:
        """The static path of the WebM file."""
        return f"{_AREA_FOLDER}/{self.key}.webm"

    @property
    def poster(self) -> str:
        """The static path of the poster photo (the loop's first frame)."""
        return f"{_AREA_FOLDER}/{self.key}.jpg"


_ANONYMOUS = "Photo: Pexels"

_LIST = (
    Photo(
        key="lightwell",
        width=1200,
        height=1600,
        alt="An indoor atrium with hanging plants under a skylight",
        credit="Photo: Fatmanur Üzüm / Pexels",
        source=f"{_PEXELS}/photo/indoor-atrium-with-hanging-plants-and-skylight-34545626/",
    ),
    Photo(
        key="veranda",
        width=1600,
        height=1060,
        alt="A shaded back veranda with wicker chairs and tropical plants",
        credit=_ANONYMOUS,
        source=(
            f"{_PEXELS}/photo/backyard-of-modern-residential-villa-with-comfy-wicker-furniture"
            "-and-tropical-plants-6430734/"
        ),
    ),
    Photo(
        key="market",
        width=1600,
        height=1280,
        alt="A woman selling vegetables on a street market",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/woman-selling-vegetables-on-the-street-19442603/",
    ),
    Photo(
        key="bedroom",
        width=1600,
        height=1067,
        alt="A calm bedroom with a made bed",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/bed-2563388/",
    ),
    Photo(
        key="corner",
        width=1200,
        height=1600,
        alt="Houseplants by a window next to an armchair",
        credit=_ANONYMOUS,
        source=(
            f"{_PEXELS}/photo/houseplants-by-the-window-and-next-to-an-armchair-in-a-room-16269026/"
        ),
    ),
    Photo(
        key="kitchen",
        width=901,
        height=1600,
        alt="A sunlit kitchen with wooden furniture",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/cozy-sunlit-kitchen-with-wooden-furniture-29148452/",
    ),
    Photo(
        key="leaves",
        width=1067,
        height=1600,
        alt="The shadow of a palm leaf on a wall",
        credit="Photo: Tim Mossholder / Pexels",
        source=f"{_PEXELS}/photo/shadow-of-palm-leaf-on-a-wall-14046313/",
    ),
    Photo(
        key="garden-evening",
        width=1067,
        height=1600,
        alt="String lights in a garden in the evening",
        credit="Photo: CharlieBrown / Pexels",
        source=f"{_PEXELS}/photo/photo-of-string-light-12125368/",
    ),
    Photo(
        key="street",
        width=1600,
        height=1067,
        alt="A quiet Vietnamese village street",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/quaint-vietnamese-village-street-scene-in-quy-nh-n-30228478/",
    ),
    Photo(
        key="first-light",
        width=1067,
        height=1600,
        alt="Walking barefoot on the beach at dawn",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/woman-walking-barefoot-on-beach-at-dawn-18790609/",
    ),
    Photo(
        key="beach-sunset",
        width=1600,
        height=856,
        alt="People walking on the beach at sunset",
        credit="Photo: Gorazd Nikoloski / Pexels",
        source=f"{_PEXELS}/photo/people-walking-on-beach-at-sunset-15506230/",
    ),
    Photo(
        key="lit-window",
        width=1067,
        height=1600,
        alt="A house with lit windows at night",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/a-low-angle-shot-of-a-house-at-night-9592440/",
    ),
    Photo(
        key="tea",
        width=1067,
        height=1600,
        alt="A cup of tea by the window",
        credit=_ANONYMOUS,
        source=f"{_PEXELS}/photo/cozy-moment-with-tea-by-the-window-31146888/",
    ),
    Photo(
        key="mezzanine",
        width=1600,
        height=1067,
        alt="A staircase with a wooden railing and plants in a light house",
        credit=_ANONYMOUS,
        source=(
            f"{_PEXELS}/photo/staircase-with-wooden-railing-decorated-with-plants-in-light"
            "-modern-house-5824879/"
        ),
    ),
)

PHOTOS: dict[str, Photo] = {entry.key: entry for entry in _LIST}

AREA_LOOP = AreaLoop(
    key="area",
    width=1280,
    height=720,
    label="Riding a motorbike along a road",
    credit="Video: Pexels",
    source=f"{_PEXELS}/video/traveling-the-road-in-motorcycle-4309733/",
)


def photo(key: str) -> Photo | None:
    """The photo of a key, or None when the key is unknown or its file is not found.

    With None the media slot shows its empty state, never a broken image.
    """
    entry = PHOTOS.get(key)
    if entry is None or finders.find(entry.path) is None:
        return None
    return entry


def area_loop() -> AreaLoop | None:
    """The Hòa Xuân loop, or None when any of its three files is missing."""
    loop = AREA_LOOP
    if any(finders.find(path) is None for path in (loop.mp4, loop.webm, loop.poster)):
        return None
    return loop
