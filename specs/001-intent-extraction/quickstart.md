# Quickstart: Intent Extraction Output

## Prerequisites

- Python >= 3.14 with uv
- Foundry Local installed and running
- FFmpeg installed and on PATH (required by Whisper)

## Configure

- `V2A_VOICE_INBOX` (default: `.voice-inbox`)
- `V2A_VOICE_PROCESSED` (default: `.voice-processed`)
- `V2A_SCAN_INTERVAL` (default: `30` seconds)

## Run

- From repo root: `uv run app.py`

## Observe

- Drop MP3 files into the inbox folder.
- Watch console output for transcript results and intent output creation.
- Inspect `.work` for `yyyyMMddThhmmss-intent.json` files and the log file.

## Manual Verification Notes

- Foundry Local model invocation for intent extraction is a manual verification item per the constitution.
- Manual verification (T020, 2026-02-01): Run `uv run app.py`, drop sample MP3s, and confirm transcripts are logged, intent output files are created in `.work` with `yyyyMMddThhmmss-intent.json` naming, and processed audio files move to `.voice-processed`.

### Manual Verification Log (T015)

Command:

`uv run .\app.py`

Observed (timestamps removed, user name obfuscated):

- Voice inbox scanner started. Inbox: C:\Users\<user>\src\foundry-local-voice2action\.voice-inbox
- Transcript for sample-recording-1-task-with-due-date-and-reminder.mp3: Follow-up with my boss. Latest by August 30th. Remind me August 20th. We should talk about our AI strategy.
- Intent model alias: qwen2.5-7b
- Intent output written to C:\Users\<user>\src\foundry-local-voice2action\.work\20260201T101321-intent.json
- Moved processed file to C:\Users\<user>\src\foundry-local-voice2action\.voice-processed\sample-recording-1-task-with-due-date-and-reminder.mp3
- Transcript for sample-recording-4-remind-by-tomorrow.mp3: Remind me by tomorrow to upload the Performance Review Files.
- Intent model alias: qwen2.5-7b
- Intent output written to C:\Users\<user>\src\foundry-local-voice2action\.work\20260201T101341-intent.json
- Moved processed file to C:\Users\<user>\src\foundry-local-voice2action\.voice-processed\sample-recording-4-remind-by-tomorrow.mp3

Manual verification artifacts (content only):

- 20260201T101321-intent.json
  - intent: "create-task"
  - content: "Follow-up with my boss. We should talk about our AI strategy."
  - due: "2026-08-30T06:00:00Z"
  - reminder: "2026-08-20T06:00:00Z"
- 20260201T101341-intent.json
  - intent: "create-task"
  - content: "upload the Performance Review Files"
  - reminder: "2026-02-02T06:00:00+00:00"

### Test Run Log (T016)

Command:

`uv run pytest`

Result:

- All tests passed.
