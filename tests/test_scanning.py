from __future__ import annotations

from pathlib import Path

from app import process_inbox_once


def _write_file(path: Path, content: str = "data") -> None:
    path.write_text(content, encoding="utf-8")


def test_non_mp3_warning_once(temp_config, test_logger, caplog) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)

    txt_file = temp_config.inbox_dir / "note.txt"
    mp3_file = temp_config.inbox_dir / "voice.mp3"
    _write_file(txt_file)
    _write_file(mp3_file)

    warned: set[Path] = set()

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    caplog.set_level("WARNING")
    process_inbox_once(temp_config, test_logger, dummy_transcriber, warned, dummy_intent)
    warnings_first = [rec for rec in caplog.records if rec.levelname == "WARNING"]
    assert len(warnings_first) == 1

    caplog.clear()
    process_inbox_once(temp_config, test_logger, dummy_transcriber, warned, dummy_intent)
    warnings_second = [rec for rec in caplog.records if rec.levelname == "WARNING"]
    assert len(warnings_second) == 0
