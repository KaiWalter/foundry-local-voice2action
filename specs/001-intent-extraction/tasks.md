# Tasks: Intent Extraction Output File

**Input**: Design documents from `/specs/001-intent-extraction/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included (required by constitution for application logic).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and shared test inputs

- [X] T001 [P] Add shared transcript fixtures in tests/fixtures/intent_transcripts.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helpers required by all user stories

- [X] T002 Add intent payload typing + prompt schema scaffold in app.py
- [X] T004 [P] Add intent filename builder helper (yyyyMMddThhmmss prefix) in app.py
- [X] T005 Add intent JSON writer helper for `.work` in app.py
- [X] T006 [P] Add unit tests for filename helper in tests/test_intent_helpers.py

**Checkpoint**: Foundational helpers and tests in place

---

## Phase 3: User Story 1 - Create intent output file (Priority: P1) 🎯 MVP

**Goal**: Produce a single intent output JSON file per transcript

**Independent Test**: Provide a transcript and verify a single `yyyyMMddThhmmss-intent.json` file is written with required keys only

### Tests for User Story 1

- [X] T007 [P] [US1] Add tests for intent file structure + required fields in tests/test_intent_extraction.py

### Implementation for User Story 1

- [X] T008 [US1] Implement Foundry Local intent extraction call (OpenAI SDK + tool calling) in app.py
- [X] T009 [US1] Integrate intent extraction + file writing into process_inbox_once in app.py
- [X] T010 [US1] Add intent output logging in app.py

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 - Infer due and reminder timestamps (Priority: P2)

**Goal**: Populate `due` and `reminder` in ISO 8601 format when detectable

**Independent Test**: Provide date-only and date-time inputs and verify normalization rules in output JSON

### Tests for User Story 2

- [X] T011 [P] [US2] Add tests that verify prompt expectations for due/reminder in tests/test_intent_extraction.py

### Implementation for User Story 2

- [X] T012 [US2] Encode due/reminder ISO rules (including missing year/month assumptions) in the intent extraction prompt in app.py

**Checkpoint**: User Story 2 fully functional and testable independently

---

## Phase 5: User Story 3 - Fallback to note intent (Priority: P3)

**Goal**: Default to `create-note` when the intent is ambiguous

**Independent Test**: Provide ambiguous inputs and verify `intent` becomes `create-note`

### Tests for User Story 3

- [X] T013 [P] [US3] Add tests for fallback intent behavior in tests/test_intent_extraction.py

### Implementation for User Story 3

- [X] T014 [US3] Encode fallback to `create-note` in the intent extraction prompt in app.py

**Checkpoint**: User Story 3 fully functional and testable independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality, documentation, and manual verification

- [X] T015 [P] Record manual verification steps and observations (including alias logging) in specs/001-intent-extraction/quickstart.md
- [X] T016 Run uv run pytest and note results in specs/001-intent-extraction/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational helpers
- **User Story 2 (P2)**: Depends on Foundational helpers; integrates with US1 prompt-only constraints
- **User Story 3 (P3)**: Depends on Foundational helpers; integrates with US1 prompt-only constraints

### Within Each User Story

- Tests should be written first and fail before implementation
- Helper functions before integration into `process_inbox_once`
- Story complete before moving to next priority (for MVP flow)

### Parallel Opportunities

- T001, T004, T006, T007, T011, T013, T015 can run in parallel (separate files)
- User story tests can proceed in parallel once Foundational helpers exist

---

## Parallel Example: User Story 1

```text
Task: "T007 [US1] Add tests for intent file structure + required fields in tests/test_intent_extraction.py"
Task: "T004 Add intent filename builder helper in app.py" (if not completed)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and validate User Story 1 independently

### Incremental Delivery

1. Add User Story 1 → test independently → demo
2. Add User Story 2 → test independently → demo
3. Add User Story 3 → test independently → demo
4. Complete Polish phase

### Parallel Team Strategy

- One dev on helper functions in app.py
- Another dev on tests in tests/test_intent_extraction.py
- Manual verification and documentation can be done after core logic lands

---

## Notes

- [P] tasks = different files, no dependencies
- Manual verification for Foundry Local invocation remains required per constitution
- All tasks include file paths to keep execution unambiguous
