# Implementation Plan: Timestamp processed audio

**Branch**: `001-timestamp-processed-audio` | **Date**: 2026-02-01 | **Spec**: [specs/001-timestamp-processed-audio/spec.md](specs/001-timestamp-processed-audio/spec.md)
**Input**: Feature specification from `/specs/001-timestamp-processed-audio/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Process inbox recordings by retaining the intent-output timestamp when moving the MP3 into `.voice-processed`. Introduce helpers that capture the timestamp produced in `write_intent_output`, reuse it for the destination filename (`<timestamp>-<original-name>`), and extend the existing file-processing tests so they assert timestamp alignment, collision avoidance, and fail-fast behavior when intent output is unavailable.

## Technical Context

**Language/Version**: Python >= 3.14 (UV-managed runtime used for scripts/tests)  
**Primary Dependencies**: whisper, foundry-local-sdk, openai, openai-whisper, pathlib/shutil, pytest  
**Storage**: Local filesystem directories (`.voice-inbox`, `.voice-processed`, `.work`) and intent JSON metadata  
**Testing**: pytest suites under `tests/` invoked via `uv run pytest`  
**Target Platform**: Cross-platform developer workstation with FFmpeg + Foundry Local (Windows primary), running CLI from repo root  
**Project Type**: Single Python CLI utility plus regression tests  
**Performance Goals**: Keep scan loop lightweight (existing 30‑second interval) and avoid blocking file I/O; no new time constraints  
**Constraints**: All file operations must guard against overwrites; rename must only happen after intent JSON is persisted; keep operations offline and under uv-managed interpreter  
**Scale/Scope**: Local only (a few recordings per scan) with low concurrency, consistent with existing inbox scanner

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Testable Application Logic**: The new timestamp-prefix behavior is verified by extending `tests/test_processing.py` (and any supporting helpers) to assert the renamed files match the intent timestamp, the original filename is preserved, and failure cases leave the inbox untouched. No manual verification is required.
- **Invocation Stewardship**: The change does not introduce new Foundry or CLI invocations; it stays within the existing scanning loop. Transcription continues to rely on `sample-transcribe.py` style usage of Whisper; there are no additional manual steps beyond the current voice inbox workflow.
- **Python + uv First Flow**: Entry point remains `app.py` executed as `uv run app.py`. Tests execute via `uv run pytest tests/test_processing.py` so all work stays in the uv-managed Python environment.
- **Reference Implementations**: The updated behavior builds on the existing `app.py` flow and keeps transcription/Test expectations aligned with `sample-transcribe.py` for audio handling.

## Project Structure

### Documentation (this feature)

```text
specs/001-timestamp-processed-audio/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app.py                  # Voice inbox scanner entry point
tests/
├── test_processing.py   # Already covers process_inbox helpers and will extend for timestamp prefix
├── test_transcription.py
└── ... (other existing suites can reference new helpers if needed)
```

**Structure Decision**: Single CLI-oriented Python repository; core logic lives in `app.py` with tests under `tests/`. No new directories added for this feature.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected; no special mitigation needed.
