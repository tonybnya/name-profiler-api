"""
Script Name : app.py
Description : Flask application with endpoints
Author      : @tonybnya
"""

import os

import requests
import sqlite3
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import (
    classify_age_group,
    current_timestamp,
    error_response,
    fetch_age,
    fetch_gender,
    fetch_nationality,
    generate_uuid_v7,
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
DB = "profiles.db"

# Config constants
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE,
            gender TEXT,
            gender_probability REAL,
            sample_size INTEGER,
            age INTEGER,
            age_group TEXT,
            country_id TEXT,
            country_probability REAL,
            created_at TEXT
        )
        """)


@app.route("/")
def root():
    """Root endpoint.
    """
    return {
        "message": "Welcome to Name Profiler API",
        "version": "v1.0.0",
        "author": "@tonybnya",
    }


@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    """Get All Profiles.
    """
    gender = request.args.get("gender")
    country_id = request.args.get("country_id")
    age_group = request.args.get("age_group")

    query = "SELECT id, name, gender, age, age_group, country_id FROM profiles WHERE 1=1"
    params = []

    if gender:
        query += " AND LOWER(gender) = ?"
        params.append(gender.lower())
    if country_id:
        query += " AND LOWER(country_id) = ?"
        params.append(country_id.lower())
    if age_group:
        query += " AND LOWER(age_group) = ?"
        params.append(age_group.lower())

    conn = get_db()
    rows = conn.execute(query, params).fetchall()

    return jsonify({
        "status": "success",
        "count": len(rows),
        "data": [dict(r) for r in rows]
    })


@app.route("/api/profiles/<id>", methods=["GET"])
def get_profile(id: str):
    """Get Single Profile.
    """
    conn = get_db()
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (id,)).fetchone()

    if not row:
        return error_response("Profile not found", 404)

    return jsonify({
        "status": "success",
        "data": dict(row)
    })


@app.route("/api/profiles/<id>", methods=["DELETE"])
def delete_profile(id: str):
    """Delete Profile.
    """
    conn = get_db()
    cur = conn.execute("DELETE FROM profiles WHERE id = ?", (id,))

    if cur.rowcount == 0:
        return error_response("Profile not found", 404)

    conn.commit()
    return "", 204



if __name__ == "__main__":
    init_db()
    app.run(debug=DEBUG, host=HOST, port=PORT)
