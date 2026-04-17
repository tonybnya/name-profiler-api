# Name Profiler API - Data Persistence & API Design Assessment

A Flask REST API that profiles names by fetching demographic data from external APIs (Genderize.io, Agify.io, Nationalize.io). Returns structured responses with demographic insights and stores results in SQLite.

## Features

- **Multi-source data aggregation**: Fetches gender, age, and nationality from 3 external APIs
- **Full CRUD operations**: Create, read (list & single), and delete profile records
- **CORS enabled**: Accessible from any origin
- **Filtering support**: Filter profiles by gender, country_id, or age_group
- **Error handling**: 400, 404, 502 error responses with structured messages
- **Data persistence**: SQLite database with UUID v7 identifiers
- **Age classification**: Automatic categorization (child/teenager/adult/senior)
- **Deployed on Vercel**: Serverless deployment with automatic scaling

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root info |
| POST | `/api/profiles` | Create profile (fetches external data) |
| GET | `/api/profiles` | List profiles with optional filters |
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

List all profiles with optional filtering.

**Query Parameters:**
- `gender` - Filter by gender (e.g., "male", "female")
- `country_id` - Filter by country code (e.g., "US", "FR")
- `age_group` - Filter by age category ("child", "teenager", "adult", "senior")

**Success Response (200 OK):**
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "id": "018f3e4a-5b6c-7d8e-9f0a-1b2c3d4e5f6a",
      "name": "tony",
      "gender": "male",
      "age": 54,
      "age_group": "adult",
      "country_id": "US"
    },
    ...
  ]
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
| 400 | Missing or empty name in POST body | "Missing or empty name" |
| 404 | Profile not found by ID | "Profile not found" |
| 502 | External API timeout | "Upstream API request timed out" (or wrapped in exception) |
| 502 | External API returns invalid/null data | "Agify/Nationalize/Genderize returned an invalid response" |

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

# List all profiles
curl http://localhost:5000/api/profiles

# Filter profiles
curl "http://localhost:5000/api/profiles?gender=male&age_group=adult"

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
├── app.py                   # Flask application with CRUD endpoints
├── utils.py                 # External API clients + helper functions
├── profiles.db              # SQLite database (auto-created)
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
