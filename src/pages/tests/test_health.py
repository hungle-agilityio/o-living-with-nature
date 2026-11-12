"""The health page the host checks, and the home page renders."""

import pytest
from django.test import Client

# The home page reads the site settings (one query), so every test here may use the database.
pytestmark = pytest.mark.django_db


def test_health_page_says_ok(client: Client) -> None:
    response = client.get("/healthz/")

    assert response.status_code == 200
    assert response.content == b"ok"


def test_home_page_renders(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Living with Nature" in response.content.decode()
