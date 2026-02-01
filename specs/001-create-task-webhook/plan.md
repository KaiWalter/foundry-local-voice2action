# Implementation Plan: Create-task webhook

**Branch**: `001-create-task-webhook` | **Date**: 2026-02-01 | **Spec**: [specs/001-create-task-webhook/spec.md](specs/001-create-task-webhook/spec.md)
**Input**: Feature specification from `/specs/001-create-task-webhook/spec.md`

## Summary

Add a webhook dispatch step for `create-task` intents so the app POSTs a JSON payload (`title`, optional `due`, optional `reminder`) to the URL in `V2A_CREATE_TODO_WEBHOOK_URL`. Use Python stdlib `urllib.request` for delivery, treat any 2xx as success, log errors (including request/response payloads on 400), and still move files. Provide pytest coverage with a stdlib HTTP server mock verifying the two specified payload cases and request headers.

## Technical Context

**Language/Version**: Python >= 3.14 (uv-managed)  
**Primary Dependencies**: openai, foundry-local-sdk, openai-whisper (existing); stdlib `urllib.request` for webhook calls  
**Storage**: Local filesystem (`.voice-inbox`, `.voice-processed`, `.work`)  
**Testing**: pytest with stdlib HTTP server mock  
**Target Platform**: Local developer machines (Windows/macOS/Linux)  
**Project Type**: Single-script CLI in repository root  
**Performance Goals**: Webhook call completes within a short timeout (target 10s) per intent  
**Constraints**: Offline-first; no retries; no auth header; log errors and continue processing  
**Scale/Scope**: Single-user demo; small batches of MP3 files per scan

## Constitution Check

- **Testable Application Logic**: Webhook payload mapping, request formatting, and error handling are covered by pytest with a local HTTP server mock.
- **Invocation Stewardship**: End-to-end runs still invoke Foundry Local for intent extraction, so full pipeline checks remain manual; webhook logic itself is fully testable without invoking the model.
- **Python + uv First Flow**: Execution via `uv run app.py`; tests via `uv run pytest`.
- **Reference Implementations**: sample-transcribe.py remains the Whisper reference for transcription behavior.

Constitution check (pre-design):

- Testable logic: webhook payload mapping and delivery error handling covered by pytest with a local HTTP server.
- Invocation stewardship: Foundry Local intent extraction remains manual for end-to-end verification.
- Python + uv flow: `uv run app.py` and `uv run pytest`.
- Reference: sample-transcribe.py.

## Project Structure

### Documentation (this feature)

```text
specs/001-create-task-webhook/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
app.py
specs/
tests/
```

**Structure Decision**: Single-script CLI at repo root with tests under `tests/`.

Constitution check (post-design):

- Testable logic: Webhook payload mapping, status handling, and error paths covered by pytest with a local HTTP server.
- Invocation stewardship: Foundry Local remains a manual verification step for full pipeline checks.
- Python + uv flow: `uv run app.py` and `uv run pytest`.
- Reference: sample-transcribe.py remains the transcription anchor.
