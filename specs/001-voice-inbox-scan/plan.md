# Implementation Plan: Voice Inbox Transcription

**Branch**: `001-voice-inbox-scan` | **Date**: 2026-01-31 | **Spec**: [specs/001-voice-inbox-scan/spec.md](specs/001-voice-inbox-scan/spec.md)
**Input**: Feature specification from `/specs/001-voice-inbox-scan/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a local CLI loop in `app.py` that scans a configurable inbox every 30 seconds, transcribes new MP3 files using Whisper (English), logs results to console and a work-file log, and moves successfully processed recordings to a processed folder. Folders are created on startup and excluded from Git. Design aligns with sample-transcribe.py for Whisper usage.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python >= 3.14 (uv-managed)  
**Primary Dependencies**: openai-whisper (Whisper), FFmpeg (runtime dependency)  
**Storage**: Local filesystem folders (`.voice-inbox`, `.voice-processed`, `.work`)  
**Testing**: pytest (unit tests for scanning, routing, and file moves)  
**Target Platform**: Local developer machines (Windows/macOS/Linux)  
**Project Type**: Single-script CLI in repository root  
**Performance Goals**: Process discovered MP3s within the configured scan interval (default 30s)  
**Constraints**: Offline-capable, local-first; log to console + `.work` file; avoid external services  
**Scale/Scope**: Single-user demo; small batches of MP3 files per scan

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Testable Application Logic**: confirm every behavior described above either ships with automated tests or a concrete test plan describing how the code can be exercised independently of invocations.
- **Invocation Stewardship**: surface any flow that runs Foundry services, CLI tooling, or runtime commands as a manual verification item, including the success criteria to be observed by a reviewer.
- **Python + uv First Flow**: declare the Python ≥3.14 entry point and the `uv run …` invocation that will execute the plan so the runtime stays aligned with the constitution.
- **Reference Implementations**: when the feature borders agent tooling or transcription flows, point to sample-agent-framework.py or sample-transcribe.py as the design anchor.

Constitution check (pre-design):

- Testable logic: inbox scanning, file filtering, move logic, and logging behavior will be covered by pytest with filesystem fixtures/mocks.
- Invocation stewardship: Whisper/FFmpeg transcription is a manual verification step; tests will not invoke the model.
- Python + uv flow: execution via `uv run app.py`.
- Reference: sample-transcribe.py is the transcription anchor for Whisper usage.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
app.py
sample-transcribe.py
specs/
tests/
```

**Structure Decision**: Single-script CLI at repo root with new tests under `tests/`.

Constitution check (post-design):

- Testable logic: Planned unit tests cover scanning, filtering, logging, and move logic without invoking Whisper.
- Invocation stewardship: Manual verification will cover Whisper/FFmpeg transcription with real MP3s.
- Python + uv flow: Execution remains `uv run app.py`.
- Reference: sample-transcribe.py remains the Whisper behavior reference.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| ----------- | ------------ | ------------------------------------- |
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
