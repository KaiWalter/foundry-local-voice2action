import os
import shutil
from pathlib import Path

import whisper


def _ensure_audio_exists(audio_file_path: str) -> None:
    if not Path(audio_file_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")


def _ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg"):
        return
    raise FileNotFoundError(
        "ffmpeg executable not found. Install ffmpeg and ensure it is on PATH before running transcription."
    )


def transcribe_audio_file(audio_file_path: str, model: str = "base") -> str:
    """
    Transcribe an audio file to text using Whisper.
    
    Args:
        audio_file_path: Path to audio file (mp3, wav, m4a, flac, opus, vorbis)
        model: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        Transcribed text
    """
    _ensure_audio_exists(audio_file_path)
    _ensure_ffmpeg()
    print(f"📁 Loading model: {model}")
    model_obj = whisper.load_model(model)
    
    print(f"🎙️ Transcribing: {audio_file_path}")
    result = model_obj.transcribe(audio_file_path, language="en")
    
    transcribed_text = result["text"]
    print(f"✅ Transcription complete:\n{transcribed_text}")
    
    return transcribed_text

# Usage
if __name__ == "__main__":
    # Example: transcribe a recording
    project_root = Path(__file__).resolve().parent
    sample_path = project_root / "audio_samples" / "sample-recording-1-task-with-due-date-and-reminder.mp3"
    text = transcribe_audio_file(str(sample_path), model="base")
    print(f"Extracted text: {text}")
