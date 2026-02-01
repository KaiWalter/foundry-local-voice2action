from __future__ import annotations

import json
import re
from pathlib import Path

from app import _intent_messages, write_intent_output


def test_write_intent_output_file(tmp_path: Path) -> None:
    payload = {
        "intent": "create-task",
        "content": "Follow up with Alex about the Q1 report",
    }

    output_path = write_intent_output(tmp_path, payload)

    assert output_path.exists()
    assert re.fullmatch(r"\d{8}T\d{6}-intent\.json", output_path.name)
    stored = json.loads(output_path.read_text(encoding="utf-8"))
    assert stored == payload


def test_prompt_includes_due_reminder_rules() -> None:
    messages = _intent_messages("remind me tomorrow")
    system = messages[0]["content"]
    assert "Latest by" in system
    assert "Remind me" in system
    assert "06:00" in system


def test_prompt_includes_fallback_to_create_note() -> None:
    messages = _intent_messages("random note")
    system = messages[0]["content"]
    assert "Otherwise intent must be `create-note`" in system
