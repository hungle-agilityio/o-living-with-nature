"""The list of illustrative photos and the Hòa Xuân loop (owner-content AC13 to AC16).

The list in `pages.photos` must say exactly what `docs/specs/owner-content/media-credits.md`
records, and every file it names must be in `src/static/media/`.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.test import Client
from pytest_django import DjangoAssertNumQueries
from pytest_mock import MockerFixture

from pages import photos

REPO = Path(settings.SRC_DIR).parent
MEDIA = Path(settings.SRC_DIR) / "static" / "media"
CREDITS = REPO / "docs" / "specs" / "owner-content" / "media-credits.md"
PAGES = ["/", "/house/", "/hoa-xuan/", "/faq/", "/contact/"]

# One row of a table in media-credits.md: key, size, alt text or label, credit, source.
_ROW = re.compile(r"^\| `([\w-]+)` \| (\d+)x(\d+) \| (.+?) \| (.+?) \| (\S+) \|$", re.MULTILINE)

Row = tuple[str, int, int, str, str, str]


def _entries() -> list[photos.Photo | photos.AreaLoop]:
    """Every entry of the list: the photos, then the loop."""
    return [*photos.PHOTOS.values(), photos.AREA_LOOP]


def _rows(section: str) -> list[Row]:
    """The rows of the table under the heading that starts with `section`."""
    text = CREDITS.read_text(encoding="utf-8")
    start = text.index(f"## {section}")
    end = text.find("\n## ", start + 1)
    part = text[start : end if end != -1 else len(text)]
    return [
        (key, int(width), int(height), shows, credit, source)
        for key, width, height, shows, credit, source in _ROW.findall(part)
    ]


# AC1


def test_list_holds_the_fourteen_photos_of_the_credits_file_exactly() -> None:
    recorded = _rows("Photos")
    assert len(recorded) == 14

    listed = [(p.key, p.width, p.height, p.alt, p.credit, p.source) for p in photos.PHOTOS.values()]

    assert listed == recorded
    assert list(photos.PHOTOS) == [row[0] for row in recorded]


def test_list_holds_the_one_loop_of_the_credits_file_exactly() -> None:
    (recorded,) = _rows("Loop")
    loop = photos.AREA_LOOP

    assert (loop.key, loop.width, loop.height, loop.label, loop.credit, loop.source) == recorded
    assert recorded[0] == "area"


def test_every_entry_is_illustrative_with_the_pexels_licence() -> None:
    for entry in _entries():
        assert entry.illustrative is True
        assert entry.licence == "Pexels License"


# AC2


@pytest.mark.parametrize("key", list(photos.PHOTOS))
def test_photo_returns_the_entry_with_its_static_path(key: str) -> None:
    entry = photos.photo(key)

    assert entry is photos.PHOTOS[key]
    assert entry.path == f"media/photos/{key}.jpg"


@pytest.mark.parametrize("key", ["", "nope", "area", "../hero/day", "LIGHTWELL"])
def test_photo_is_none_for_an_unknown_key(key: str) -> None:
    assert photos.photo(key) is None


def test_photo_is_none_when_the_finders_do_not_find_the_file(mocker: MockerFixture) -> None:
    find = mocker.patch("pages.photos.finders.find", return_value=None)

    assert photos.photo("lightwell") is None
    find.assert_called_once_with("media/photos/lightwell.jpg")


def test_area_loop_returns_the_three_paths() -> None:
    loop = photos.area_loop()

    assert loop is photos.AREA_LOOP
    assert loop.mp4 == "media/area/area.mp4"
    assert loop.webm == "media/area/area.webm"
    assert loop.poster == "media/area/area.jpg"


@pytest.mark.parametrize("missing", ["area.mp4", "area.webm", "area.jpg"])
def test_area_loop_is_none_when_any_file_is_missing(mocker: MockerFixture, missing: str) -> None:
    mocker.patch(
        "pages.photos.finders.find",
        side_effect=lambda path: None if path.endswith(missing) else f"/found/{path}",
    )

    assert photos.area_loop() is None


# AC3


def test_every_listed_file_exists_in_static_media() -> None:
    paths = [p.path for p in photos.PHOTOS.values()]
    loop = photos.AREA_LOOP
    paths += [loop.mp4, loop.webm, loop.poster]

    assert len(paths) == 17
    for path in paths:
        assert path.startswith("media/")
        assert (MEDIA / path.removeprefix("media/")).is_file(), path


def test_every_entry_has_words_a_credit_and_a_pexels_source() -> None:
    words = [p.alt for p in photos.PHOTOS.values()] + [photos.AREA_LOOP.label]
    assert all(text.strip() for text in words)

    for entry in _entries():
        assert entry.credit.strip()
        assert entry.source.startswith("https://www.pexels.com/")


# AC4


@pytest.mark.django_db
@pytest.mark.parametrize("address", PAGES)
def test_no_page_shows_the_photos_and_none_asks_the_database(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries, address: str
) -> None:
    with django_assert_num_queries(0):
        response = client.get(address, follow=True)

    assert response.status_code == 200
    html = response.content.decode()
    assert "media/photos/" not in html
    assert "media/area/" not in html
