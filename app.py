"""
Script Name : app.py
Description : Flask application with endpoints
Author      : @tonybnya
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import (
    error_response,
    get_db,
    _create_table,
    seed,
    DB,
    JSON_PATH
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Config constants
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))


# Init DB on cold start (idempotent)
with get_db() as conn:
    _create_table(conn)

# Optionally seed once on cold start
# safe: upsert prevents duplicates
try:
    seed(JSON_PATH, DB)
except FileNotFoundError:
    # no seed file present — skip without failing startup
    pass


@app.route("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Name Profiler API",
        "version": "v1.0.0",
        "author": "@tonybnya",
    }


@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    """Get All Profiles with filtering, sorting, and pagination."""
    # Define valid parameters
    valid_params = {
        "gender", "age_group", "country_id",
        "min_age", "max_age",
        "min_gender_probability", "min_country_probability",
        "sort_by", "order", "page", "limit"
    }
    
    # Check for unrecognized parameters
    for param in request.args.keys():
        if param not in valid_params:
            return error_response("Invalid query parameters", 400)
    
    # Get filter parameters
    gender = request.args.get("gender")
    age_group = request.args.get("age_group")
    country_id = request.args.get("country_id")
    
    # Validate min_age (must be non-negative integer)
    min_age = request.args.get("min_age")
    if min_age is not None:
        try:
            min_age = int(min_age)
            if min_age < 0:
                return error_response("Invalid query parameters", 422)
        except ValueError:
            return error_response("Invalid query parameters", 422)
    else:
        min_age = None
    
    # Validate max_age (must be non-negative integer)
    max_age = request.args.get("max_age")
    if max_age is not None:
        try:
            max_age = int(max_age)
            if max_age < 0:
                return error_response("Invalid query parameters", 422)
        except ValueError:
            return error_response("Invalid query parameters", 422)
    else:
        max_age = None
    
    # Validate min_age <= max_age
    if min_age is not None and max_age is not None and min_age > max_age:
        return error_response("Invalid query parameters", 422)
    
    # Validate min_gender_probability (must be 0.0 to 1.0)
    min_gender_probability = request.args.get("min_gender_probability")
    if min_gender_probability is not None:
        try:
            min_gender_probability = float(min_gender_probability)
            if min_gender_probability < 0.0 or min_gender_probability > 1.0:
                return error_response("Invalid query parameters", 422)
        except ValueError:
            return error_response("Invalid query parameters", 422)
    else:
        min_gender_probability = None
    
    # Validate min_country_probability (must be 0.0 to 1.0)
    min_country_probability = request.args.get("min_country_probability")
    if min_country_probability is not None:
        try:
            min_country_probability = float(min_country_probability)
            if min_country_probability < 0.0 or min_country_probability > 1.0:
                return error_response("Invalid query parameters", 422)
        except ValueError:
            return error_response("Invalid query parameters", 422)
    else:
        min_country_probability = None
    
    # Validate sort_by (must be one of valid columns)
    sort_by = request.args.get("sort_by", "created_at")
    valid_sort_columns = ["age", "created_at", "gender_probability"]
    if sort_by not in valid_sort_columns:
        return error_response("Invalid query parameters", 422)
    
    # Validate order (must be asc or desc)
    order = request.args.get("order", "desc")
    if order.lower() not in ["asc", "desc"]:
        return error_response("Invalid query parameters", 422)
    order = order.upper()
    
    # Validate page (must be positive integer)
    page = request.args.get("page", "1")
    try:
        page = int(page)
        if page < 1:
            return error_response("Invalid query parameters", 422)
    except ValueError:
        return error_response("Invalid query parameters", 422)
    
    # Validate limit (must be integer 1-50)
    limit = request.args.get("limit", "10")
    try:
        limit = int(limit)
        if limit < 1 or limit > 50:
            return error_response("Invalid query parameters", 422)
    except ValueError:
        return error_response("Invalid query parameters", 422)
    
    # Build base query
    query = "SELECT * FROM profiles WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM profiles WHERE 1=1"
    params = []
    
    # Apply filters (case-insensitive)
    if gender:
        query += " AND LOWER(gender) = ?"
        count_query += " AND LOWER(gender) = ?"
        params.append(gender.lower())
    
    if age_group:
        query += " AND LOWER(age_group) = ?"
        count_query += " AND LOWER(age_group) = ?"
        params.append(age_group.lower())
    
    # Validate country_id exists in database
    if country_id:
        country_id_upper = country_id.upper()
        conn = get_db()
        existing_country = conn.execute(
            "SELECT 1 FROM profiles WHERE country_id = ? LIMIT 1",
            (country_id_upper,)
        ).fetchone()
        if not existing_country:
            return error_response("Invalid query parameters", 422)
        query += " AND country_id = ?"
        count_query += " AND country_id = ?"
        params.append(country_id_upper)
    
    if min_age is not None:
        query += " AND age >= ?"
        count_query += " AND age >= ?"
        params.append(min_age)
    
    if max_age is not None:
        query += " AND age <= ?"
        count_query += " AND age <= ?"
        params.append(max_age)
    
    if min_gender_probability is not None:
        query += " AND gender_probability >= ?"
        count_query += " AND gender_probability >= ?"
        params.append(min_gender_probability)
    
    if min_country_probability is not None:
        query += " AND country_probability >= ?"
        count_query += " AND country_probability >= ?"
        params.append(min_country_probability)
    
    # Apply sorting
    query += f" ORDER BY {sort_by} {order}"
    
    # Get total count before pagination
    conn = get_db()
    total_result = conn.execute(count_query, params).fetchone()
    total = total_result["total"] if total_result else 0
    
    # Apply pagination
    offset = (page - 1) * limit
    query += " LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)
    
    # Execute query
    rows = conn.execute(query, params).fetchall()
    
    return jsonify({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [dict(r) for r in rows]
    })


@app.route("/api/profiles/<id>", methods=["GET"])
def get_profile(id: str):
    """Get Single Profile."""
    conn = get_db()
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (id,)).fetchone()
    
    if not row:
        return error_response("Profile not found", 404)
    
    return jsonify({"status": "success", "data": dict(row)})


@app.route("/api/profiles/<id>", methods=["DELETE"])
def delete_profile(id: str):
    """Delete Profile."""
    conn = get_db()
    cur = conn.execute("DELETE FROM profiles WHERE id = ?", (id,))
    
    if cur.rowcount == 0:
        return error_response("Profile not found", 404)
    
    conn.commit()
    return "", 204


# Commented endpoints for future implementation:
# @app.route("/api/profiles", methods=["POST"])
# def create_profile():
#     pass
#     with get_db() as conn:
#         conn.execute("""
#         CREATE TABLE IF NOT EXISTS profiles (
#             id TEXT PRIMARY KEY,
#             name TEXT UNIQUE,
#             gender TEXT,
#             gender_probability REAL,
#             sample_size INTEGER,
#             age INTEGER,
#             age_group TEXT,
#             country_id TEXT,
#             country_probability REAL,
#             created_at TEXT
#         )
#         """)
#
#
# # Initialize database on module load (required for Vercel serverless)
# init_db()
#
#
# @app.route("/")
# def root():
#     """Root endpoint."""
#     return {
#         "message": "Welcome to Name Profiler API",
#         "version": "v1.0.0",
#         "author": "@tonybnya",
#     }
#
#
# @app.route("/api/profiles", methods=["POST"])
# def create_profile():
#     """Create Profile."""
#     data = request.get_json()
#
#     if not data or "name" not in data:
#         return error_response("Missing or empty name", 400)
#
#     name = data["name"].strip().lower()
#     if not name:
#         return error_response("Missing or empty name", 400)
#
#     conn = get_db()
#     existing = conn.execute("SELECT * FROM profiles WHERE name = ?", (name,)).fetchone()
#
#     if existing:
#         return jsonify(
#             {
#                 "status": "success",
#                 "message": "Profile already exists",
#                 "data": dict(existing),
#             }
#         ), 200
#
#     try:
#         gender = fetch_gender(name)
#         age = fetch_age(name)
#         nationality = fetch_nationality(name)
#     except Exception as e:
#         return error_response(str(e), 502)
#
#     profile_id = generate_uuid_v7()
#     created_at = current_timestamp()
#
#     age_group = classify_age_group(age["age"])
#
#     conn.execute(
#         """
#         INSERT INTO profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """,
#         (
#             profile_id,
#             name,
#             gender["gender"],
#             gender["probability"],
#             gender["count"],
#             age["age"],
#             age_group,
#             nationality["country_id"],
#             nationality["probability"],
#             created_at,
#         ),
#     )
#     conn.commit()
#
#     return jsonify(
#         {
#             "status": "success",
#             "data": {
#                 "id": profile_id,
#                 "name": name,
#                 "gender": gender["gender"],
#                 "gender_probability": gender["probability"],
#                 "sample_size": gender["count"],
#                 "age": age["age"],
#                 "age_group": age_group,
#                 "country_id": nationality["country_id"],
#                 "country_probability": nationality["probability"],
#                 "created_at": created_at,
#             },
#         }
#     ), 201
#
#
# @app.route("/api/profiles", methods=["GET"])
# def get_profiles():
#     """Get All Profiles."""
#     gender = request.args.get("gender")
#     country_id = request.args.get("country_id")
#     age_group = request.args.get("age_group")
#
#     query = (
#         "SELECT id, name, gender, age, age_group, country_id FROM profiles WHERE 1=1"
#     )
#     params = []
#
#     if gender:
#         query += " AND LOWER(gender) = ?"
#         params.append(gender.lower())
#     if country_id:
#         query += " AND LOWER(country_id) = ?"
#         params.append(country_id.lower())
#     if age_group:
#         query += " AND LOWER(age_group) = ?"
#         params.append(age_group.lower())
#
#     conn = get_db()
#     rows = conn.execute(query, params).fetchall()
#
#     return jsonify(
#         {"status": "success", "count": len(rows), "data": [dict(r) for r in rows]}
#     )
#
#
# @app.route("/api/profiles/<id>", methods=["GET"])
# def get_profile(id: str):
#     """Get Single Profile."""
#     conn = get_db()
#     row = conn.execute("SELECT * FROM profiles WHERE id = ?", (id,)).fetchone()
#
#     if not row:
#         return error_response("Profile not found", 404)
#
#     return jsonify({"status": "success", "data": dict(row)})
#
#
# @app.route("/api/profiles/<id>", methods=["DELETE"])
# def delete_profile(id: str):
#     """Delete Profile."""
#     conn = get_db()
#     cur = conn.execute("DELETE FROM profiles WHERE id = ?", (id,))
#
#     if cur.rowcount == 0:
#         return error_response("Profile not found", 404)
#
#     conn.commit()
#     return "", 204


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
