"""The move-in months and stay lengths of the enquiry form, in English and Vietnamese."""

from datetime import date

_MONTHS_EN = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

STAY_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "1-3": "1–3 months",
        "3-6": "3–6 months",
        "6-12": "6–12 months",
        "12+": "A year or more",
    },
    "vi": {
        "1-3": "1–3 tháng",
        "3-6": "3–6 tháng",
        "6-12": "6–12 tháng",
        "12+": "Từ một năm trở lên",
    },
}

NOT_SURE: dict[str, str] = {"en": "Not sure yet", "vi": "Chưa chắc"}


def move_in_months(today: date) -> list[str]:
    """The 12 months `YYYY-MM` starting with the month of `today`."""
    months = []
    for offset in range(12):
        index = today.month - 1 + offset
        months.append(f"{today.year + index // 12:04d}-{index % 12 + 1:02d}")
    return months


def _split(value: str) -> tuple[int, int]:
    year, month = value.split("-")
    return int(year), int(month)


def month_label(value: str, language: str) -> str:
    """`"2027-01"` is "January 2027" in English and "Tháng 1/2027" in Vietnamese."""
    year, month = _split(value)
    if language == "vi":
        return f"Tháng {month}/{year}"
    return f"{_MONTHS_EN[month - 1]} {year}"


def short_month_label(value: str) -> str:
    """`"2027-01"` is "Jan 2027"."""
    year, month = _split(value)
    return f"{_MONTHS_EN[month - 1][:3]} {year}"
