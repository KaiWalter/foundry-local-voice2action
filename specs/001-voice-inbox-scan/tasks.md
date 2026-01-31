---

description: "Task list for Voice Inbox Transcription"
---

# Tasks: Voice Inbox Transcription

**Input**: Design documents from `/specs/001-voice-inbox-scan/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included (required by constitution for application logic).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Constitution note**: Every task with application logic includes automated test coverage; invocation-only tasks are manual and include the `uv run …` command with expected observations.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Update pyproject.toml and uv.lock to add pytest dependency for automated tests
- [x] T002 [P] Add shared test fixtures for temp inbox/work/processed dirs in tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Implement environment configuration parsing and validation in app.py (V2A_VOICE_INBOX, V2A_VOICE_PROCESSED, V2A_SCAN_INTERVAL, defaults)
- [x] T004 [P] Add config parsing tests in tests/test_config.py
- [x] T005 Implement logging setup (console + .work log file) in app.py
- [x] T006 [P] Add logging initialization tests in tests/test_logging.py
- [x] T007 Implement startup directory creation for inbox/processed/work in app.py
- [x] T008 [P] Add directory creation tests in tests/test_directories.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - See transcriptions from new recordings (Priority: P1) 🎯 MVP

**Goal**: Detect MP3 files in the inbox, transcribe them in English, and print results to the console.

**Independent Test**: Run unit tests for scanning, filtering, and transcription dispatch without invoking Whisper.

### Tests for User Story 1

- [x] T009 [P] [US1] Add scanning/filtering tests (MP3 only, non-MP3 warnings) in tests/test_scanning.py
- [x] T010 [P] [US1] Add transcription configuration/dispatch tests without invoking Whisper in tests/test_transcription.py
- [x] T011 [P] [US1] Add tests to assert no transcript files are written to disk in tests/test_transcription.py

### Implementation for User Story 1

- [x] T012 [US1] Implement inbox scanning and MP3 filtering in app.py
- [x] T013 [US1] Implement Whisper transcription wrapper in app.py (reuse model, force English; reference sample-transcribe.py)
- [x] T014 [US1] Implement error handling for locked/unreadable files and transcription failures in app.py

**Checkpoint**: User Story 1 is functional and testable independently

---

## Phase 4: User Story 2 - Processed recordings are archived (Priority: P2)

**Goal**: Move successfully processed MP3 files to the processed folder to prevent reprocessing.

**Independent Test**: Unit tests verify files are moved on success and remain in inbox on failure.

### Tests for User Story 2

- [x] T015 [P] [US2] Add move-to-processed tests in tests/test_processing.py

### Implementation for User Story 2

- [x] T016 [US2] Implement move-to-processed behavior after successful transcription in app.py

**Checkpoint**: User Stories 1 and 2 are both functional and testable independently

---

## Phase 5: User Story 3 - Folders are created and ignored by Git (Priority: P3)

**Goal**: Ensure runtime folders are created at startup and excluded from Git tracking.

**Independent Test**: Unit tests validate folder creation; .gitignore change is reviewable in diff.

### Implementation for User Story 3

- [x] T017 [US3] Update .gitignore to exclude .voice-inbox/, .voice-processed/, and .work/

**Checkpoint**: All user stories are functional and testable independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and manual verification of invocation-only flows

- [x] T018 [P] Update README.md with environment variables, defaults, and runtime folder behavior
- [x] T019 Manual verification: run `uv run app.py`, drop an MP3 into the inbox, observe console output + .work log, confirm move to processed (record observations in specs/001-voice-inbox-scan/quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Depends on User Story 1 completion (needs successful transcription)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- T002, T004, T006, T008, T009, T010, T011, T015, T018 can run in parallel (different files)

---

## Parallel Example: User Story 1

```text
Task: "Add scanning/filtering tests (MP3 only, non-MP3 warnings) in tests/test_scanning.py"
Task: "Add transcription configuration/dispatch tests without invoking Whisper in tests/test_transcription.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run tests for US1 independently

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → test independently → demo
3. Add User Story 2 → test independently → demo
4. Add User Story 3 → review .gitignore + folder creation tests
5. Manual verification of Whisper/FFmpeg via `uv run app.py`
