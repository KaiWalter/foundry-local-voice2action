from __future__ import annotations

from datetime import datetime, timezone

from app import build_intent_filename


def test_build_intent_filename_format() -> None:
    created_at = datetime(2026, 2, 1, 6, 0, 0, tzinfo=timezone.utc)
    assert build_intent_filename(created_at) == "20260201T060000-intent.json"
