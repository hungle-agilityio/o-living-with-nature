"""A note's text as safe HTML: paragraphs, `## ` subheadings, line breaks and links."""

import re

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe

_ADDRESS = re.compile(r"https?://[^\s<>\"']+")
_TRAILING = ".,;:!?)"


def _line(text: str) -> str:
    """One line with its web addresses linked; every piece is escaped on its own."""
    pieces: list[str] = []
    position = 0
    for match in _ADDRESS.finditer(text):
        address = match.group(0).rstrip(_TRAILING)
        pieces.append(escape(text[position : match.start()]))
        shown = escape(address)
        pieces.append(f'<a href="{shown}" rel="noopener" target="_blank">{shown}</a>')
        position = match.start() + len(address)
    pieces.append(escape(text[position:]))
    return "".join(pieces)


def _paragraph(lines: list[str]) -> str:
    return "<p>" + "<br>".join(_line(line) for line in lines) + "</p>"


def to_html(text: str) -> SafeString:
    """The note's text as HTML; everything that is not markup of ours is escaped."""
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    parts: list[str] = []
    for block in blocks:
        if not block.strip():
            continue
        lines = block.split("\n")
        if lines[0].startswith("## "):
            parts.append(f"<h2>{escape(lines[0][3:])}</h2>")
            lines = lines[1:]
            if lines:
                parts.append(_paragraph(lines))
        else:
            parts.append(_paragraph(lines))
    return mark_safe("\n".join(parts))
