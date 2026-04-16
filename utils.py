"""
Script Name : utils.py
Description : Helper functions
Author      : @tonybnya
"""

import requests
from uuid6 import uuid7
from datetime import datetime, timezone

# APIs urls
GENDERIZE_API_URL = "https://api.genderize.io"
AGIFY_API_URL = "https://api.agify.io"
NATIONALIZE_API_URL = "https://api.nationalize.io"
REQUEST_TIMEOUT = 5  # seconds


def classify_age_group(age: int) -> str:
    """Classify age group from Agify API.
    """
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"


def current_timestamp() -> str:
    """Generate ISO 8601 UTC timestamp.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def error_response(message: str, code: int) -> tuple[dict[str, str], int]:
    """Build the response error structure.
    """
    return {"status": "error", "message": message}, code


def fetch_age(name: str) -> dict[str, int | str]:
    """ Fetch data from the Agify API.
    """
    # Call Agify API
    response = requests.get(
        AGIFY_API_URL, params={"name": name}, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if data.get("age") is None:
        raise Exception("Agify returned an invalid response")

    return data


def fetch_gender(name):
    """Fetch data from the Genderize API.
    """
    # Call Genderize API
    response = requests.get(
        GENDERIZE_API_URL, params={"name": name}, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if data.get("gender") is None or data.get("count") == 0:
        raise Exception("Genderize returned an invalid response")

    return data


def fetch_nationality(name: str) -> dict[str, int | str]:
    """Pick the country with the highest probability from the Nationalize API.
    """
    # Call Nationalize API
    response = requests.get(
        NATIONALIZE_API_URL, params={"name": name}, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    countries = data.get("country", [])
    if not countries:
        raise Exception("Nationalize returned an invalid response")

    top = max(countries, key=lambda x: x["probability"])
    return top


def generate_uuid_v7() -> str:
    """Generate UUID v7.
    """
    return str(uuid7())
