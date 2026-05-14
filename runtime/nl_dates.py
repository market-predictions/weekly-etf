from __future__ import annotations

import re
from datetime import datetime

DUTCH_WEEKDAYS = {
    "Monday": "Maandag",
    "Tuesday": "Dinsdag",
    "Wednesday": "Woensdag",
    "Thursday": "Donderdag",
    "Friday": "Vrijdag",
    "Saturday": "Zaterdag",
    "Sunday": "Zondag",
}

DUTCH_MONTHS = {
    "January": "januari",
    "February": "februari",
    "March": "maart",
    "April": "april",
    "May": "mei",
    "June": "juni",
    "July": "juli",
    "August": "augustus",
    "September": "september",
    "October": "oktober",
    "November": "november",
    "December": "december",
}

DATE_WITH_WEEKDAY_RE = re.compile(
    r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+"
    r"(\d{1,2})\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"(20\d{2})\b"
)

DATE_NO_WEEKDAY_RE = re.compile(
    r"\b(\d{1,2})\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"(20\d{2})\b"
)

ISO_DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")


def localize_english_report_dates(text: str) -> str:
    """Localize English report-date strings in Dutch client-facing output.

    Handles all weekdays and all months, not a single hard-coded report date.
    It intentionally leaves ISO dates such as 2026-05-13 unchanged because they
    are audit/state identifiers and table data, not prose dates.
    """

    def repl_with_weekday(match: re.Match[str]) -> str:
        weekday, day, month, year = match.groups()
        return f"{DUTCH_WEEKDAYS[weekday]} {int(day)} {DUTCH_MONTHS[month]} {year}"

    def repl_without_weekday(match: re.Match[str]) -> str:
        day, month, year = match.groups()
        return f"{int(day)} {DUTCH_MONTHS[month]} {year}"

    text = DATE_WITH_WEEKDAY_RE.sub(repl_with_weekday, text)
    text = DATE_NO_WEEKDAY_RE.sub(repl_without_weekday, text)
    return text


def format_dutch_report_date(date_value: str) -> str:
    """Convert YYYY-MM-DD into a Dutch long report date."""
    parsed = datetime.strptime(date_value, "%Y-%m-%d")
    weekday = DUTCH_WEEKDAYS[parsed.strftime("%A")]
    month = DUTCH_MONTHS[parsed.strftime("%B")]
    return f"{weekday} {parsed.day} {month} {parsed.year}"
