# Feature Specification: Voice Inbox Transcription

**Feature Branch**: `001-voice-inbox-scan`  
**Created**: 2026-01-31  
**Status**: Draft  
**Input**: User description: "Build app.py to periodically scan a folder for mp3 voice recordings, transcribe to English text, print results, and move processed files; use configurable inbox/processed folders with defaults and ensure folders are ignored by Git."

## Clarifications

### Session 2026-01-31

- Q: What scan interval should the periodic scanner use? → A: 30 seconds, configurable via environment variable V2A_SCAN_INTERVAL.
- Q: Should transcripts be written to disk? → A: Console output only; do not write transcript files by default.
- Q: How should the app behave when an MP3 file is still being written or locked? → A: Fail the file and log an error.
- Q: Should non-MP3 files be ignored or logged as errors? → A: Ignore them but log a warning once per file.
- Q: Where should log output go? → A: Console output plus a log file in the work folder.

## User Scenarios & Testing *(mandatory)*

> NOTE: Per the constitution’s Testable Application Logic principle, each story must call out how its logic is covered by automated tests. When a story describes an invocation-only flow, mark it as manual verification with an explicit explanation of why automation is not feasible.

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - See transcriptions from new recordings (Priority: P1)

As a user running the voice-to-action demo, I want new voice recordings dropped into the inbox to be detected and transcribed so I can immediately see the text output.

**Why this priority**: This is the core value of the demo—turning audio into usable text without manual steps.

**Independent Test**: Automated tests can validate inbox scanning, file discovery, and transcript output handling with mocked transcription results.

**Acceptance Scenarios**:

1. **Given** the inbox folder contains an unprocessed MP3 recording, **When** the scanner runs, **Then** the transcript for that file is written to the console output.
2. **Given** multiple new MP3 recordings appear in the inbox, **When** the scanner runs, **Then** each file is transcribed once and each transcript is printed.

---

### User Story 2 - Processed recordings are archived (Priority: P2)

As a user, I want recordings that were successfully transcribed to be moved out of the inbox so I can keep the inbox clean and avoid reprocessing.

**Why this priority**: Prevents duplicate processing and keeps workflows orderly.

**Independent Test**: Automated tests can validate file moves after a successful transcription result without invoking real transcription.

**Acceptance Scenarios**:

1. **Given** an MP3 recording is successfully transcribed, **When** processing completes, **Then** the original file is moved to the processed folder and no longer remains in the inbox.

---

### User Story 3 - Folders are created and ignored by Git (Priority: P3)

As a user, I want required runtime folders to be created automatically and excluded from version control so the repo stays clean.

**Why this priority**: Avoids setup friction and prevents accidental commits of runtime artifacts.

**Independent Test**: Automated tests can validate folder creation and Git ignore configuration without invoking external services.

**Acceptance Scenarios**:

1. **Given** the inbox and processed folders do not exist, **When** the app starts, **Then** the folders are created and are excluded from Git tracking.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Non-MP3 files appear in the inbox.
- Non-MP3 files appear in the inbox and should be ignored with a warning.
- An MP3 file is locked or still being written when detected (should be treated as a failed file and logged).
- Transcription fails for a specific file while other files succeed.
- The processed folder is missing or unavailable at runtime.

## Requirements *(mandatory)*

> NOTE: State for every requirement whether it is satisfied by automated tests or serves a manual invocation step, referencing the constitution’s Invocation Stewardship note when tests cannot cover the behavior.

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The system MUST periodically scan a configured inbox folder for new MP3 recordings. (Test: Automated)
- **FR-002**: The system MUST treat English as the assumed language for transcription. (Test: Automated)
- **FR-003**: The system MUST output the transcription text to the console for each successfully processed file. (Test: Automated)
- **FR-004**: The system MUST move each successfully processed MP3 recording to a configured processed folder. (Test: Automated)
- **FR-005**: The system MUST create the inbox, processed, and optional work folders at startup if they do not exist. (Test: Automated)
- **FR-006**: The system MUST allow configuring inbox and processed folder locations via environment variables, with documented defaults. (Test: Automated)
- **FR-010**: The system MUST allow configuring the scan interval via environment variable V2A_SCAN_INTERVAL, with a default of 30 seconds. (Test: Automated)
- **FR-007**: The system MUST keep runtime folders out of version control by default. (Test: Automated)
- **FR-008**: If transcription fails for a file, the system MUST leave the original file in the inbox and surface a clear console error for that file. (Test: Automated)
- **FR-009**: Running a full transcription pass against real audio files MUST be validated via manual verification because it depends on external runtime models. (Test: Manual)
- **FR-011**: The system MUST NOT write transcript files to disk by default. (Test: Automated)
- **FR-012**: If an MP3 file cannot be opened due to being locked or still written, the system MUST treat it as a failed transcription and log a clear error. (Test: Automated)
- **FR-013**: The system MUST ignore non-MP3 files while logging a warning per file. (Test: Automated)
- **FR-014**: The system MUST write logs to console output and also to a log file in the work folder. (Test: Automated)

### Key Entities *(include if feature involves data)*

- **Voice Recording**: An MP3 audio file discovered in the inbox, with attributes such as filename, size, and discovery time.
- **Transcript**: The text output generated from a voice recording, linked to the original filename and processing time.
- **Inbox Configuration**: The configured inbox and processed folder locations and their defaults.
- **Processing Result**: The outcome of an attempted transcription (success or failure) with any error details.

## Assumptions

- The inbox and processed folder locations are scoped to a subfolder of the project directory by default.
- A periodic scan interval (default 30 seconds) is used rather than real-time filesystem notifications.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: New MP3 files are detected and processed within 30 seconds of being placed in the inbox during normal operation.
- **SC-002**: 100% of successfully transcribed files are moved out of the inbox on the same scan cycle.
- **SC-003**: At least 90% of manual test runs with valid English recordings produce readable transcripts on first attempt.
- **SC-004**: No runtime inbox, work, or processed files appear as Git-tracked changes after running the app.
