---

description: "Task list for create-task webhook implementation"
---

# Tasks: Create-task webhook

**Input**: Design documents from /specs/001-create-task-webhook/
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included (automated tests are required by the specification).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Constitution note**: Webhook delivery logic must be covered by automated tests; end-to-end runs that invoke Foundry Local remain manual verification.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add shared test utilities used across user stories.

- [x] T001 [P] Create shared HTTP webhook test helper in tests/helpers/webhook_server.py (HTTPServer + queue capture + clean shutdown)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared configuration needed for all user stories.

- [x] T002 Add V2A_CREATE_TODO_WEBHOOK_URL configuration helper and validation in app.py

**Checkpoint**: Configuration helper available for user story implementation.

---

## Phase 3: User Story 1 - Create-task webhook call (Priority: P1) 🎯 MVP

**Goal**: Send a create-task intent to the webhook with the required JSON schema and headers.

**Independent Test**: Use a local HTTP server mock to validate payload shape, headers, method, and two provided content cases.

### Tests for User Story 1

- [x] T003 [P] [US1] Add webhook payload tests for the two provided create-task cases in tests/test_webhook.py
- [x] T004 [P] [US1] Add request formatting tests (POST, Content-Type, no auth header, 2xx success) in tests/test_webhook.py

### Implementation for User Story 1

- [x] T005 [US1] Implement webhook payload builder and POST dispatcher with urllib.request in app.py
- [x] T006 [US1] Invoke webhook dispatch during process_inbox_once for create-task intents in app.py
- [x] T007 [US1] Log webhook success/failure outcomes in app.py

**Checkpoint**: Create-task intents produce one webhook call with correct JSON and headers.

---

## Phase 4: User Story 2 - Non-task intents do not call webhook (Priority: P2)

**Goal**: Prevent create-note intents from triggering webhook calls.

**Independent Test**: Use the mock webhook server to verify zero requests for create-note intents.

### Tests for User Story 2

- [x] T008 [P] [US2] Add test ensuring create-note intents do not call the webhook in tests/test_webhook.py

### Implementation for User Story 2

- [x] T009 [US2] Guard webhook dispatch to only run when intent == "create-task" in app.py

**Checkpoint**: Non-task intents never trigger webhook calls.

---

## Phase 5: User Story 3 - Missing or failing webhook configuration (Priority: P3)

**Goal**: Handle missing/invalid URL and webhook failures without stopping processing.

**Independent Test**: Simulate missing URL, failing response, and verify errors are logged while processing continues.

### Tests for User Story 3

- [x] T010 [P] [US3] Add tests for missing/invalid webhook URL handling in tests/test_webhook.py
- [x] T011 [P] [US3] Add test ensuring webhook failure logs error and audio still moves in tests/test_processing.py

### Implementation for User Story 3

- [x] T012 [US3] Handle missing/invalid URL by logging error and skipping dispatch in app.py
- [x] T013 [US3] Treat non-2xx responses as failures without retries and continue processing in app.py

**Checkpoint**: Configuration and failure handling are robust and do not block processing.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and manual verification alignment.

- [x] T014 [P] Update README.md to document V2A_CREATE_TODO_WEBHOOK_URL behavior and webhook semantics
- [x] T015 Run manual quickstart verification in specs/001-create-task-webhook/quickstart.md (uv run app.py + webhook receiver) and record observations in that file

---

## Notes

- [P] tasks can run in parallel when they touch different files.
- All automated tests should run with `uv run pytest`.
- Manual verification is required for full pipeline runs that invoke Foundry Local.
