from __future__ import annotations

from app import ensure_directories


def test_ensure_directories_creates_all(temp_config) -> None:
    ensure_directories(temp_config)

    assert temp_config.inbox_dir.exists()
    assert temp_config.processed_dir.exists()
    assert temp_config.work_dir.exists()
