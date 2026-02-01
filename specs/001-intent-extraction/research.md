# Research Findings: Intent Extraction Output

## Decision 1: Use OpenAI SDK with Foundry Local (no Agent Framework)

- **Decision**: Invoke Foundry Local via the OpenAI SDK directly, resolving the model ID from an alias and pointing the client to the local endpoint.
- **Rationale**: Keeps the dependency surface minimal and aligns with the existing low-level sample and project guidance.
- **Alternatives considered**: Agent Framework `ChatAgent` orchestration; rejected due to extra abstraction for a single-call workflow.

## Decision 2: Use tool calling to enforce JSON schema

- **Decision**: Define a single tool (e.g., `emit_intent`) and require the model to respond via tool calling with a JSON schema that only allows `intent`, `content`, `due`, and `reminder`.
- **Rationale**: Structured arguments reduce parsing errors and prevent extra keys in the output.
- **Alternatives considered**: “JSON-only” natural language responses; rejected due to higher parsing/validation risk.

## Decision 3: Use prompt-only constraints for output structure

- **Decision**: Do not apply explicit sanitization or validation in code; instead, constrain the model output solely through a strict prompt and tool schema.
- **Rationale**: The feature request requires that all structural constraints be enforced through the prompt only.
- **Alternatives considered**: Post-processing/sanitization in code; rejected due to requirement to avoid explicit sanitization.

## Decision 4: Treat model invocation as manual verification

- **Decision**: Mark the Foundry Local model invocation as manual verification per the constitution.
- **Rationale**: Model runtime is an external dependency; automated tests should not mock or assert the full invocation flow.
- **Alternatives considered**: Fully mocked model invocations; rejected by Invocation Stewardship requirements.
