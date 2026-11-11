"""The health page the host checks, and the home page renders."""

from django.test import Client


def test_health_page_says_ok(client: Client) -> None:
    response = client.get("/healthz/")

    assert response.status_code == 200
    assert response.content == b"ok"


def test_home_page_renders(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Living with Nature" in response.content.decode()
