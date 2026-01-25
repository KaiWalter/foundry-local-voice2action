import asyncio
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from foundry_local import FoundryLocalManager
from pydantic import Field

ALIAS = "phi-3.5-mini"

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
            " Never guess or use outside knowledge—only summarize tool outputs in"
            " friendly prose once all requested data has been gathered."
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
        reply = result.text or str(result)
        print(f"🤖 Agent: {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())
