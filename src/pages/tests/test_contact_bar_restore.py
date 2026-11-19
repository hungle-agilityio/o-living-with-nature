"""Epic review of contact-one-place: the phone bar's script after a page restore.

The bar steps away while a form field has focus (AC4). A page restored from the back-forward
cache may still have focus in the form without a focusout ever firing, so the script reads the
focus again on pageshow; otherwise the bar could stay away for the rest of the visit.
"""

from django.conf import settings

SCRIPT = settings.SRC_DIR / "static" / "js" / "contact-bar.js"


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_script_reads_the_focus_again_when_the_page_is_shown() -> None:
    script = _script()

    assert 'addEventListener("pageshow"' in script
    assert "form.contains(document.activeElement)" in script
    assert len(script.encode("utf-8")) < 4000
