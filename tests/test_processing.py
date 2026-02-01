from __future__ import annotations

import json
import logging
from pathlib import Path

import app
from app import INTENT_FILE_SUFFIX, process_inbox_once


def _intent_timestamp_from_work_dir(work_dir: Path) -> str:
    intent_files = list(work_dir.glob(f"*{INTENT_FILE_SUFFIX}"))
    assert len(intent_files) == 1
    filename = intent_files[0].name
    return filename[: -len(INTENT_FILE_SUFFIX)]


def test_move_to_processed_on_success(temp_config, test_logger) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)

    mp3_file = temp_config.inbox_dir / "voice.mp3"
    mp3_file.write_text("data", encoding="utf-8")

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    process_inbox_once(temp_config, test_logger, dummy_transcriber, set(), dummy_intent)

    timestamp = _intent_timestamp_from_work_dir(temp_config.work_dir)
    expected_path = temp_config.processed_dir / f"{timestamp}-voice.mp3"

    assert not mp3_file.exists()
    assert expected_path.exists()


def test_move_skips_when_destination_exists(
    temp_config, test_logger, monkeypatch, caplog
) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)
    temp_config.work_dir.mkdir(parents=True, exist_ok=True)

    mp3_file = temp_config.inbox_dir / "voice.mp3"
    mp3_file.write_text("data", encoding="utf-8")

    fixed_timestamp = "20260201T010203"
    intent_path = temp_config.work_dir / f"{fixed_timestamp}{INTENT_FILE_SUFFIX}"

    def fake_write_intent_output(work_dir: Path, payload: dict[str, str]) -> Path:
        work_dir.mkdir(parents=True, exist_ok=True)
        intent_path.write_text(json.dumps(payload), encoding="utf-8")
        return intent_path

    monkeypatch.setattr(app, "write_intent_output", fake_write_intent_output)

    existing_destination = temp_config.processed_dir / f"{fixed_timestamp}-voice.mp3"
    existing_destination.write_text("existing", encoding="utf-8")

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    caplog.set_level(logging.ERROR)
    process_inbox_once(temp_config, test_logger, dummy_transcriber, set(), dummy_intent)

    assert mp3_file.exists()
    assert existing_destination.exists()
    assert any(
        "Processed destination already exists" in record.message
        for record in caplog.records
    )


def test_move_skips_when_intent_write_fails(
    temp_config, test_logger, monkeypatch, caplog
) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)

    mp3_file = temp_config.inbox_dir / "voice.mp3"
    mp3_file.write_text("data", encoding="utf-8")

    def failing_write(_: Path, __: dict[str, str]) -> Path:
        raise RuntimeError("boom")

    monkeypatch.setattr(app, "write_intent_output", failing_write)

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    caplog.set_level(logging.ERROR)
    process_inbox_once(temp_config, test_logger, dummy_transcriber, set(), dummy_intent)

    assert mp3_file.exists()
    assert list(temp_config.processed_dir.iterdir()) == []
    assert any(
        "Failed to write intent output" in record.message for record in caplog.records
    )


def test_multi_file_processing_uses_matching_timestamps(
    temp_config, test_logger, monkeypatch
) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)
    temp_config.work_dir.mkdir(parents=True, exist_ok=True)

    first_mp3 = temp_config.inbox_dir / "voice-one.mp3"
    second_mp3 = temp_config.inbox_dir / "voice-two.mp3"
    first_mp3.write_text("data", encoding="utf-8")
    second_mp3.write_text("data", encoding="utf-8")

    timestamps = iter(["20260201T101010", "20260201T101011"])

    def fake_write_intent_output(work_dir: Path, payload: dict[str, str]) -> Path:
        work_dir.mkdir(parents=True, exist_ok=True)
        timestamp = next(timestamps)
        intent_path = work_dir / f"{timestamp}{INTENT_FILE_SUFFIX}"
        intent_path.write_text(json.dumps(payload), encoding="utf-8")
        return intent_path

    monkeypatch.setattr(app, "write_intent_output", fake_write_intent_output)

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    process_inbox_once(temp_config, test_logger, dummy_transcriber, set(), dummy_intent)

    expected_first = temp_config.processed_dir / "20260201T101010-voice-one.mp3"
    expected_second = temp_config.processed_dir / "20260201T101011-voice-two.mp3"

    assert not first_mp3.exists()
    assert not second_mp3.exists()
    assert expected_first.exists()
    assert expected_second.exists()
