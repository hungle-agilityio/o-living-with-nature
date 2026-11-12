"""System checks of the owner's content: is the production database one that lasts?"""

import os
from collections.abc import Sequence
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, Warning, register

W001_MESSAGE = (
    "DATABASE_URL is not set: on Render the SQLite file is wiped on every deploy "
    "and the owner's settings are lost."
)


@register()
def database_url_is_set(
    app_configs: Sequence[AppConfig] | None, **kwargs: Any
) -> list[CheckMessage]:
    """Warn when production (debug off) would run on the default SQLite file.

    A warning, not an error: the app still starts. `DJANGO_DB_NAME` means someone chose the
    SQLite file on purpose (a local check with debug off), so it is quiet too.
    """
    # Stripped like the settings do: a DATABASE_URL of spaces only is not a database address.
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if settings.DEBUG or database_url or os.environ.get("DJANGO_DB_NAME"):
        return []
    return [Warning(W001_MESSAGE, id="config.W001")]
