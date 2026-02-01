from __future__ import annotations

from pathlib import Path

from app import LOG_FILE_NAME, process_inbox_once, setup_logging, transcribe_with_model


def test_transcribe_with_model_forces_english(tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    class FakeModel:
        def transcribe(self, audio_path: str, language: str) -> dict[str, str]:
            calls["audio_path"] = audio_path
            calls["language"] = language
            return {"text": "ok"}

    audio_path = tmp_path / "sample.mp3"
    audio_path.write_text("data", encoding="utf-8")

    result = transcribe_with_model(FakeModel(), audio_path)
    assert result == "ok"
    assert calls["audio_path"] == str(audio_path)
    assert calls["language"] == "en"


def test_no_transcript_files_written(temp_config) -> None:
    temp_config.inbox_dir.mkdir(parents=True, exist_ok=True)
    temp_config.processed_dir.mkdir(parents=True, exist_ok=True)

    mp3_file = temp_config.inbox_dir / "voice.mp3"
    mp3_file.write_text("data", encoding="utf-8")

    logger = setup_logging(temp_config.work_dir)

    def dummy_transcriber(_: Path) -> str:
        return "hello"

    def dummy_intent(_: str) -> dict[str, str]:
        return {"intent": "create-note", "content": "hello"}

    process_inbox_once(temp_config, logger, dummy_transcriber, set(), dummy_intent)

    work_files = list(temp_config.work_dir.iterdir())
    log_path = temp_config.work_dir / LOG_FILE_NAME
    assert log_path in work_files
    intent_files = [path for path in work_files if path.name.endswith("-intent.json")]
    assert len(intent_files) == 1
