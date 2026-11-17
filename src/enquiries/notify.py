"""The push to the owner's phone when an enquiry is stored (ntfy)."""

import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger("enquiries")


def push_new_enquiry() -> None:
    """Send one push with no personal data; a failure is logged by class name and swallowed."""
    if not settings.NTFY_TOPIC_URL:
        return
    try:
        request = urllib.request.Request(
            settings.NTFY_TOPIC_URL,
            data="New enquiry on Ở".encode(),
            method="POST",
            headers={
                "Title": "New enquiry",
                "Click": f"{settings.SITE_BASE_URL}/owner/enquiries/enquiry/",
                "Tags": "house",
            },
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            if not 200 <= response.status < 300:
                raise urllib.error.HTTPError(
                    settings.NTFY_TOPIC_URL, response.status, "bad status", response.headers, None
                )
    except Exception as error:
        logger.warning("ntfy push failed: %s", type(error).__name__)
