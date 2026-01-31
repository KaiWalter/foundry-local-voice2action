# Quickstart: Voice Inbox Transcription

## Prerequisites

- Python >= 3.14 with uv
- FFmpeg installed and on PATH (required by Whisper)

## Configure

- `V2A_VOICE_INBOX` (default: `.voice-inbox`)
- `V2A_VOICE_PROCESSED` (default: `.voice-processed`)
- `V2A_SCAN_INTERVAL` (default: `30` seconds)

## Run

- From repo root: `uv run app.py`

## Observe

- Drop MP3 files into the inbox folder.
- Watch console output for transcript results and warnings.
- Check `.work` for the log file.

## Manual Verification Notes

- Whisper model download/usage and FFmpeg availability are manual verification items per the constitution.
