# Feature Specification: Create-task webhook

**Feature Branch**: `001-create-task-webhook`  
**Created**: 2026-02-01  
**Status**: Draft  
**Input**: User description: "when intent is identified as create-task, app shall call a webhook url defined by V2A_CREATE_TODO_WEBHOOK_URL converting the intent exactly into this structure / JSON schema: { "type": "object", "properties": { "title": { "type": "string" }, "due": { "type": "string" }, "reminder": { "type": "string" } }, "required": [ "title" ] } for testing create a mock for the webhook that checks the structure and content based on these 2 cases { "intent": "create-task", "content": "upload the Performance Review Files", "reminder": "2026-02-02T06:00:00+00:00" } { "intent": "create-task", "content": "Follow-up with my boss. We should talk about our AI strategy.", "due": "2026-08-30T06:00:00Z", "reminder": "2026-08-20T06:00:00Z" }"

## Clarifications

### Session 2026-02-01

- Q: What HTTP response codes count as a successful webhook call? → A: Any 2xx response is success.
- Q: Should webhook calls be retried on failure? → A: Single attempt only (no retries).
- Q: What HTTP method and content type should be used for the webhook call? → A: POST with Content-Type: application/json.
- Q: What should happen to the audio file when the webhook call fails? → A: Log error and still move file to processed.
- Q: Should the webhook include an authorization header? → A: No auth header.

## User Scenarios & Testing *(mandatory)*

> NOTE: Per the constitution’s Testable Application Logic principle, each story must call out how its logic is covered by automated tests. When a story describes an invocation-only flow, mark it as manual verification with an explicit explanation of why automation is not feasible, except intent derivation which MUST be tested against the actual LLM model.

### User Story 1 - Create-task webhook call (Priority: P1)

As a user who records a task, I want create-task intents to trigger a webhook call so my to-do system receives the task immediately.

**Why this priority**: This is the core value—without the webhook call, tasks never reach the downstream system.

**Independent Test**: Can be fully tested with an automated mock webhook that asserts payload shape and content for the two provided cases.

**Acceptance Scenarios**:

1. **Given** a create-task intent with `content` and `reminder` only, **When** the intent is processed, **Then** the webhook is called once with JSON containing `title` equal to `content`, `reminder` equal to the intent reminder, and no `due` field.
2. **Given** a create-task intent with `content`, `due`, and `reminder`, **When** the intent is processed, **Then** the webhook is called once with JSON containing `title`, `due`, and `reminder` that exactly match the intent values.

---

### User Story 2 - Non-task intents do not call webhook (Priority: P2)

As a user recording notes, I want create-note intents to avoid webhook calls so my to-do list is not polluted.

**Why this priority**: Prevents incorrect downstream actions and preserves trust in the automation.

**Independent Test**: Can be tested with an automated mock webhook verifying no call occurs for non-task intents.

**Acceptance Scenarios**:

1. **Given** a create-note intent, **When** the intent is processed, **Then** no webhook call is made.

---

### User Story 3 - Missing or failing webhook configuration (Priority: P3)

As an operator, I want missing or failing webhook configuration to be reported so I can fix delivery issues without losing processed files.

**Why this priority**: Ensures reliability and debuggability for real-world integrations.

**Independent Test**: Can be tested with automated cases that omit the webhook URL or simulate a failure and verify error reporting.

**Acceptance Scenarios**:

1. **Given** a create-task intent and no webhook URL configured, **When** the intent is processed, **Then** the system records a clear error and continues processing other files.
2. **Given** a create-task intent and a webhook endpoint that fails, **When** the intent is processed, **Then** the system records the failure and continues processing other files.

---

### Edge Cases

- Webhook URL is set but empty or malformed.
- Webhook endpoint returns non-success responses or times out.
- Webhook endpoint returns 204 No Content but should still be treated as success.
- Intent includes only `content` (no `due` or `reminder`).
- Intent contains `due` and `reminder` with different timezone suffixes (Z vs +00:00) that must be preserved.

## Requirements *(mandatory)*

> NOTE: State for every requirement whether it is satisfied by automated tests or serves a manual invocation step, referencing the constitution’s Invocation Stewardship note when tests cannot cover the behavior. Intent derivation requires automated tests that use the actual LLM model.

### Functional Requirements

- **FR-001**: System MUST read the webhook URL from `V2A_CREATE_TODO_WEBHOOK_URL`. **Test**: Automated (configuration test).
- **FR-002**: When an intent is `create-task`, system MUST send a JSON payload to the webhook where `title` equals the intent `content`. **Test**: Automated (mock webhook assertions).
- **FR-003**: If the intent includes `due` and/or `reminder`, system MUST include those fields with identical string values; if a field is absent, it MUST be omitted from the payload. **Test**: Automated (mock webhook assertions).
- **FR-004**: For intents that are not `create-task`, system MUST NOT call the webhook. **Test**: Automated (mock webhook asserts no calls).
- **FR-005**: If the webhook URL is missing or invalid, system MUST record a clear error and continue processing. **Test**: Automated (missing/invalid configuration).
- **FR-006**: If the webhook call fails, system MUST record the failure and continue processing remaining items. **Test**: Automated (mock webhook failure).
- **FR-007**: System MUST treat any HTTP 2xx response from the webhook as success and any non-2xx as failure. **Test**: Automated (mock webhook status codes).
- **FR-008**: System MUST attempt the webhook call only once per create-task intent (no retries). **Test**: Automated (mock call count).
- **FR-009**: System MUST send the webhook payload using HTTP POST with `Content-Type: application/json`. **Test**: Automated (mock request inspection).
- **FR-010**: If the webhook call fails, system MUST log the error and still move the audio file to the processed folder. **Test**: Automated (mock failure with file move check).
- **FR-011**: System MUST NOT include an authorization header in the webhook request. **Test**: Automated (mock request inspection).
- **FR-012**: System MUST log request and response payloads when the webhook returns HTTP 400. **Test**: Automated (mock 400 response).

**Acceptance Coverage**: FR-001 through FR-006 are covered by User Story acceptance scenarios 1-3.

### Key Entities *(include if feature involves data)*

- **Intent**: A detected action with `intent`, `content`, and optional `due` and `reminder` timestamps.
- **To-do Webhook Request**: A JSON object containing `title` and optional `due` and `reminder` fields sent to the configured webhook.

## Assumptions

- If `due` or `reminder` is not present on the intent, the corresponding field is omitted from the webhook payload.
- Failure to call the webhook should not block moving or logging processed audio files.

## Dependencies

- A reachable webhook endpoint is provided via `V2A_CREATE_TODO_WEBHOOK_URL`.
- The webhook endpoint accepts the required JSON schema with `title` and optional `due` and `reminder` fields.

## Out of Scope

- Creating or managing tasks directly in external systems outside the webhook call.
- Changes to intent extraction rules or transcript handling logic.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of create-task intents in automated tests result in exactly one webhook call with a payload that matches the required schema and values.
- **SC-002**: 0% of create-note intents trigger webhook calls in automated tests.
- **SC-003**: 100% of simulated missing/invalid URL and webhook failure cases record a clear error without halting processing.
- **SC-004**: Webhook calls are attempted in the same processing pass as intent extraction for create-task intents.
