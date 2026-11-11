"""The https redirect with debug off, and the setting that switches it off for a local run.

The settings are read once per process, so each case loads them in a fresh Python process.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

SRC = Path(__file__).resolve().parents[2]

# Asks the security middleware, as the site runs it, whether a plain request is redirected.
PROBE = """
import json
import django
from django.conf import settings
from django.http import HttpResponse
from django.middleware.security import SecurityMiddleware
from django.test import RequestFactory

django.setup()
middleware = SecurityMiddleware(lambda request: HttpResponse())
answers = {}
for path in ("/", "/healthz/"):
    response = middleware.process_request(RequestFactory().get(path, HTTP_HOST="localhost"))
    answers[path] = None if response is None else [response.status_code, response["Location"]]
print(json.dumps({"setting": settings.SECURE_SSL_REDIRECT, "answers": answers}))
"""


def probe(**extra: str) -> dict[str, Any]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("DJANGO_") and key != "PYTHONPATH"
    }
    env.update(
        {
            "DJANGO_SETTINGS_MODULE": "config.settings",
            "DJANGO_DEBUG": "0",
            "DJANGO_SECRET_KEY": "test-only-not-secret-value-for-the-settings-probe",
            "PYTHONPATH": str(SRC),
            **extra,
        }
    )
    done = subprocess.run(
        [sys.executable, "-c", PROBE], env=env, capture_output=True, text=True, check=True
    )
    result: dict[str, Any] = json.loads(done.stdout.strip().splitlines()[-1])
    return result


def test_debug_off_still_redirects_to_https_by_default() -> None:
    result = probe()

    assert result["setting"] is True
    assert result["answers"]["/"] == [301, "https://localhost/"]


def test_the_setting_switches_the_redirect_off() -> None:
    result = probe(DJANGO_SECURE_SSL_REDIRECT="0")

    assert result["setting"] is False
    assert result["answers"]["/"] is None


def test_the_health_page_never_redirects() -> None:
    assert probe()["answers"]["/healthz/"] is None
    assert probe(DJANGO_SECURE_SSL_REDIRECT="0")["answers"]["/healthz/"] is None
