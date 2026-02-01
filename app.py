from __future__ import annotations

import json
import logging
import os
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, NotRequired, TypedDict

import whisper
from foundry_local import FoundryLocalManager
from openai import OpenAI

VOICE_INBOX_ENV = "V2A_VOICE_INBOX"
VOICE_PROCESSED_ENV = "V2A_VOICE_PROCESSED"
SCAN_INTERVAL_ENV = "V2A_SCAN_INTERVAL"

DEFAULT_INBOX = ".voice-inbox"
DEFAULT_PROCESSED = ".voice-processed"
DEFAULT_WORK = ".work"
DEFAULT_SCAN_INTERVAL_SECONDS = 30
DEFAULT_MODEL = "base"
DEFAULT_INTENT_ALIAS = "qwen2.5-7b"
INTENT_ALIAS_ENV = "V2A_INTENT_MODEL_ALIAS"
INTENT_FILE_SUFFIX = "-intent.json"

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


class IntentPayload(TypedDict):
    intent: str
    content: str
    due: NotRequired[str]
    reminder: NotRequired[str]


def build_intent_filename(created_at: datetime) -> str:
    timestamp = created_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return f"{timestamp}{INTENT_FILE_SUFFIX}"


def write_intent_output(work_dir: Path, payload: IntentPayload) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    filename = build_intent_filename(datetime.now(timezone.utc))
    output_path = work_dir / filename
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _intent_timestamp(intent_path: Path) -> str:
    name = intent_path.name
    if name.endswith(INTENT_FILE_SUFFIX):
        return name[: -len(INTENT_FILE_SUFFIX)]
    return intent_path.stem


def build_processed_destination(
    intent_path: Path,
    original_name: str,
    processed_dir: Path,
) -> Path:
    timestamp = _intent_timestamp(intent_path)
    return processed_dir / f"{timestamp}-{original_name}"


def _intent_tool_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "emit_intent",
            "description": "Return the intent payload for the transcript.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["create-task", "create-note"],
                    },
                    "content": {
                        "type": "string",
                    },
                    "due": {
                        "type": "string",
                        "description": "ISO 8601 timestamp using Z or +00:00 for UTC. If only a date is known, time MUST be 06:00:00Z.",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|\\+00:00)$",
                    },
                    "reminder": {
                        "type": "string",
                        "description": "ISO 8601 timestamp using Z or +00:00 for UTC. If only a date is known, time MUST be 06:00:00Z.",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(Z|\\+00:00)$",
                    },
                },
                "required": ["intent", "content"],
                "additionalProperties": False,
            },
        },
    }


def _intent_messages(transcript: str) -> list[dict[str, str]]:
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    year = now.year
    tomorrow = (now.date() + timedelta(days=1)).isoformat()
    normalized = transcript.strip().lower()
    prefix_intent = (
        "create-task"
        if normalized.startswith("create a task")
        or normalized.startswith("follow up")
        or normalized.startswith("follow-up")
        or normalized.startswith("remind me")
        else "create-note"
    )
    system_prompt = (
        "You extract intent from voice transcripts. Respond ONLY by calling the tool `emit_intent`. "
        "Rules: intent must be `create-task` ONLY if the transcript starts with 'create a task', 'follow up', 'follow-up', or 'remind me'. "
        "This prefix check is case-insensitive and treats 'Follow-up' at the start as `create-task`. "
        "If the transcript starts with anything else, you MUST use `create-note`. "
        "Otherwise intent must be `create-note`. Always include `content` as the requested action or note, "
        "and include key subjects/people mentioned in the transcript (e.g., 'boss'). This is REQUIRED. "
        "Include `due` and/or `reminder` only if explicitly stated; omit them otherwise. "
        "If only a date is provided (including relative dates), you MUST set the time to 06:00 UTC "
        "(e.g., T06:00:00Z or T06:00:00+00:00), never the current time. "
        "If a due or reminder date omits the year or month, you MUST call `get_current_date` before emitting intent "
        "and assume the next occurrence of that date. Never return a year earlier than the current year. "
        "If the transcript mentions relative dates (today, tomorrow, next, this), you MUST call `get_current_date` "
        "before emitting intent and resolve to a concrete date. "
        "Tomorrow means current date + 1 day (never the current date). Today means current date. "
        "Interpret 'Latest by <date>' or 'Due by <date>' as the `due` date. "
        "Interpret 'Remind me <date>' or 'Remind me by <date>' as the `reminder` date. Do not swap these. "
        "The `reminder` field MUST be an ISO 8601 timestamp string, never a boolean. "
        "Use ISO 8601 timestamps with Z or +00:00 for UTC and DO NOT prefix timestamps with 'T'. "
        "Do NOT output date-only strings; timestamps MUST include time and timezone. "
        "Use the `get_current_date` tool response for date math; it provides a date only, not a time. "
        f"Current UTC date: {today} (year {year}). You MUST NOT output a year earlier than {year}. "
        f"If the transcript says 'tomorrow', use {tomorrow} at 06:00 UTC. "
        f"Prefix intent classification (must follow): {prefix_intent}. You MUST set intent to {prefix_intent}. "
        "Example 1: 'Follow-up with my boss.' -> intent=create-task, content includes 'boss'. "
        "Example 2: 'Remind me by tomorrow to upload files.' -> intent=create-task, reminder=<tomorrow at 06:00 UTC>."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript.strip()},
    ]


def extract_intent(transcript: str) -> IntentPayload | None:
    alias = os.getenv(INTENT_ALIAS_ENV, DEFAULT_INTENT_ALIAS)
    logging.getLogger("voice_inbox").info("Intent model alias: %s", alias)
    manager = FoundryLocalManager(alias)
    model_info = manager.get_model_info(alias)

    client = OpenAI(
        base_url=manager.endpoint,
        api_key=manager.api_key or "not-required",
    )

    input_list: list[dict[str, object]] = _intent_messages(transcript)
    tools = [_intent_tool_schema(), _current_date_tool_schema()]

    current_date_response = client.chat.completions.create(
        model=model_info.id,
        messages=input_list,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_current_date"}},
    )
    current_message = current_date_response.choices[0].message
    current_calls = current_message.tool_calls or []
    if not current_calls:
        logging.getLogger("voice_inbox").error("Intent extraction returned no tool calls.")
        return None
    input_list.append(
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in current_calls
            ],
        }
    )
    for call in current_calls:
        if call.function.name != "get_current_date":
            continue
        input_list.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(_current_date_payload()),
            }
        )

    for attempt in range(3):
        tool_choice = (
            {"type": "function", "function": {"name": "emit_intent"}}
            if attempt == 0
            else "auto"
        )
        response = client.chat.completions.create(
            model=model_info.id,
            messages=input_list,
            tools=tools,
            tool_choice=tool_choice,
        )
        message = response.choices[0].message
        tool_calls = message.tool_calls or []
        if not tool_calls:
            logging.getLogger("voice_inbox").error("Intent extraction returned no tool calls.")
            return None

        emit_call = next((call for call in tool_calls if call.function.name == "emit_intent"), None)
        if emit_call:
            arguments = emit_call.function.arguments
            try:
                payload = json.loads(arguments) if isinstance(arguments, str) else arguments
            except json.JSONDecodeError:
                logging.getLogger("voice_inbox").error("Intent extraction returned invalid JSON arguments.")
                return None
            if not isinstance(payload, dict):
                logging.getLogger("voice_inbox").error("Intent extraction returned non-object arguments.")
                return None
            return payload  # type: ignore[return-value]

        if any(call.function.name == "get_current_date" for call in tool_calls):
            input_list.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in tool_calls
                    ],
                }
            )
            for call in tool_calls:
                if call.function.name != "get_current_date":
                    continue
                input_list.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(_current_date_payload()),
                    }
                )
            continue

        logging.getLogger("voice_inbox").error("Intent extraction returned unsupported tool call.")
        return None

    logging.getLogger("voice_inbox").error("Intent extraction exceeded tool-call retries.")
    return None

def _current_date_tool_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get the current UTC date (no time) to resolve relative dates.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    }

def _current_date_payload() -> dict[str, str]:
    now = datetime.now(timezone.utc)
    return {
        "date": now.date().isoformat(),
    }


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
    intent_func: Callable[[str], IntentPayload | None] = extract_intent,
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
        intent_payload = intent_func(transcript)
        if intent_payload is None:
            logger.error("Intent extraction failed for %s", audio_path.name)
            continue
        try:
            intent_path = write_intent_output(config.work_dir, intent_payload)
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Failed to write intent output for %s: %s", audio_path.name, exc)
            continue
        logger.info("Intent output written to %s", intent_path)
        destination = build_processed_destination(
            intent_path,
            audio_path.name,
            config.processed_dir,
        )
        if destination.exists():
            logger.error("Processed destination already exists: %s", destination)
            continue
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
