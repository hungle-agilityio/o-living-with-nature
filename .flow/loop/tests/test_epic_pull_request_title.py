"""The epic pull request title carries the "[EPIC]" prefix exactly once (#30)."""

import pytest
from epic_pull_request import title_for


@pytest.mark.parametrize(
    "epic_title",
    [
        "[EPIC] Site shell and look",
        "[epic] Site shell and look",
        "Epic: Site shell and look",
        "[EPIC] Epic: Site shell and look",
        "Site shell and look",
    ],
)
def test_title_has_the_prefix_once(epic_title: str) -> None:
    assert title_for({"title": epic_title}) == "[EPIC] Site shell and look"


def test_word_starting_with_epic_is_kept() -> None:
    assert title_for({"title": "Epicentre map"}) == "[EPIC] Epicentre map"
