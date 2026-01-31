from __future__ import annotations

from pathlib import Path

from app import LOG_FILE_NAME, setup_logging


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    logger = setup_logging(tmp_path)
    logger.info("log entry")

    log_file = tmp_path / LOG_FILE_NAME
    assert log_file.exists()
    assert "log entry" in log_file.read_text(encoding="utf-8")
