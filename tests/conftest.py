from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import AppConfig


@pytest.fixture
def temp_config(tmp_path: Path) -> AppConfig:
    inbox_dir = tmp_path / "inbox"
    processed_dir = tmp_path / "processed"
    work_dir = tmp_path / ".work"
    return AppConfig(
        inbox_dir=inbox_dir,
        processed_dir=processed_dir,
        work_dir=work_dir,
        scan_interval_seconds=30,
    )


@pytest.fixture
def test_logger() -> logging.Logger:
    logger = logging.getLogger("test_voice_inbox")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.NullHandler())
    logger.propagate = True
    return logger
