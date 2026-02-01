---

description: "Task list for the timestamped processed audio feature"
---

# Tasks: Timestamp processed audio

**Input**: Design documents from `/specs/001-timestamp-processed-audio/`
**Prerequisites**: plan.md, spec.md

**Tests**: Automated tests are required by the spec for all functional requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add shared test helpers to keep timestamp expectations consistent.

- [x] T001 [P] Add a shared helper in tests/test_processing.py that derives the `<timestamp>` prefix from the intent output filename stored under the work directory for assertions.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Centralize timestamp parsing and processed-file naming in the application code.

- [x] T002 Implement a helper in app.py that accepts the intent output Path, original MP3 name, and processed directory and returns the destination Path formatted as `<timestamp>-<original-name>`.

---

## Phase 3: User Story 1 - Traceable processed audio (Priority: P1) 🎯 MVP

**Goal**: Rename processed recordings using the intent timestamp and handle failure cases without overwriting or moving files incorrectly.

**Independent Test**: `uv run pytest tests/test_processing.py` verifies timestamp renaming, collision handling, and intent-write failure behavior.

### Tests for User Story 1

- [x] T003 [P] [US1] Update tests/test_processing.py to assert the processed MP3 is renamed to `<timestamp>-voice.mp3` where `<timestamp>` matches the intent JSON filename created in `.work`.
- [x] T004 [P] [US1] Add a collision test in tests/test_processing.py that pre-creates `<timestamp>-voice.mp3` in `.voice-processed`, runs process_inbox_once, and asserts the inbox file remains while the collision is logged.
- [x] T005 [P] [US1] Add a failure test in tests/test_processing.py that monkeypatches app.write_intent_output to raise and asserts the inbox MP3 is not moved and `.voice-processed` remains empty.

### Implementation for User Story 1

- [x] T006 [US1] Update process_inbox_once in app.py to handle write_intent_output failures, use the new helper for the destination filename, and skip moves when the destination already exists (log the failure).

**Checkpoint**: US1 is complete when the new tests pass and processed filenames always follow `<timestamp>-<original-name>` without overwriting or losing files.

---

## Phase 4: User Story 2 - Consistent naming across runs (Priority: P2)

**Goal**: Ensure each processed file uses its own intent timestamp when multiple recordings are handled in a single scan.

**Independent Test**: A multi-file pytest scenario verifies each processed file uses its own intent timestamp.

### Tests for User Story 2

- [x] T007 [US2] Add a multi-file test in tests/test_processing.py that processes two MP3s in one call and asserts each processed filename matches its own intent JSON timestamp prefix.

**Checkpoint**: US2 is complete when the multi-file test passes and shows distinct, matching timestamps per recording.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Document the updated naming convention for reviewers.

- [x] T008 [P] Update README.md to note processed MP3s are prefixed with the intent timestamp (`<timestamp>-<original-name>`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 can start immediately.
- **Foundational (Phase 2)**: T002 depends on understanding the intent filename format; complete before US1.
- **User Story 1 (Phase 3)**: T006 depends on T002; tests T003–T005 depend on T006 and T001.
- **User Story 2 (Phase 4)**: T007 depends on US1 completion.
- **Polish (Phase 5)**: T008 can run after implementation details are stable.

### User Story Dependencies

- **US1 (P1)**: Blocks US2 because the core rename behavior must exist.
- **US2 (P2)**: Depends on US1 completion.

### Parallel Opportunities

- T001 and T002 can run in parallel (different files).
- T003, T004, and T005 are marked [P] but all touch tests/test_processing.py; coordinate to avoid conflicts.
- T008 can run in parallel with T007 once US1 implementation is stable.

---

## Parallel Execution Examples

### User Story 1

- **Parallel test tasks**: T003, T004, T005 (coordinate to avoid merge conflicts in tests/test_processing.py).
- **Implementation task**: T006 must complete before tests can pass.

### User Story 2

- **Single task**: T007 can run while T008 updates README.md.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 and T002.
2. Implement T006, then complete T003–T005.
3. Run `uv run pytest tests/test_processing.py`.

### Incremental Delivery

1. Deliver US1 (T001–T006) as the MVP.
2. Add US2 test coverage (T007).
3. Update documentation (T008).

---

## Notes

- Keep all changes within app.py, tests/test_processing.py, and README.md.
- Always derive the prefix from the intent filename created for the same recording.
