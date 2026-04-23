# Name Profiler API - Data Persistence & API Design Assessment

A Flask REST API that profiles names by fetching demographic data from external APIs (Genderize.io, Agify.io, Nationalize.io). Returns structured responses with demographic insights and stores results in SQLite.

## Features

- **Multi-source data aggregation**: Fetches gender, age, and nationality from 3 external APIs
- **Full CRUD operations**: Create, read (list & single), and delete profile records
- **CORS enabled**: Accessible from any origin
- **Advanced filtering**: Filter profiles by gender, country_id, age_group, min/max age, min probabilities
- **Sorting & Pagination**: Sort by age, created_at, or gender_probability with pagination support
- **Query validation**: Comprehensive validation with 400/422 error responses
- **Natural language search**: Search profiles using plain English queries
- **Error handling**: 400, 404, 502 error responses with structured messages
- **Data persistence**: SQLite database with UUID v7 identifiers
- **Age classification**: Automatic categorization (child/teenager/adult/senior)
- **Deployed on Vercel**: Serverless deployment with automatic scaling

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root info |
| POST | `/api/profiles` | Create profile (fetches external data) |
| GET | `/api/profiles` | List profiles with filtering, sorting, and pagination |
| GET | `/api/profiles/search` | Natural language search |
| GET | `/api/profiles/<id>` | Get single profile by UUID |
| DELETE | `/api/profiles/<id>` | Delete profile by UUID |

### POST /api/profiles

Create a new profile by providing a name. The API fetches data from external services and stores the result.

**Request Body:**
```json
{
  "name": "tony"
}
```

**Success Response (201 CREATED):**
```json
{
  "status": "success",
  "data": {
    "id": "018f3e4a-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
    "name": "tony",
    "gender": "male",
    "gender_probability": 0.99,
    "sample_size": 752575,
    "age": 54,
    "age_group": "adult",
    "country_id": "US",
    "country_probability": 0.2,
    "created_at": "2026-04-17T15:30:45Z"
  }
}
```

**Error Response (400 BAD REQUEST):**
```json
{
  "status": "error",
  "message": "Missing or empty name"
}
```

### GET /api/profiles

List all profiles with advanced filtering, sorting, and pagination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `gender` | string | Filter by gender ("male", "female") |
| `country_id` | string | Filter by country code ("US", "FR", "NG") |
| `age_group` | string | Filter by age category ("child", "teenager", "adult", "senior") |
| `min_age` | integer | Minimum age |
| `max_age` | integer | Maximum age |
| `min_gender_probability` | float | Minimum gender probability (0.0-1.0) |
| `min_country_probability` | float | Minimum country probability (0.0-1.0) |
| `sort_by` | string | Sort by: "age", "created_at", "gender_probability" (default: "created_at") |
| `order` | string | Sort order: "asc" or "desc" (default: "desc") |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page, max 50 (default: 10) |

**Success Response (200 OK):**
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 2026,
  "data": [
    {
      "id": "018f3e4a-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
      "name": "tony",
      "gender": "male",
      "gender_probability": 0.99,
      "age": 54,
      "age_group": "adult",
      "country_id": "US",
      "country_name": "United States",
      "country_probability": 0.2,
      "created_at": "2026-04-17T15:30:45Z"
    }
  ]
}
```

**Error Response (422 UNPROCESSABLE ENTITY):**
```json
{
  "status": "error",
  "message": "Invalid query parameters"
}
```

### GET /api/profiles/search

Search profiles using natural language queries. Supports filtering, sorting, and pagination.

**Query Parameters:**
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `q` | Yes | - | Natural language query string |
| `page` | No | 1 | Page number |
| `limit` | No | 10 | Items per page (max 50) |

**Example Queries:**
- `young males` → gender=male, min_age=16, max_age=24
- `females above 30` → gender=female, min_age=30
- `from nigeria or ghana` → country_id=["NG", "GH"]
- `adult males from kenya` → gender=male, age_group=adult, country_id="KE"
- `people aged 25` → min_age=25, max_age=25

**Success Response (200 OK):**
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 129,
  "data": [
    {
      "id": "018f3e4a-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
      "name": "Hassan Girma",
      "gender": "male",
      "age": 37,
      "age_group": "adult",
      "country_id": "UG",
      "country_name": "Uganda",
      "created_at": "2026-04-17T15:30:45Z"
    }
  ]
}
```

**Error Response (422 UNPROCESSABLE ENTITY):**
```json
{
  "status": "error",
  "message": "Unable to interpret query"
}
```

### GET /api/profiles/{id}

Retrieve a single profile by its UUID.

**Success Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "018f3e4a-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
    "name": "tony",
    "gender": "male",
    "gender_probability": 0.99,
    "sample_size": 752575,
    "age": 54,
    "age_group": "adult",
    "country_id": "US",
    "country_probability": 0.2,
    "created_at": "2026-04-17T15:30:45Z"
  }
}
```

**Error Response (404 NOT FOUND):**
```json
{
  "status": "error",
  "message": "Profile not found"
}
```

### DELETE /api/profiles/{id}

Delete a profile by its UUID.

**Success Response (204 NO CONTENT):** Empty body

**Error Response (404 NOT FOUND):**
```json
{
  "status": "error",
  "message": "Profile not found"
}
```

## Data Processing Rules

1. **External API Calls** (parallel, 5-second timeout each):
   - **Genderize.io**: Returns `gender`, `probability`, `count`
   - **Agify.io**: Returns `age`
   - **Nationalize.io**: Returns array of countries, pick highest probability

2. **Age Classification**:
   - `child`: age ≤ 12
   - `teenager`: age ≤ 19
   - `adult`: age ≤ 59
   - `senior`: age > 59

3. **Name Normalization**:
   - Strip whitespace
   - Convert to lowercase before storage and query

4. **Duplicate Prevention**:
   - Names stored with UNIQUE constraint
   - Returns existing profile with message if duplicate

5. **Timestamp**:
   - `created_at` generated in UTC ISO 8601 format for every new profile

6. **UUID Generation**:
   - Uses UUID v7 (uuid6 library) for profile identifiers

## Error Responses

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Missing or empty parameter | "Missing or empty name" / "Missing query parameter" |
| 422 | Invalid parameter type or value | "Invalid query parameters" / "Unable to interpret query" |
| 404 | Profile not found by ID | "Profile not found" |
| 502 | External API timeout or invalid response | "Agify/Nationalize/Genderize returned an invalid response" |
| 500 | Server error | "Server error: {details}" |

All errors follow this structure:
```json
{
  "status": "error",
  "message": "<error message>"
}
```

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js (optional, for Vercel CLI)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/tonybnya/name-profiler-api
cd name-profiler-api
```

2. Install dependencies:
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

## Usage

### Start the Server (Local Development)

```bash
uv run python app.py
```

The server starts on `http://localhost:5000` (or PORT from env)

### Tests

#### Using curl (Local)

```bash
# Create a profile
curl -X POST http://localhost:5000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "tony"}'

# List all profiles with pagination
curl "http://localhost:5000/api/profiles?page=1&limit=5"

# Filter profiles
curl "http://localhost:5000/api/profiles?gender=male&min_age=25&sort_by=age&order=desc"

# Natural language search
curl "http://localhost:5000/api/profiles/search?q=young%20males%20from%20nigeria"

# Get single profile (replace {id} with actual UUID)
curl http://localhost:5000/api/profiles/{id}

# Delete a profile
curl -X DELETE http://localhost:5000/api/profiles/{id}
```

#### Error Cases

```bash
# Missing name in request body
curl -X POST http://localhost:5000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{}'
# Returns: 400 BAD REQUEST

# Invalid query parameter
curl "http://localhost:5000/api/profiles?foo=bar"
# Returns: 400 BAD REQUEST

# Profile not found
curl http://localhost:5000/api/profiles/nonexistent-id
# Returns: 404 NOT FOUND

# Duplicate name (returns existing profile)
curl -X POST http://localhost:5000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "tony"}'
curl -X POST http://localhost:5000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "tony"}'
# Returns: 200 OK with existing profile
```

## Project Structure

```
name-profiler-api/
├── api/                      # Vercel serverless entry point
│   ├── __init__.py
│   └── index.py             # ASGI adapter for Vercel (WsgiToAsgi)
├── app.py                   # Flask application with endpoints
├── utils.py                 # External API clients + helper functions
├── search_parser.py         # Natural language query parser
├── profiles.db              # SQLite database (auto-created)
├── seed_profiles.json       # Seed data for database
├── requirements.txt         # Python dependencies (generated)
├── pyproject.toml           # uv project configuration
├── uv.lock                  # uv lock file
├── .python-version          # Python version specifier
├── .env                     # Local environment variables
├── .env.example             # Environment template
├── .gitignore
└── README.md
```

## Deployment

### Deploy on Vercel

This API is configured for serverless deployment on Vercel.

#### Prerequisites

- Vercel CLI: `npm i -g vercel`
- Vercel account (free tier available)

#### Deploy

```bash
# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

#### Environment Variables

Set environment variables in Vercel dashboard or CLI:

```bash
vercel env add PORT
vercel env add DEBUG
```

**Note**: The SQLite database on Vercel is ephemeral (resets on each deployment). For persistent storage, consider migrating to a managed database service.

### Deploy on Other Platforms

The project can be containerized for deployment on platforms like:

- Fly.io
- Railway
- Google Cloud Run
- AWS Lambda

Create a `Dockerfile` if needed for containerized deployment:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Dependencies

```bash
# Sync dependencies from lockfile
uv sync

# Export to requirements.txt
uv export --format requirements-txt -o requirements.txt

# Add new dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>
```

## Testing

No test suite configured. Add tests with pytest if extending:

```bash
uv add --dev pytest
uv run pytest
```

## License

Copyright © [2026] [@tonybnya]
