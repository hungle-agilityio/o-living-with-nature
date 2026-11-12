"""Create the owner's admin account, or reset its password, from the environment.

Render's free plan has no shell, so the start command runs this at every start: the owner
changes the password by changing `OWNER_PASSWORD` on Render. The password is never printed.
"""

import os
from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

MIN_PASSWORD_LENGTH = 12


@dataclass(frozen=True)
class Outcome:
    message: str
    ok: bool = True


def ensure_owner(username: str, password: str) -> Outcome:
    """Make sure the user `username` can sign in with `password`; say what was done."""
    if not username or not password:
        return Outcome("owner skipped: OWNER_USERNAME and OWNER_PASSWORD are not set")
    if len(password) < MIN_PASSWORD_LENGTH:
        return Outcome(
            f"owner not ready: OWNER_PASSWORD needs at least {MIN_PASSWORD_LENGTH} characters",
            ok=False,
        )
    user = User.objects.filter(username=username).first()
    if user is None:
        User.objects.create_superuser(username=username, password=password)
        return Outcome("owner ready: created")
    user.set_password(password)
    user.save(update_fields=["password"])
    return Outcome("owner ready: password updated")


class Command(BaseCommand):
    help = "Create the owner's admin account, or set its password, from OWNER_USERNAME and OWNER_PASSWORD."  # noqa: E501

    def handle(self, *args: Any, **options: Any) -> None:
        outcome = ensure_owner(
            os.environ.get("OWNER_USERNAME", ""), os.environ.get("OWNER_PASSWORD", "")
        )
        self.stdout.write(outcome.message)
        if not outcome.ok:
            raise SystemExit(1)
