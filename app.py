import os
from pathlib import Path

import certifi
import requests
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI


os.environ["SSL_CERT_FILE"] = certifi.where()

project_dir = Path(__file__).resolve().parent
env_path = project_dir / ".env"
if not env_path.is_file():
    env_path = project_dir / "research" / ".env"
load_dotenv(env_path)


@tool
def get_weather_data(city: str) -> str:
    """Fetch current weather information for a city."""
    api_key = os.getenv("WEATHERSTACK_API_KEY")
    if not api_key:
        return "Weather lookup is unavailable: WEATHERSTACK_API_KEY is not configured."

    response = requests.get(
        "https://api.weatherstack.com/current",
        params={"access_key": api_key, "query": city},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    if "current" not in data:
        error = data.get("error", {}).get("info", "No current weather data returned.")
        return f"Could not fetch weather data for {city}: {error}"

    current = data["current"]
    descriptions = current.get("weather_descriptions") or ["Unknown"]
    return (
        f"City: {city}\n"
        f"Temperature: {current.get('temperature', 'Unknown')}°C\n"
        f"Weather: {descriptions[0]}\n"
        f"Humidity: {current.get('humidity', 'Unknown')}%"
    )


def create_agent_executor() -> AgentExecutor:
    """Build the search-and-weather agent using credentials from the environment."""
    missing_keys = [
        key
        for key in ("OPENAI_API_KEY", "TAVILY_API_KEY")
        if not os.getenv(key)
    ]
    if missing_keys:
        raise RuntimeError(
            "Missing required API key(s): "
            + ", ".join(missing_keys)
            + ". Add them to .env."
        )

    tools = [TavilySearchResults(max_results=3), get_weather_data]
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )


if __name__ == "__main__":
    agent_executor = create_agent_executor()
    response = agent_executor.invoke(
        {
            "input": (
                "Tell me the latest news on the Iran and US conflict, "
                "then tell me the current weather in Bengaluru."
            )
        }
    )
    print(response["output"])
