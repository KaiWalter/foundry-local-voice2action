import asyncio
import json
import re
from typing import Annotated, Any

from agent_framework import (
    ChatAgent,
    FunctionCallContent,
    FunctionResultContent,
    TextContent,
)
from agent_framework.openai import OpenAIChatClient
from foundry_local import FoundryLocalManager
from pydantic import Field

ALIAS = "qwen2.5-7b"

# Mock weather database (replace with real API in production)
WEATHER_DB = {
    "london": {"temp": 8, "condition": "Rainy", "humidity": 75, "wind": 12},
    "new york": {"temp": 12, "condition": "Cloudy", "humidity": 65, "wind": 8},
    "tokyo": {"temp": 18, "condition": "Clear", "humidity": 55, "wind": 5},
    "heilbronn": {"temp": 5, "condition": "Partly Cloudy", "humidity": 68, "wind": 10},
}


def _format_location(name: str) -> str:
    return name.strip().title()


def get_weather(
    location: Annotated[str, Field(description="City or location name (e.g., 'London', 'Tokyo')")],
) -> str:
    """Return current conditions for a supported location."""

    record = WEATHER_DB.get(location.lower().strip())
    pretty_name = _format_location(location)
    if not record:
        return f"Sorry, I do not have weather data for {pretty_name}."

    return (
        f"Current weather in {pretty_name}: {record['condition']} with a temperature of {record['temp']}°C, "
        f"humidity around {record['humidity']}% and winds near {record['wind']} km/h."
    )


def get_forecast(
    location: Annotated[str, Field(description="City or location name (e.g., 'London', 'Tokyo')")],
    days: Annotated[int, Field(description="Number of days to forecast (1-5)", ge=1, le=5)] = 3,
) -> str:
    """Return a simple multi-day outlook for a supported location."""

    record = WEATHER_DB.get(location.lower().strip())
    pretty_name = _format_location(location)
    if not record:
        return f"Sorry, I do not have forecast data for {pretty_name}."

    days = min(days, 5)
    outlook = []
    for idx in range(days):
        delta = idx - 1
        outlook.append(
            f"Day {idx + 1}: {(record['temp'] + delta):.0f}°C and {record['condition'].lower()} skies"
        )

    return f"Forecast for {pretty_name} (next {days} day{'s' if days > 1 else ''}):\n- " + "\n- ".join(outlook)


TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_forecast": get_forecast,
}


async def build_agent(alias: str) -> ChatAgent:
    print("🚀 Initializing Foundry Local via Agent Framework...")
    manager = FoundryLocalManager(alias)
    model_info = manager.get_model_info(alias)

    client = OpenAIChatClient(
        model_id=model_info.id,
        api_key=manager.api_key or "not-required",
        base_url=manager.endpoint,
    )

    print(f"✅ Loaded model: {model_info.id}")
    print(f"📍 Endpoint: {manager.endpoint}\n")

    agent = ChatAgent(
        chat_client=client,
        instructions=(
            "You are a weather assistant that MUST call the provided tools before"
            " answering. For every user request:"
            " 1) Call get_weather for the city they mention."
            " 2) Call get_forecast when they ask about future conditions."
            " When tools finish, ALWAYS send a final natural-language reply—never"
            " return raw tool call markup to the user. Never guess or use outside"
            " knowledge; only summarize the tool outputs in friendly prose."
        ),
        tools=[get_weather, get_forecast],
    )
    return agent


async def main() -> None:
    agent = await build_agent(ALIAS)

    queries = [
        "What's the weather like in London?",
        "Can you get the forecast for Tokyo?",
        "How's the weather in Heilbronn today?",
    ]

    for query in queries:
        print(f"👤 User: {query}")
        result = await agent.run(query)
        reply = _extract_text(result) or _fallback_from_query(query)
        if not reply:
            reply = "(assistant returned no text)"
        print(f"🤖 Agent: {reply}\n")


def _extract_text(result: Any) -> str:
    text_chunks: list[str] = []
    tool_chunks: list[str] = []
    calls: list[tuple[str, dict[str, Any]]] = []
    for message in getattr(result, "messages", []) or []:
        for content in getattr(message, "contents", []) or []:
            if isinstance(content, TextContent) and content.text:
                text_chunks.append(content.text)
                calls.extend(_parse_inline_tool_calls(content.text))
            elif isinstance(content, FunctionResultContent) and content.result is not None:
                if isinstance(content.result, str):
                    tool_chunks.append(content.result)
                else:
                    tool_chunks.append(json.dumps(content.result))
            elif isinstance(content, FunctionCallContent):
                try:
                    args = content.arguments
                    if isinstance(args, str):
                        args = json.loads(args)
                    calls.append((content.name, args or {}))
                except Exception:
                    continue
    if text_chunks:
        return _strip_tool_markup("\n".join(text_chunks))
    if tool_chunks:
        return "\n".join(tool_chunks)
    if calls:
        fallback: list[str] = []
        for name, args in calls:
            func = TOOL_REGISTRY.get(name)
            if not func:
                continue
            try:
                fallback.append(str(func(**args)))
            except Exception as exc:  # pragma: no cover - defensive
                fallback.append(f"{name} failed: {exc}")
        if fallback:
            return "\n".join(fallback)
    if getattr(result, "text", None):
        return _strip_tool_markup(result.text)
    return _strip_tool_markup(str(result))


_TOOL_TAG = re.compile(r"<tool_call[^>]*>.*?(?:</tool_call>|$)", flags=re.DOTALL)
_TOOL_PAREN = re.compile(r"\)\(\(\(.*?\)\)\)", flags=re.DOTALL)
_TOOL_BLOCK = re.compile(r"\(\(tool_call\)[\s\S]*?\)\)")
_INLINE_TOOL_CALL = re.compile(r"<tool_call[^>]*>\s*(\{.*?\})\s*(?:</tool_call>|$)", flags=re.DOTALL)
_INLINE_BLOCK_CALL = re.compile(r"\(\(tool_call\)\s*(\{.*?\})\s*\)\)", flags=re.DOTALL)


def _strip_tool_markup(text: str) -> str:
    cleaned = _TOOL_TAG.sub("", text)
    cleaned = _TOOL_PAREN.sub("", cleaned)
    cleaned = _TOOL_BLOCK.sub("", cleaned)
    return cleaned.strip()


def _parse_inline_tool_calls(text: str) -> list[tuple[str, dict[str, Any]]]:
    calls: list[tuple[str, dict[str, Any]]] = []
    for pattern in (_INLINE_TOOL_CALL, _INLINE_BLOCK_CALL):
        for match in pattern.finditer(text):
            try:
                payload = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
            name = payload.get("name")
            args = payload.get("arguments", {})
            if name:
                calls.append((name, args if isinstance(args, dict) else {}))
    return calls


def _fallback_from_query(query: str) -> str:
    lower = query.lower()
    location = next((name for name in WEATHER_DB if name in lower), None)
    if not location:
        return ""
    if any(keyword in lower for keyword in ("forecast", "next", "tomorrow")):
        return get_forecast(location)
    return get_weather(location)


if __name__ == "__main__":
    asyncio.run(main())
