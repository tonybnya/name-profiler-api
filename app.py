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
    """Root endpoint."""
    return {
        "message": "Welcome to Name Profiler API",
        "version": "v1.0.0",
        "author": "@tonybnya",
    }


if __name__ == "__main__":
    init_db()
    app.run(debug=DEBUG, host=HOST, port=PORT)
