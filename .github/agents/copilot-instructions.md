# foundry-local-voice2action Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-31

## Active Technologies
- Python 3.14 (uv-managed) + openai, foundry-local-sdk, agent-framework (reference), openai-whisper (001-intent-extraction)
- Local files in `.work` (intent output JSON + logs) (001-intent-extraction)

- Python >= 3.14 (uv-managed) + openai-whisper (Whisper), FFmpeg (runtime dependency) (001-voice-inbox-scan)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python >= 3.14 (uv-managed): Follow standard conventions

## Recent Changes
- 001-intent-extraction: Added Python 3.14 (uv-managed) + openai, foundry-local-sdk, agent-framework (reference), openai-whisper

- 001-voice-inbox-scan: Added Python >= 3.14 (uv-managed) + openai-whisper (Whisper), FFmpeg (runtime dependency)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
