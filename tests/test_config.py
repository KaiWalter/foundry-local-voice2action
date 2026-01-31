from __future__ import annotations

from pathlib import Path

import pytest

from app import (
    DEFAULT_INBOX,
    DEFAULT_PROCESSED,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    VOICE_INBOX_ENV,
    VOICE_PROCESSED_ENV,
    SCAN_INTERVAL_ENV,
    load_config,
)


def test_load_config_defaults(tmp_path: Path) -> None:
    config = load_config(root=tmp_path, environ={})
    assert config.inbox_dir == tmp_path / DEFAULT_INBOX
    assert config.processed_dir == tmp_path / DEFAULT_PROCESSED
    assert config.scan_interval_seconds == DEFAULT_SCAN_INTERVAL_SECONDS


def test_load_config_env_overrides(tmp_path: Path) -> None:
    env = {
        VOICE_INBOX_ENV: "custom-inbox",
        VOICE_PROCESSED_ENV: "custom-processed",
        SCAN_INTERVAL_ENV: "45",
    }
    config = load_config(root=tmp_path, environ=env)
    assert config.inbox_dir == tmp_path / "custom-inbox"
    assert config.processed_dir == tmp_path / "custom-processed"
    assert config.scan_interval_seconds == 45


@pytest.mark.parametrize("value", ["0", "-1", "not-a-number"])
def test_load_config_invalid_scan_interval(tmp_path: Path, value: str) -> None:
    env = {SCAN_INTERVAL_ENV: value}
    with pytest.raises(ValueError):
        load_config(root=tmp_path, environ=env)
