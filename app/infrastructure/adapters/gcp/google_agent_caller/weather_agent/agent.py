"""Weather and Time Agent module.

This module provides an agent that can answer questions about weather and time
in various cities using Google ADK framework.
"""

import datetime
from zoneinfo import ZoneInfo

import requests
from google.adk.agents import Agent

# HACK: Disable IPv6 to avoid issues in certain environments.
requests.packages.urllib3.util.connection.HAS_IPV6 = False


def get_weather(city: str) -> dict:
    """Retrieve the current weather report for a specified city.

    Parameters
    ----------
    city : str
        The name of the city to get weather information for.

    Returns
    -------
    dict
        A dictionary containing weather information with the following keys:
        - 'status' : str
            Either 'success' or 'error' indicating the operation result.
        - 'report' : str
            Weather details if successful.
        - 'error_message' : str
            Error description if the operation failed.

    Examples
    --------
    >>> get_weather("New York")
    {'status': 'success', 'report': 'The weather in New York is sunny...'}

    >>> get_weather("Unknown City")
    {'status': 'error', 'error_message': "Weather information for..."}
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of "
                "25 degrees Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Return the current time in a specified city.

    Parameters
    ----------
    city : str
        The name of the city to get current time for.

    Returns
    -------
    dict
        A dictionary containing time information with the following keys:
        - 'status' : str
            Either 'success' or 'error' indicating the operation result.
        - 'report' : str
            Current time details if successful.
        - 'error_message' : str
            Error description if the operation failed.

    Examples
    --------
    >>> get_current_time("New York")
    {'status': 'success', 'report': 'The current time in New York is...'}

    >>> get_current_time("Unknown City")
    {'status': 'error', 'error_message': 'Sorry, I don't have timezone...'}
    """
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}."),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return {
        "status": "success",
        "report": (
            f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
        ),
    }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="I can answer your questions about the time and weather in a city.",
    tools=[get_weather, get_current_time],
)
