"""
Script Name : utils.py
Description : Helper functions
Author      : @tonybnya
"""

import requests
from uuid6 import uuid7
from datetime import datetime, timezone
from typing import Dict, Any
import sqlite3
import json

# APIs urls
GENDERIZE_API_URL = "https://api.genderize.io"
AGIFY_API_URL = "https://api.agify.io"
NATIONALIZE_API_URL = "https://api.nationalize.io"
REQUEST_TIMEOUT = 5  # seconds
DB = "profiles.db"
JSON_PATH = "seed_profiles.json"


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


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def _create_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE,
        gender TEXT,
        gender_probability REAL,
        age INTEGER,
        age_group TEXT,
        country_id TEXT,
        country_name TEXT,
        country_probability REAL,
        created_at TEXT DEFAULT (CURRENT_TIMESTAMP)
    )
    """)


def _upsert_profile(conn: sqlite3.Connection, p: Dict[str, Any]) -> None:
    sql = """
    INSERT INTO profiles (
        id, name, gender, gender_probability, age, age_group,
        country_id, country_name, country_probability, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
        gender = excluded.gender,
        gender_probability = excluded.gender_probability,
        age = excluded.age,
        age_group = excluded.age_group,
        country_id = excluded.country_id,
        country_name = excluded.country_name,
        country_probability = excluded.country_probability
    """
    conn.execute(sql, (
        generate_uuid_v7(),
        p.get("name"),
        p.get("gender"),
        p.get("gender_probability"),
        p.get("age"),
        p.get("age_group"),
        p.get("country_id"),
        p.get("country_name"),
        p.get("country_probability"),
        current_timestamp()
    ))


def load_profiles(path: str) -> list:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("profiles", [])


def seed(json_path: str = JSON_PATH, db_path: str = DB) -> None:
    conn = get_db()
    try:
        _create_table(conn)
        profiles = load_profiles(json_path)
        with conn:  # transaction
            for p in profiles:
                _upsert_profile(conn, p)
    finally:
        conn.close()
