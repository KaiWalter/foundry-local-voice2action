# Data Model: Voice Inbox Transcription

## Entities

### VoiceRecording

- **Represents**: A discovered MP3 file in the inbox.
- **Fields**:
  - `path` (string): Absolute path to the file.
  - `filename` (string): Base name of the file.
  - `size_bytes` (integer): Size at discovery time.
  - `discovered_at` (datetime): When the file was first seen.
  - `status` (enum): `pending`, `processing`, `processed`, `failed`.

### Transcript

- **Represents**: Text output for a processed recording.
- **Fields**:
  - `recording_path` (string): Link back to `VoiceRecording`.
  - `text` (string): Transcribed content.
  - `transcribed_at` (datetime): Completion timestamp.

### ProcessingResult

- **Represents**: Outcome of a transcription attempt.
- **Fields**:
  - `recording_path` (string): Link back to `VoiceRecording`.
  - `status` (enum): `success`, `error`.
  - `error_message` (string, optional): Error detail if failed.

### InboxConfiguration

- **Represents**: Runtime configuration for folders and timing.
- **Fields**:
  - `inbox_dir` (string): From `V2A_VOICE_INBOX` (default `.voice-inbox`).
  - `processed_dir` (string): From `V2A_VOICE_PROCESSED` (default `.voice-processed`).
  - `work_dir` (string): `.work` (for logs; created if needed).
  - `scan_interval_seconds` (integer): From `V2A_SCAN_INTERVAL` (default 30).

## Relationships

- `VoiceRecording` 1→1 `Transcript` (only when processed successfully)
- `VoiceRecording` 1→1 `ProcessingResult`

## Validation Rules

- Only files with `.mp3` extension are eligible for transcription.
- `scan_interval_seconds` must be a positive integer.
- Locked/unreadable files are treated as failed and logged.

## State Transitions

```text
[pending] -> [processing] -> [processed]
[pending] -> [processing] -> [failed]
```
