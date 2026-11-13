"""The site settings as the lines and links the pages show."""

from dataclasses import dataclass

from owner_content.models import SiteSettings
from owner_content.phones import national_number


@dataclass(frozen=True)
class Channel:
    """One contact button: `key` is `call`, `whatsapp` or `zalo`."""

    key: str
    label: str
    link: str


@dataclass(frozen=True)
class SiteSettingsValue:
    price_line: str | None
    channels: tuple[Channel, ...]
    greeting: str
    reply_line: str
    # The owner's first name alone, for the signature under the rent quote.
    first_name: str = ""


def site_settings() -> SiteSettingsValue:
    """The owner's settings, read in one query; the model defaults when there is no record."""
    record = SiteSettings.objects.order_by("pk").first() or SiteSettings()
    return SiteSettingsValue(
        price_line=_price_line(record.price_from_million, record.price_to_million),
        channels=_channels(record),
        greeting=f"Hi, I'm {record.owner_first_name}.",
        reply_line=f"I usually reply {record.reply_time}.",
        first_name=record.owner_first_name,
    )


def _price_line(price_from: int | None, price_to: int | None) -> str | None:
    if price_from is None:
        return None
    if price_to is None or price_to <= price_from:
        return f"From {price_from} million VND a month"
    return f"From {price_from}–{price_to} million VND a month"


def _channels(record: SiteSettings) -> tuple[Channel, ...]:
    """One entry per filled channel, in the order Call, WhatsApp, Zalo."""
    candidates = (
        ("call", "Call", record.phone, "tel:+84{}"),
        ("whatsapp", "WhatsApp", record.whatsapp, "https://wa.me/84{}"),
        ("zalo", "Zalo", record.zalo, "https://zalo.me/0{}"),
    )
    channels: list[Channel] = []
    for key, label, raw, link in candidates:
        number = national_number(raw)
        if number is not None:
            channels.append(Channel(key=key, label=label, link=link.format(number)))
    return tuple(channels)
