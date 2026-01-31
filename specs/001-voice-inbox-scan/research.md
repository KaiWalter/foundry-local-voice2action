# Research Findings: Voice Inbox Transcription

## Decision 1: Use polling scan with 30s interval

- **Decision**: Implement periodic polling based on `V2A_SCAN_INTERVAL` (default 30s).
- **Rationale**: Polling is the most portable approach across local and network filesystems and aligns with spec requirements. Event-based watchers are lower latency but less reliable across shares and require more dependencies.
- **Alternatives considered**: File system event watchers (e.g., watchdog) with periodic rescan; rejected due to added dependency and cross-platform edge cases.

## Decision 2: Locked/in-progress files treated as failed

- **Decision**: If a file cannot be opened (locked or still written), log an error and leave it in the inbox.
- **Rationale**: Spec explicitly requires treating locked files as failed. This ensures the operator sees the issue and can resolve producer behavior.
- **Alternatives considered**: Skip and retry on the next scan, or use size/mtime stability windows; rejected because the spec mandates error behavior.

## Decision 3: Avoid reprocessing by moving to processed folder

- **Decision**: After successful transcription, move the file to the processed folder.
- **Rationale**: Moving the file provides a clear, durable signal that it has been processed and aligns with user story expectations.
- **Alternatives considered**: Tracking hashes or a state file; rejected to keep the demo minimal and aligned with spec.

## Decision 4: Whisper model usage

- **Decision**: Load Whisper model once per run and reuse for all files; force language to English.
- **Rationale**: Model loading is expensive; reuse improves throughput. Explicit language avoids detection overhead and ensures consistent output as required.
- **Alternatives considered**: Per-file model loading; rejected due to performance costs.

## Decision 5: Logging to console + file

- **Decision**: Log all events to console and to a log file in the work folder.
- **Rationale**: The spec requires both; a file log aids troubleshooting while console output keeps CLI visibility.
- **Alternatives considered**: Console-only or file-only logging; rejected due to explicit requirement.

## Decision 6: Non-MP3 handling

- **Decision**: Ignore non-MP3 files but log a warning once per file.
- **Rationale**: This meets the spec requirement while keeping processing focused on supported input.
- **Alternatives considered**: Treat as errors or ignore silently; rejected by clarification.
