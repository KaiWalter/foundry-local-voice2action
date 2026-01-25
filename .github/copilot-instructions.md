# Copilot Instructions

## Context
- Minimal Voice-to-Action prototype that runs entirely on-device via Foundry Local, exposing a Phi-4-Mini alias and interacting through the OpenAI Python SDK.
- The demo is a single CLI script ([app.py](../app.py)) that exercises OpenAI-style tool calling against the local model endpoint.
- Project is uv-managed; Python requirement is ≥3.14 per [pyproject.toml](../pyproject.toml).

## Key Files & Entry Points
- [app.py](../app.py): defines the `ToolCall` class, boots `FoundryLocalManager`, configures `openai.OpenAI`, and drives a multi-turn chat completion loop with tool invocation.
- [pyproject.toml](../pyproject.toml): lists runtime deps (`openai`, `foundry-local-sdk`); any new scripts must stay compatible with uv’s lock/resolution.
- [README.md](../README.md): states the uv-first workflow—every run/test should use `uv run …` so the Foundry Local manager hooks fire correctly.

## Core Flow (app.py)
- Always resolve the model dynamically: `manager = FoundryLocalManager(alias)` followed by `manager.get_model_info(alias).id`; never hard-code IDs because aliases map to versioned builds.
- The OpenAI client must point to the local service: `OpenAI(base_url=manager.endpoint, api_key=manager.api_key)` even when the key is blank.
- Tool calling loop: first request forces `tool_choice="required"`, later turns fall back to `"auto"`; helper functions (`get_current_weather`, etc.) append tool responses with a `tool_call_id` so the model can continue the conversation.
- Messages are accumulated in `input_list` exactly as the OpenAI REST contract expects (assistant/tool pairs). Preserve this structure when extending scenarios (e.g., adding new tools or user prompts).

## Local Workflows
- Install/refresh deps: `uv sync` (runs lock + install respecting [pyproject.toml](../pyproject.toml)).
- Run the demo: `uv run app.py`; this auto-starts Foundry Local, downloads models on first use, and prints both intermediate tool-call payloads and the final assistant reply.
- New command-line scripts should also be invoked via `uv run <script.py>` so they inherit the same virtual env and Foundry Local availability.

## Conventions & Gotchas
- Reuse the module-level helpers in [app.py](../app.py) when adding tools so every tool result is JSON-serialized and tagged with the originating `tool_call_id`.
- The mock tool implementations currently return canned strings—if you swap in real APIs, keep latency in mind because Foundry Local may still be downloading models on first run.
- Local API key can be empty, but the OpenAI client still requires the parameter; do not omit it.
- If you change the alias (`alias = "phi-4-mini"` today), expect Foundry Local to download the new weights; surface that latency to users as needed.
- Because Python ≥3.14 is enforced, avoid syntax/features that rely on older versions; let uv manage interpreter selection.

## Extending
- To add more user interactions, push additional `{ "role": "user", ... }` entries into `input_list` rather than restarting the manager—this ensures multi-turn parity with OpenAI’s tools contract.
- When adding new dependencies, edit [pyproject.toml](../pyproject.toml) then rerun `uv sync`; avoid `pip install` directly to keep the lock consistent.
