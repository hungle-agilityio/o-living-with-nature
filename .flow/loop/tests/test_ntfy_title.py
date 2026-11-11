"""The ntfy title header must be sendable when the display name is not ASCII."""

import base64

from agent_tick import header_text


def test_ascii_title_is_unchanged() -> None:
    assert header_text("Living with Nature") == "Living with Nature"


def test_non_ascii_title_is_rfc2047_encoded_and_latin1_safe() -> None:
    value = header_text("Ở — Living with Nature")

    value.encode("latin-1")  # http.client encodes headers as latin-1
    assert value.startswith("=?UTF-8?B?") and value.endswith("?=")
    assert base64.b64decode(value[10:-2]).decode() == "Ở — Living with Nature"
