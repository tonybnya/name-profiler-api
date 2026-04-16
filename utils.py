"""
Script Name : utils.py
Description : Helper functions
Author      : @tonybnya
"""

import requests
from uuid6 import uuid7


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


def fetch_nationality(name: str, nationalize_api_url: str) -> dict[str, int | str]:
    r = requests.get(f"{nationalize_api_url}?name={name}")
    data = r.json()

    countries = data.get("country", [])
    if not countries:
        raise Exception("Nationalize returned an invalid response")

    top = max(countries, key=lambda x: x["probability"])
    return top
