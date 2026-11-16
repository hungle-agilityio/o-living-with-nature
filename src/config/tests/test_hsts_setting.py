"""HSTS with debug off and the silenced subdomain and preload warnings (ADR-031).

The settings are read once per process, so each case loads them in a fresh Python process.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

SRC = Path(__file__).resolve().parents[2]
ROOT = SRC.parent
SECRET = "k9Xv2Lq8ZpR4tW7yB1nM6cD3fG5hJ0sA-eU_iO!aQzXwCvBnMlKjHgFdSpOiUyTrEwQ"

PROBE = """
import json
import django
from django.conf import settings
from django.http import HttpResponse
from django.middleware.security import SecurityMiddleware
from django.test import RequestFactory

django.setup()
middleware = SecurityMiddleware(lambda request: HttpResponse())
secure = middleware(RequestFactory().get("/", secure=True))
health = middleware.process_request(RequestFactory().get("/healthz/", HTTP_HOST="localhost"))
print(
    json.dumps(
        {
            "seconds": settings.SECURE_HSTS_SECONDS,
            "subdomains": settings.SECURE_HSTS_INCLUDE_SUBDOMAINS,
            "preload": settings.SECURE_HSTS_PRELOAD,
            "silenced": settings.SILENCED_SYSTEM_CHECKS,
            "header": secure.get("Strict-Transport-Security"),
            "health": None if health is None else health.status_code,
        }
    )
)
"""


def _clean_env() -> dict[str, str]:
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("DJANGO_") and key not in {"DATABASE_URL", "RENDER", "PYTHONPATH"}
    }


def probe(**extra: str) -> dict[str, Any]:
    env = _clean_env()
    env.update({"DJANGO_SETTINGS_MODULE": "config.settings", "PYTHONPATH": str(SRC), **extra})
    if env.get("DJANGO_DEBUG") == "0":
        env.setdefault("DJANGO_SECRET_KEY", SECRET)
    done = subprocess.run(
        [sys.executable, "-c", PROBE], env=env, capture_output=True, text=True, check=True
    )
    result: dict[str, Any] = json.loads(done.stdout.strip().splitlines()[-1])
    return result


def test_debug_off_sends_hsts_for_one_year_without_subdomains_or_preload() -> None:
    result = probe(DJANGO_DEBUG="0")

    assert result["seconds"] == 31536000
    assert result["subdomains"] is False
    assert result["preload"] is False


def test_debug_on_leaves_hsts_off() -> None:
    assert probe()["seconds"] == 0


def test_only_the_subdomains_and_preload_warnings_are_silenced_in_both_modes() -> None:
    expected = ["security.W005", "security.W021"]

    assert probe()["silenced"] == expected
    assert probe(DJANGO_DEBUG="0")["silenced"] == expected


def test_deploy_check_with_production_settings_passes_with_two_silenced() -> None:
    env = _clean_env()
    env.update(
        {
            "DJANGO_DEBUG": "0",
            "DJANGO_SECRET_KEY": SECRET,
            "DJANGO_ALLOWED_HOSTS": "o-living-web.onrender.com",
        }
    )
    done = subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert done.returncode == 0, done.stderr
    assert "(2 silenced)" in done.stdout + done.stderr


def test_https_response_carries_the_hsts_header_and_the_health_page_does_not_redirect() -> None:
    result = probe(DJANGO_DEBUG="0")

    assert result["header"] == "max-age=31536000"
    assert result["health"] is None
