# Feature Specification: Intent Extraction Output File

**Feature Branch**: `001-intent-extraction`  
**Created**: 2026-02-01  
**Status**: Draft  
**Input**: User description: "Based on the transcript created with #file:001-voice-inbox-scan use a LLM to determine the intent of the user. Result of this process shall be a file with ISO timestamp in the work folder with only this and no other structure: intent: \"create-task|create-note\", content: \"...\", due: \"YYYY-MM-DDThh:mm:ssZ or YYYY-MM-DDThh:mm:ss+00:00\", reminder: \"YYYY-MM-DDThh:mm:ssZ or YYYY-MM-DDThh:mm:ss+00:00\". if the intent is clearly stated at the beginning of the record to \"create a task\", \"follow up\" then respond with above structure with intent=\"create-task\" trying also to determine a due date/time and reminder for that task in ISO format. if either of those cannot be determined do not have these fields in the return structure. if only a date can be determined for these fields, assume 06:00 UTC as start of the business day. Only if not clear intent can be determined fall back to intent=\"create-note\"."

## Clarifications

### Session 2026-02-01

- Q: What is the file format for the intent output content? → A: JSON object with only the allowed keys.
- Q: What is the filename format for intent output files? → A: Prefix with ISO 8601 date/time, remove "-" and ":" from the timestamp for the filename fragment (format `yyyyMMddThhmmss`), and suffix with "-intent.json".

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

### User Story 1 - Create intent output file (Priority: P1)

As a user of the voice inbox workflow, I want each transcript to produce a single intent output file in the work folder so that downstream actions can read a standardized intent and content payload.

**Why this priority**: This is the core value—without the intent output file, the workflow cannot proceed to task or note handling.

**Independent Test**: Can be fully tested by providing a transcript string and verifying that exactly one output file is created with the required keys and ISO timestamps.

**Acceptance Scenarios**:

1. **Given** a transcript that begins with “create a task” and includes a clear description, **When** intent extraction runs, **Then** the system writes a single output file containing `intent: "create-task"` and a `content` line that reflects the request.
2. **Given** a transcript with no explicit task phrasing, **When** intent extraction runs, **Then** the system writes a single output file containing `intent: "create-note"` and a `content` line that reflects the request.

---

### User Story 2 - Infer due and reminder timestamps (Priority: P2)

As a user, I want due dates and reminders to be inferred from the transcript when present so that tasks can be scheduled without extra manual steps.

**Why this priority**: Scheduling information is critical for task usefulness, but only after the base intent output exists.

**Independent Test**: Can be tested with controlled transcripts that include full date-time phrases, date-only phrases, and no dates, verifying the resulting fields.

**Acceptance Scenarios**:

1. **Given** a transcript that specifies a due date and time, **When** intent extraction runs, **Then** the output file includes `due` in ISO 8601 format.
2. **Given** a transcript that specifies only a date, **When** intent extraction runs, **Then** the output file includes `due` set to $06{:}00$ UTC on that date.
3. **Given** a transcript with no due date or reminder mentioned, **When** intent extraction runs, **Then** the output file omits `due` and `reminder` entirely.

---

### User Story 3 - Fallback to note intent (Priority: P3)

As a user, I want ambiguous transcripts to be captured as notes rather than tasks so that uncertain requests do not trigger unintended scheduling.

**Why this priority**: It reduces risk of false task creation while still preserving user input.

**Independent Test**: Can be tested with transcripts that lack clear task language and verifying that intent is `create-note`.

**Acceptance Scenarios**:

1. **Given** a transcript that does not start with a clear task directive, **When** intent extraction runs, **Then** the output intent is `create-note`.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Transcript is empty or only contains filler words.
- Transcript contains multiple dates and times with conflicting meanings.
- Transcript includes time zone hints that are not UTC.
- Transcript begins with “follow up” but contains no actionable content.
- Transcript includes a task intent but no content after the intent phrase.

## Requirements *(mandatory)*

> NOTE: State for every requirement whether it is satisfied by automated tests or serves a manual invocation step, referencing the constitution’s Invocation Stewardship note when tests cannot cover the behavior.

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST accept a transcript produced by the voice inbox scan as the sole input for intent extraction. **Test**: Automated.
- **FR-002**: System MUST classify intent as `create-task` when the transcript starts with an explicit directive such as “create a task” or “follow up”. **Test**: Automated with labeled transcripts.
- **FR-003**: System MUST classify intent as `create-note` when the transcript does not clearly begin with a task directive. **Test**: Automated with labeled transcripts.
- **FR-004**: System MUST write exactly one output file to the work folder for each processed transcript. **Test**: Automated.
- **FR-005**: The output file MUST be a JSON object containing only the fields `intent`, `content`, and optionally `due` and `reminder`, with no additional keys or nested structure. **Test**: Automated.
- **FR-006**: The `content` field MUST capture the user’s requested action or note content in plain text derived from the transcript. **Test**: Automated with curated examples.
- **FR-007**: When a due date/time is explicitly stated, the output MUST include a `due` field in ISO 8601 format using `Z` or `+00:00` for UTC. **Test**: Automated with time parsing fixtures.
- **FR-008**: When only a date is stated, the output MUST set the time to $06{:}00$ UTC for `due` or `reminder`. **Test**: Automated.
- **FR-009**: When a due date or reminder cannot be determined, the output MUST omit those fields entirely. **Test**: Automated.
- **FR-010**: The output filename MUST be prefixed with the ISO 8601 timestamp of creation, with "-" and ":" removed for the filename fragment (`yyyyMMddThhmmss`), and suffixed with "-intent.json". **Test**: Automated filename validation.
- **FR-011**: If intent extraction depends on runtime model invocation, the model invocation outcome MUST be manually verified end-to-end due to external dependency constraints. **Test**: Manual verification (Invocation Stewardship).

### Key Entities *(include if feature involves data)*

- **Transcript**: The plain-text output from the voice inbox transcription pipeline.
- **Intent Output File**: A single file written to the work folder containing the intent payload.
- **Intent Fields**: The `intent`, `content`, and optional `due` and `reminder` values derived from the transcript.

## Assumptions

- Each transcript is processed exactly once to produce one output file.
- The work folder referenced in the workflow is the designated destination for intent output files.
- ISO 8601 timestamps in data fields use `Z` or `+00:00` for UTC (e.g., $2026\text{-}02\text{-}01T06{:}00{:}00Z$ or $2026\text{-}02\text{-}01T06{:}00{:}00+00{:}00$), and filename prefixes use the same instant with separators removed ($20260201T060000$).
- No post-processing or sanitization is applied beyond using the prompt to constrain model output.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 90% of transcripts in a labeled evaluation set are classified with the correct intent.
- **SC-002**: For transcripts that include explicit due date/time phrases, at least 95% of outputs contain correctly formatted ISO 8601 `due` values.
- **SC-003**: 100% of intent output files conform to the required field set and contain no extra keys.
- **SC-004**: Intent output files are created within 2 seconds of transcript availability for 95% of runs.
