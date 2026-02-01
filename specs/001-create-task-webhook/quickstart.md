# Quickstart: Create-task webhook

## Prerequisites

- Python >= 3.14 with uv
- Foundry Local installed and running (for end-to-end app runs)

## Configure

- `V2A_CREATE_TODO_WEBHOOK_URL`: Webhook URL that receives JSON payloads with `title`, optional `due`, optional `reminder`.
- Existing voice inbox env vars remain supported (see main README).

## Run tests

- From repo root: `uv run pytest`

## Manual verification (invocation-only)

Because end-to-end runs invoke Foundry Local for intent extraction, manual verification is required for full pipeline checks.

- Start a local webhook receiver (or test endpoint).
- Set `V2A_CREATE_TODO_WEBHOOK_URL` to that endpoint.
- Run: `uv run app.py`
- Drop MP3 files into the inbox and confirm the webhook receives:
  - `title` matching the intent `content`
  - Optional `due` and `reminder` when present

### Manual Verification Log (2026-02-01)

Command:

`uv run app.py`

Observed:

- Voice inbox scanner started and processed sample MP3s.
- Webhook receiver captured POST payloads:
  - `title` = "upload the Performance Review Files", `reminder` = "2026-02-02T06:00:00+00:00"
  - `title` = "Follow-up with my boss. We should talk about our AI strategy.", `due` = "2026-08-30T06:00:00Z", `reminder` = "2026-08-20T06:00:00Z"
