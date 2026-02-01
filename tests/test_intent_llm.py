from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import os
import re

import pytest

from app import extract_intent


TRANSCRIPT = (
    "Follow-up with my boss. Latest by August 30th. "
    "Remind me August 20th. We should talk about our AI strategy."
)

REMIND_BY_TOMORROW = "Remind me by tomorrow to upload the performance review files."


def _next_occurrence_year(today: date, month: int, day: int) -> int:
    candidate = date(today.year, month, day)
    return today.year if candidate >= today else today.year + 1


def _parse_iso_date(value: str) -> date:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})T", value)
    if not match:
        raise AssertionError(f"Invalid ISO date prefix: {value}")
    year, month, day = map(int, match.groups())
    return date(year, month, day)


def _assert_time_is_six_utc(value: str) -> None:
    assert value.startswith("06:00:00"), f"Expected 06:00:00 UTC time, got {value}"
    assert value.endswith("Z") or value.endswith("+00:00"), f"Expected UTC offset, got {value}"


@pytest.mark.llm
def test_intent_extraction_follow_up_with_due_and_reminder() -> None:
    if os.getenv("V2A_RUN_LLM_TESTS") != "1":
        pytest.skip("Set V2A_RUN_LLM_TESTS=1 to run LLM-backed tests.")

    payload = extract_intent(TRANSCRIPT)
    assert payload is not None

    assert payload.get("intent") == "create-task"
    assert "boss" in payload.get("content", "").lower()

    due = payload.get("due")
    reminder = payload.get("reminder")
    assert isinstance(due, str)
    assert isinstance(reminder, str)

    today = datetime.now(timezone.utc).date()
    expected_due_year = _next_occurrence_year(today, 8, 30)
    expected_reminder_year = _next_occurrence_year(today, 8, 20)

    due_date = _parse_iso_date(due)
    reminder_date = _parse_iso_date(reminder)

    assert due_date == date(expected_due_year, 8, 30)
    assert reminder_date == date(expected_reminder_year, 8, 20)

    _assert_time_is_six_utc(due.split("T", 1)[1])
    _assert_time_is_six_utc(reminder.split("T", 1)[1])


@pytest.mark.llm
def test_intent_extraction_remind_by_tomorrow() -> None:
    if os.getenv("V2A_RUN_LLM_TESTS") != "1":
        pytest.skip("Set V2A_RUN_LLM_TESTS=1 to run LLM-backed tests.")

    payload = extract_intent(REMIND_BY_TOMORROW)
    assert payload is not None
    assert payload.get("intent") == "create-task"
    assert "performance review" in payload.get("content", "").lower()

    reminder = payload.get("reminder")
    assert isinstance(reminder, str)

    today = datetime.now(timezone.utc).date()
    expected = today + timedelta(days=1)
    reminder_date = _parse_iso_date(reminder)
    assert reminder_date == expected
    _assert_time_is_six_utc(reminder.split("T", 1)[1])
