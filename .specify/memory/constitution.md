<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.1
- Modified principles: Invocation Stewardship (clarified non-testable invocation scope)
- Added sections: Operational Constraints, Development Workflow
- Removed sections: None
- Templates requiring updates: ✅ .specify/templates/plan-template.md, ✅ .specify/templates/spec-template.md, ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->
# foundry-local-voice2action Constitution

## Core Principles

### I. Testable Application Logic

Everything that bears application logic, from reusable helpers through flow orchestration, MUST be accompanied by repeatable, automated verification. Tests should be sufficiently isolated so that logic can be reproduced without wired-in invocations, and they must live alongside the code they cover.

### II. Invocation Stewardship

Any change that involves invoking framework components, AI models, Foundry services, CLI tooling, or external runtimes is currently NOT testable and must NOT be mocked. These flows are treated as manual verification steps with clear success criteria. Invocations are documented, observable, and retried manually but are never treated as automated assertions until tooling matures.

### III. Python + uv First Flow

Python (>=3.14) under uv is the only approved runtime; every script and test must run via `uv run …` so environment setup and dependency resolution stay centralized. Use the uv-managed interpreter for experiments, linting, and assertions rather than invoking bare Python executables.

### IV. Local-first Runtime Flow

The project lives entirely on-device: favor Foundry Local-managed models, keep dependencies minimal, and shadow cloud-only APIs with mock data or sample helpers. Leverage the small sample scripts as the canonical pattern for any new tooling that exercises the model.

### V. Reference Implementations & Documentation

Sample-agent-framework.py and sample-transcribe.py serve as the ground truth for how agent-driven tool calling and Whisper transcription should behave; consult them before adding features or refactors and document any deviations in prose that cites those samples.

## Operational Constraints

Application logic must stay testable, but anything that touches framework components, AI models, or other invocations must remain manual and unmocked until tooling matures. These flows need a manual verification checklist and explicit notes on why they cannot yet be automated. Keep the runtime stack pinned to Python/uv in documentation, and flag any tooling that requires external services so reviewers know it is part of the manual-verification bucket.

## Development Workflow

Plan, specification, and task artifacts honor these principles by embedding test requirements, calling out manual invocations, and directing contributors to the canonical samples. Every pull request must cite the relevant sample script, describe how its logic is verified, and enumerate any manual invocation steps with their expected observations.

## Governance

This constitution is the authoritative source for development expectations. Amendments require at least one maintainer approval and an explicit migration plan that highlights how the new principle will be enforced in downstream templates.

**Version**: 1.0.1 | **Ratified**: 2026-01-31 | **Last Amended**: 2026-01-31
