# Feature Specification: Timestamp processed audio

**Feature Branch**: `001-timestamp-processed-audio`  
**Created**: 2026-02-01  
**Status**: Draft  
**Input**: User description: "when moving the processed voice recording to the processed folder, prefix it with the same timestamp as the intent.json file put into the work folder"

## Clarifications

### Session 2026-02-01

- Q: What delimiter should separate the timestamp and original filename? → A: Use a hyphen (timestamp-original-filename).

## User Scenarios & Testing *(mandatory)*

> NOTE: Per the constitution’s Testable Application Logic principle, each story must call out how its logic is covered by automated tests. When a story describes an invocation-only flow, mark it as manual verification with an explicit explanation of why automation is not feasible, except intent derivation which MUST be tested against the actual LLM model.

### User Story 1 - Traceable processed audio (Priority: P1)

As a user reviewing processed recordings, I want the moved audio files to share the same timestamp prefix as their intent output so I can quickly correlate an audio file with its intent JSON.

**Why this priority**: This is the core request and directly improves traceability between processed audio and intent output.

**Independent Test**: Can be fully tested with automated file-processing tests that simulate a processed transcript and verify the resulting filenames and locations.

**Acceptance Scenarios**:

1. **Given** a readable MP3 in the inbox and an intent output is written to the work folder, **When** the recording is moved to the processed folder, **Then** the processed audio filename is prefixed with the same timestamp as the intent output filename.
2. **Given** a readable MP3 in the inbox and an intent output is written, **When** the audio is moved, **Then** the original base filename remains after the timestamp prefix.

---

### User Story 2 - Consistent naming across runs (Priority: P2)

As a user processing multiple recordings, I want each processed audio file to use the matching intent timestamp so that files created in the same scan cycle remain distinct and easy to map to their intent outputs.

**Why this priority**: Prevents confusion and accidental overwrites when multiple recordings are processed.

**Independent Test**: Can be tested by processing multiple inbox files in a single run and verifying each processed file uses its corresponding intent timestamp prefix.

**Acceptance Scenarios**:

1. **Given** multiple readable MP3 files in the inbox, **When** each file is processed, **Then** each processed audio file is prefixed with the timestamp from its own intent output.

---

### Edge Cases

- What happens when an intent output cannot be written? The audio file is not moved, and no prefixed filename is created.
- How does the system handle a processed filename that already exists? The move must avoid overwriting and log a clear error without deleting the inbox file.

## Requirements *(mandatory)*

> NOTE: State for every requirement whether it is satisfied by automated tests or serves a manual invocation step, referencing the constitution’s Invocation Stewardship note when tests cannot cover the behavior. Intent derivation requires automated tests that use the actual LLM model.

### Functional Requirements

- **FR-001**: The system MUST prefix the processed audio filename with the same timestamp string used in the intent output filename for that recording, formatted as `<timestamp>-<original-filename>`. **(Automated test)**
- **FR-002**: The system MUST keep the original audio filename after the timestamp prefix so users can still recognize the source recording. **(Automated test)**
- **FR-003**: The system MUST use the intent output filename generated for the same recording as the source of the timestamp prefix. **(Automated test)**
- **FR-004**: If the intent output cannot be written, the system MUST NOT move or rename the audio file. **(Automated test)**
- **FR-005**: If a prefixed filename already exists in the processed folder, the system MUST avoid overwriting and MUST report the failure. **(Automated test)**

### Key Entities *(include if feature involves data)*

- **Intent Output**: The intent JSON file produced per recording, identified by a timestamped filename.
- **Processed Recording**: The audio file moved to the processed folder with a timestamp prefix that links it to the intent output.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of processed audio files in automated tests include the correct timestamp prefix that matches their intent output filename.
- **SC-002**: 0 instances of processed audio file overwrites occur in automated tests when a name collision is simulated.
- **SC-003**: Users can match a processed audio file to its intent output using the timestamp prefix in under 30 seconds during manual review.

## Assumptions

- Each processed recording produces exactly one intent output file.
- The timestamp portion of the intent output filename is the unique identifier to use as the prefix.
