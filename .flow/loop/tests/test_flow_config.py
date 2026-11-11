"""The flow is configured for this repository; also keeps `pytest` from finding nothing."""

import flow_config

EXPECTED_REPO = "hungle-agilityio/o-living-with-nature"


def test_flow_toml_names_this_repository() -> None:
    assert flow_config.load().project_repo == EXPECTED_REPO
