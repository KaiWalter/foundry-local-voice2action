# Data Model: Create-task webhook

## Entities

### Intent

- **Represents**: The extracted intent output from the voice pipeline.
- **Fields**:
  - `intent` (enum): `create-task` or `create-note`.
  - `content` (string): User-requested task text.
  - `due` (datetime, optional): ISO 8601 timestamp string.
  - `reminder` (datetime, optional): ISO 8601 timestamp string.

### TodoWebhookRequest

- **Represents**: Payload sent to the create-to-do webhook.
- **Fields**:
  - `title` (string): Copied from `Intent.content`.
  - `due` (datetime, optional): Copied from `Intent.due` when present.
  - `reminder` (datetime, optional): Copied from `Intent.reminder` when present.

### WebhookDeliveryResult

- **Represents**: Result of attempting to deliver the webhook.
- **Fields**:
  - `status_code` (int): HTTP response status code.
  - `success` (bool): True when status code is 2xx.
  - `error` (string, optional): Error message if request fails or returns non-2xx.

## Relationships

- `Intent` 1→0..1 `TodoWebhookRequest` (only when `intent` is `create-task`).
- `TodoWebhookRequest` 1→1 `WebhookDeliveryResult`.

## Validation Rules

- `title` must exactly equal the `Intent.content` string.
- `due` and `reminder` must be omitted if absent on the `Intent`.
- Timestamp strings must be preserved as-is (Z vs +00:00).

## State Transitions

```text
[intent-extracted] -> [webhook-delivered | webhook-failed]
```
