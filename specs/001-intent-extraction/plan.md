# Implementation Plan: Intent Extraction Output File

**Branch**: `001-intent-extraction` | **Date**: 2026-02-01 | **Spec**: [specs/001-intent-extraction/spec.md](specs/001-intent-extraction/spec.md)
**Input**: Feature specification from `/specs/001-intent-extraction/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add intent extraction after transcription so each transcript yields a single JSON intent file in the work folder. The implementation will call a Foundry Local model via the OpenAI SDK (using the local endpoint and alias-resolved model ID), log the effective model alias, enforce a tool-call schema for `intent`, `content`, `due`, and `reminder` via prompt-only constraints (no code sanitization), and write a `yyyyMMddThhmmss-intent.json` file derived from the ISO timestamp with separators removed.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.14 (uv-managed)  
**Primary Dependencies**: openai, foundry-local-sdk, agent-framework (reference), openai-whisper  
**Storage**: Local files in `.work` (intent output JSON + logs)  
**Testing**: pytest  
**Target Platform**: Local desktop (Windows/macOS/Linux)  
**Project Type**: Single-file CLI workflow in repo root  
**Performance Goals**: Intent output file created within 2 seconds of transcript availability for most runs  
**Constraints**: Offline-capable; Foundry Local runtime required; no cloud services  
**Scale/Scope**: Single-user local workflow; low throughput (one inbox folder)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Testable Application Logic**: confirm every behavior described above either ships with automated tests or a concrete test plan describing how the code can be exercised independently of invocations.
- **Invocation Stewardship**: surface any flow that runs Foundry services, CLI tooling, or runtime commands as a manual verification item, including the success criteria to be observed by a reviewer.
- **Python + uv First Flow**: declare the Python ≥3.14 entry point and the `uv run …` invocation that will execute the plan so the runtime stays aligned with the constitution.
- **Reference Implementations**: when the feature borders agent tooling or transcription flows, point to sample-agent-framework.py or sample-transcribe.py as the design anchor.
\
Status:
- Testable Application Logic: ✅ Unit tests will cover prompt-shape expectations, file naming, and JSON field presence. Model invocation remains manual.
- Invocation Stewardship: ✅ Foundry Local model invocation called out for manual verification in quickstart.
- Python + uv First Flow: ✅ `uv run app.py` remains the entry point.
- Reference Implementations: ✅ Use [sample-agent-framework.py](sample-agent-framework.py) for LLM invocation pattern and [sample-transcribe.py](sample-transcribe.py) for transcription reference.

## Project Structure

### Documentation (this feature)

```text
specs/001-intent-extraction/
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
sample-agent-framework.py
sample-transcribe.py
specs/
tests/
  ├── test_config.py
  ├── test_directories.py
  ├── test_logging.py
  ├── test_processing.py
  ├── test_scanning.py
  └── test_transcription.py
```

**Structure Decision**: Single-project CLI workflow in repo root with pytest tests under `tests/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| ----------- | ------------ | ------------------------------------- |
| None | N/A | N/A |

## Phase 0: Outline & Research

- ✅ [specs/001-intent-extraction/research.md](specs/001-intent-extraction/research.md) created with decisions on LLM invocation, tool calling, prompt-only constraints, and manual verification boundaries.

## Phase 1: Design & Contracts

- ✅ [specs/001-intent-extraction/data-model.md](specs/001-intent-extraction/data-model.md) defined entities and validation rules.
- ✅ [specs/001-intent-extraction/contracts/README.md](specs/001-intent-extraction/contracts/README.md) documented no external API contracts.
- ✅ [specs/001-intent-extraction/quickstart.md](specs/001-intent-extraction/quickstart.md) documented manual verification for model invocation.
- ✅ Agent context updated via `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`.

## Constitution Check (Post-Design)

- **Testable Application Logic**: ✅ Planned tests will cover prompt expectations and file naming; model invocation is excluded from automated tests.
- **Invocation Stewardship**: ✅ Foundry Local invocation documented as manual verification in quickstart.
- **Python + uv First Flow**: ✅ `uv run app.py` remains the execution path.
- **Reference Implementations**: ✅ Plan references sample-agent-framework.py and sample-transcribe.py patterns.

## Phase 2: Implementation Plan

1. **Add intent extraction flow to app.py**. After transcription, call a new `extract_intent(transcript: str)` function that uses Foundry Local via the OpenAI SDK and alias resolution with `FoundryLocalManager` plus a tool-call schema.

1. **Constrain output via prompt only**. Encode all structural and date rules in the tool schema/prompt, including missing year/month rules, with no explicit sanitization or validation in code.

1. **Write intent output file**. Create `${yyyyMMddThhmmss}-intent.json` in `.work` containing only allowed keys.

1. **Log effective model alias**. Record the alias used for Foundry Local intent extraction in logs for traceability.

1. **Extend tests**. Add unit tests for intent prompt expectations, timestamp normalization outcomes, and filename formatting. Keep model invocation out of automated tests per Invocation Stewardship.

1. **Manual verification**. Run `uv run app.py` with a transcript that starts with “create a task …” and confirm output file content and naming.
