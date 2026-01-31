from __future__ import annotations

import logging
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import whisper

VOICE_INBOX_ENV = "V2A_VOICE_INBOX"
VOICE_PROCESSED_ENV = "V2A_VOICE_PROCESSED"
SCAN_INTERVAL_ENV = "V2A_SCAN_INTERVAL"

DEFAULT_INBOX = ".voice-inbox"
DEFAULT_PROCESSED = ".voice-processed"
DEFAULT_WORK = ".work"
DEFAULT_SCAN_INTERVAL_SECONDS = 30
DEFAULT_MODEL = "base"

LOG_FILE_NAME = "voice-inbox.log"


@dataclass(frozen=True)
class AppConfig:
    inbox_dir: Path
    processed_dir: Path
    work_dir: Path
    scan_interval_seconds: int


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _resolve_path(value: str | None, default_name: str, root: Path) -> Path:
    if not value:
        return root / default_name
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return root / candidate


def _parse_scan_interval(value: str | None) -> int:
    if value is None or value.strip() == "":
        return DEFAULT_SCAN_INTERVAL_SECONDS
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{SCAN_INTERVAL_ENV} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"{SCAN_INTERVAL_ENV} must be greater than zero")
    return parsed


def load_config(root: Path | None = None, environ: dict[str, str] | None = None) -> AppConfig:
    root = root or _project_root()
    environ = environ or os.environ
    inbox_dir = _resolve_path(environ.get(VOICE_INBOX_ENV), DEFAULT_INBOX, root)
    processed_dir = _resolve_path(environ.get(VOICE_PROCESSED_ENV), DEFAULT_PROCESSED, root)
    work_dir = _resolve_path(DEFAULT_WORK, DEFAULT_WORK, root)
    scan_interval = _parse_scan_interval(environ.get(SCAN_INTERVAL_ENV))
    return AppConfig(
        inbox_dir=inbox_dir,
        processed_dir=processed_dir,
        work_dir=work_dir,
        scan_interval_seconds=scan_interval,
    )


def ensure_directories(config: AppConfig) -> None:
    config.inbox_dir.mkdir(parents=True, exist_ok=True)
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    config.work_dir.mkdir(parents=True, exist_ok=True)


def setup_logging(work_dir: Path) -> logging.Logger:
    work_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("voice_inbox")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    log_file = work_dir / LOG_FILE_NAME
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def _ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg"):
        return
    raise FileNotFoundError(
        "ffmpeg executable not found. Install ffmpeg and ensure it is on PATH before running transcription."
    )


class WhisperTranscriber:
    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        _ensure_ffmpeg()
        self._model = whisper.load_model(model_name)

    def transcribe(self, audio_path: Path) -> str:
        return transcribe_with_model(self._model, audio_path)


def transcribe_with_model(model: object, audio_path: Path) -> str:
    result = model.transcribe(str(audio_path), language="en")
    return str(result["text"])


def list_inbox_files(inbox_dir: Path) -> list[Path]:
    if not inbox_dir.exists():
        return []
    return sorted([path for path in inbox_dir.iterdir() if path.is_file()])


def _is_mp3(path: Path) -> bool:
    return path.suffix.lower() == ".mp3"


def _is_readable(path: Path) -> bool:
    try:
        with path.open("rb"):
            return True
    except OSError:
        return False


def process_inbox_once(
    config: AppConfig,
    logger: logging.Logger,
    transcribe_func: Callable[[Path], str],
    warned_non_mp3: set[Path],
) -> None:
    for audio_path in list_inbox_files(config.inbox_dir):
        if not _is_mp3(audio_path):
            if audio_path not in warned_non_mp3:
                logger.warning("Ignoring non-MP3 file: %s", audio_path.name)
                warned_non_mp3.add(audio_path)
            continue
        if not _is_readable(audio_path):
            logger.error("File is locked or unreadable: %s", audio_path.name)
            continue
        try:
            transcript = transcribe_func(audio_path)
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Transcription failed for %s: %s", audio_path.name, exc)
            continue
        logger.info("Transcript for %s: %s", audio_path.name, transcript.strip())
        destination = config.processed_dir / audio_path.name
        try:
            shutil.move(str(audio_path), str(destination))
            logger.info("Moved processed file to %s", destination)
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Failed to move %s to processed folder: %s", audio_path.name, exc)


def main() -> None:
    config = load_config()
    ensure_directories(config)
    logger = setup_logging(config.work_dir)
    logger.info("Voice inbox scanner started. Inbox: %s", config.inbox_dir)
    transcriber = WhisperTranscriber()
    warned_non_mp3: set[Path] = set()

    while True:
        process_inbox_once(config, logger, transcriber.transcribe, warned_non_mp3)
        time.sleep(config.scan_interval_seconds)


if __name__ == "__main__":
    main()
