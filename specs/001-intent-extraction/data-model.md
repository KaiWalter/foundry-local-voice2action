# Data Model: Intent Extraction Output

## Entities

### Transcript

- **Represents**: Plain text produced by the voice inbox transcription pipeline.
- **Fields**:
  - `text` (string): Transcribed content.
  - `source_path` (string): Path to the original audio file.
  - `transcribed_at` (datetime): Time the transcript was generated.

### IntentOutput

- **Represents**: The structured payload written to a JSON file in the work folder.
- **Fields**:
  - `intent` (enum): `create-task`, `create-note`.
  - `content` (string): User-requested action or note content.
  - `due` (datetime, optional): ISO 8601 timestamp in UTC offset form.
  - `reminder` (datetime, optional): ISO 8601 timestamp in UTC offset form.
  - `created_at` (datetime): Timestamp used to prefix the output filename.

### IntentOutputFile

- **Represents**: The file artifact in the work folder.
- **Fields**:
  - `filename` (string): `${created_at}-intent.json` with ISO 8601 prefix.
  - `path` (string): Absolute path to the file.
  - `payload` (IntentOutput): JSON object written to the file.

## Relationships

- `Transcript` 1→1 `IntentOutput`
- `IntentOutput` 1→1 `IntentOutputFile`

## Validation Rules

- `intent` must be `create-task` only when the transcript starts with “create a task” or “follow up”.
- If due/reminder are omitted, they must not appear in the JSON.
- If only a date is found, set the time to 06:00 UTC.
- `filename` must start with the ISO timestamp using `yyyyMMddThhmmss` (separators removed) and end with `-intent.json`.

## Validation Responsibility

- Output structure and field constraints are enforced exclusively through the model prompt and tool schema; no post-processing sanitization is applied in code.

## State Transitions

```text
[transcribed] -> [intent-extracted] -> [intent-file-written]
```
