# Copilot Instructions

## Context
- This repo is a minimal Voice-to-Action demo that runs entirely on-device using Microsoft Foundry Local and the OpenAI Python SDK.
- The only runtime entry point today is `app.py`, which demonstrates sending a single chat completion to the locally hosted Phi-4-Mini model alias.

## Key Files
- `app.py`: boots `FoundryLocalManager`, exposes the Foundry Local endpoint and API key, then calls `openai.OpenAI` with `chat.completions.create`.
- `pyproject.toml`: managed by uv; declares the `openai` and `foundry-local` dependencies plus Python 3.10+ requirement.
- `README.md`: documents that all runs/tests must go through `uv run ...` so agents inherit the uv-managed environment.

## Implementation Patterns
- Always obtain the base URL and API key from a `FoundryLocalManager` instance instead of hard-coding endpoints; the manager auto-starts the local service and downloads/loads the correct model.
- Fetch the concrete model ID via `manager.get_model_info(alias).id` before passing it to the OpenAI client; aliases resolve to versioned IDs that may change.
- Use OpenAI-compatible request objects (`messages`, `model`, etc.); Foundry Local mirrors the OpenAI REST contract, so standard SDK patterns apply.

## Workflows
- Installation/lock: `uv sync` (installs deps from `pyproject.toml`).
- Run the sample: `uv run app.py` (ensures Foundry Local service starts automatically via the manager).
- Extend into tests or scripts with `uv run <module>` to stay inside the same environment.

## Gotchas
- The API key returned by `FoundryLocalManager` can be blank for local usage, but still pass `manager.api_key` to satisfy the OpenAI client constructor.
- Large model downloads happen on first run; handle this latency by surfacing progress or caching models before tight loops.
- If you change the alias (e.g., `alias = "phi-4"`), ensure the target model is available locally or expect the manager to download it on demand.
