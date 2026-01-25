from openai import OpenAI
import json

from foundry_local import FoundryLocalManager


class ToolCall:

    @staticmethod
    def run():
        alias = "phi-4-mini"
        manager = FoundryLocalManager(alias)
        client = OpenAI(
            base_url=manager.endpoint,
            api_key=manager.api_key
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_typical_weather",
                    "description": "Get the typical weather for a specified city and date / time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco"
                            },
                            "datetime": {
                                "type": "string",
                                "description": "The date and time for which to get the typical weather in a format that can be parsed by datetime"
                            }
                        },
                        "required": ["city", "datetime"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_date_time",
                    "description": "Get the current date and time in a timezone.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "timeZone": {
                                "type": "string",
                                "description": "The timezone string (e.g., 'America/New_York', 'Europe/London')"
                            }
                        },
                        "required": ["timeZone"]
                    }
                }
            }
        ]

        # Create a running input list we will add to over time
        input_list = [
            {"role": "system", "content": "You are a helpful assistant with some tools. When you are mapping cities to timezones, ensure the timezone string is standard."},
            {"role": "user", "content": "What is the time and weather in Abudabi?"},
        ]

        def get_current_weather(city):
            return f"The weather in {city} is sunny with a high of 75°F."

        def get_typical_weather(city, datetime):
            from datetime import datetime as dt
            parsed_datetime = dt.fromisoformat(datetime.replace(
                'Z', '+00:00')) if 'Z' in datetime or '+' in datetime or '-' in datetime else dt.strptime(datetime, '%Y-%m-%d %H:%M:%S')
            return f"The typical weather at {datetime} in {city} is mild with occasional rain."

        def get_date_time(timeZone):
            from datetime import datetime
            import zoneinfo
            if not timeZone or timeZone == "":
                return datetime.now().strftime('%A, %B %d, %Y %I:%M:%S %p')
            try:
                tz = zoneinfo.ZoneInfo(timeZone)
                local_time = datetime.now(tz)
                return local_time.strftime('%A, %B %d, %Y %I:%M:%S %p')
            except Exception:
                return f"Invalid timezone: {timeZone}"

        get_tool = {
            'get_current_weather': get_current_weather,
            'get_typical_weather': get_typical_weather,
            'get_date_time': get_date_time,
        }

        # Prompt the model with tools defined
        require_tool = True
        final_response = None
        final_message = None

        while True:
            response = client.chat.completions.create(
                model=manager.get_model_info(alias).id,
                messages=input_list,
                tools=tools,
                tool_choice="required" if require_tool else "auto",
                stream=False
            )

            print(response.model_dump_json(indent=2))
            assistant_message = response.choices[0].message
            input_list.append(assistant_message.model_dump(exclude_none=True))

            tool_calls = assistant_message.tool_calls or []
            if not tool_calls:
                final_response = response
                final_message = assistant_message
                break

            require_tool = False

            # Execute the tool logic for each requested call
            for tool_call in tool_calls:
                tool_call_dict = tool_call if isinstance(
                    tool_call, dict) else tool_call.model_dump()
                tool_name = tool_call_dict["function"]["name"]
                tool_call_arguments = json.loads(
                    tool_call_dict["function"]["arguments"])

                if tool_name == "get_current_weather":
                    result = {tool_name: get_tool[tool_name](
                        tool_call_arguments["city"])}
                elif tool_name == "get_typical_weather":
                    result = {tool_name: get_tool[tool_name](
                        tool_call_arguments["city"], tool_call_arguments["datetime"])}
                elif tool_name == "get_date_time":
                    result = {tool_name: get_tool[tool_name](
                        tool_call_arguments["timeZone"])}
                else:
                    result = {tool_name: f"Unknown tool: {tool_name}"}

                input_list.append({
                    "role": "tool",
                    "tool_call_id": tool_call_dict["id"],
                    "content": json.dumps(result),
                })

        print("Final input:")
        for row in input_list:
            print(json.dumps(row, indent=2))

        # The model's response
        print("Final output:")
        if final_response is not None:
            print(final_response.model_dump_json(indent=2))
        if final_message is not None:
            print("\n" + (final_message.content or ""))
        else:
            print("\nNo final response message available.")


if __name__ == "__main__":
    ToolCall.run()
