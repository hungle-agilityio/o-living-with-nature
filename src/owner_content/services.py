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


@dataclass(frozen=True)
class _OwnerWords:
    """The owner's lines of one language; `{}` takes the owner's value."""

    greeting: str
    reply_line: str
    one_price: str
    price_range: str
    call: str


# Built from the owner's values, so they stay here beside each other rather than in
# pages/texts (vietnamese spec AC5 excepts the owner's values; decisions/T3.md).
_WORDS = {
    "en": _OwnerWords(
        greeting="Hi, I'm {}.",
        reply_line="I usually reply {}.",
        one_price="From {} million VND a month",
        price_range="From {}–{} million VND a month",
        call="Call",
    ),
    "vi": _OwnerWords(
        greeting="Chào bạn, mình là {}.",
        reply_line="Mình thường trả lời {}.",
        one_price="Từ {} triệu đồng mỗi tháng",
        price_range="Từ {}–{} triệu đồng mỗi tháng",
        call="Gọi điện",
    ),
}


def site_settings(language: str = "en") -> SiteSettingsValue:
    """The owner's settings in the page language (`"vi"`; anything else is English), read in
    one query; the model defaults when there is no record."""
    record = SiteSettings.objects.order_by("pk").first() or SiteSettings()
    vietnamese = language.lower().split("-")[0] == "vi"
    words = _WORDS["vi" if vietnamese else "en"]
    return SiteSettingsValue(
        price_line=_price_line(record.price_from_million, record.price_to_million, words),
        channels=_channels(record, words),
        greeting=words.greeting.format(record.owner_first_name),
        reply_line=words.reply_line.format(
            record.reply_time_vi if vietnamese else record.reply_time
        ),
        first_name=record.owner_first_name,
    )


def _price_line(price_from: int | None, price_to: int | None, words: _OwnerWords) -> str | None:
    if price_from is None:
        return None
    if price_to is None or price_to <= price_from:
        return words.one_price.format(price_from)
    return words.price_range.format(price_from, price_to)


def _channels(record: SiteSettings, words: _OwnerWords) -> tuple[Channel, ...]:
    """One entry per filled channel, in the order Call, WhatsApp, Zalo."""
    candidates = (
        ("call", words.call, record.phone, "tel:+84{}"),
        ("whatsapp", "WhatsApp", record.whatsapp, "https://wa.me/84{}"),
        ("zalo", "Zalo", record.zalo, "https://zalo.me/0{}"),
    )
    channels: list[Channel] = []
    for key, label, raw, link in candidates:
        number = national_number(raw)
        if number is not None:
            channels.append(Channel(key=key, label=label, link=link.format(number)))
    return tuple(channels)
