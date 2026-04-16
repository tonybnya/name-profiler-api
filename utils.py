"""
Script Name : utils.py
Description : Helper functions
Author      : @tonybnya
"""

import requests
from uuid6 import uuid7
from datetime import datetime, timezone


def current_timestamp() -> str:
    """Generate ISO 8601 UTC timestamp.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_uuid_v7() -> str:
    return str(uuid7())


def classify_age(age: int) -> str:
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"


def fetch_nationality(name: str) -> dict[str, int | str]:
    NATIONALIZE_API_URL = "https://api.nationalize.io"

    r = requests.get(f"{NATIONALIZE_API_URL}?name={name}")
    data = r.json()

    countries = data.get("country", [])
    if not countries:
        raise Exception("Nationalize returned an invalid response")

    top = max(countries, key=lambda x: x["probability"])
    return top


def fetch_age(name: str) -> dict[str, int | str]:
    AGIFY_API_URL = "https://api.agify.io"

    r = requests.get(f"{AGIFY_API_URL}?name={name}")
    data = r.json()

    if data.get("age") is None:
        raise Exception("Agify returned an invalid response")

    return data


def fetch_gender(name):
    GENDERIZE_API_URL = "https://api.genderize.io"

    r = requests.get(f"{GENDERIZE_API_URL}?name={name}")
    data = r.json()

    if data.get("gender") is None or data.get("count") == 0:
        raise Exception("Genderize returned an invalid response")

    return data


def error_response(message: str, code: int) -> tuple[dict[str, str], int]:
    return {"status": "error", "message": message}, code
