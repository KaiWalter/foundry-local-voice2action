from __future__ import annotations

from pathlib import Path

from app import process_inbox_once


def test_move_to_processed_on_success(temp_config, test_logger) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)

    mp3_file = temp_config.inbox_dir / "voice.mp3"
    mp3_file.write_text("data", encoding="utf-8")

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    process_inbox_once(temp_config, test_logger, dummy_transcriber, set())

    assert not mp3_file.exists()
    assert (temp_config.processed_dir / "voice.mp3").exists()
