# BMKG Data Cuaca FastAPI

FastAPI service that wraps the public `infoBMKG/data-cuaca` repository and provides city autocomplete,
validation, and weather data lookup.

## Requirements
- Python 3.10+

## Setup
```bash
cd bmkg-data-cuaca-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API
```bash
uvicorn app.main:app --reload --port 8000
```

Open the interactive docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints
### City search with suggestions
```bash
curl "http://localhost:8000/cities?q=Jak"
```

### Weather data lookup
```bash
curl "http://localhost:8000/weather?city=Jakarta&at=2026-10-23"
```

If the city is unknown, the API returns suggestions so the user can retype or pick another city
that maps to a BMKG city code.

## City data
The service reads city data from `app/data/cities.json` (sample entries included). Update this file
with the official mapping from `infoBMKG/data-cuaca` so the city names map to the correct BMKG codes.

You can replace the file using the helper script:
```bash
python scripts/update_cities.py --source <url-or-file>
```

The `--source` JSON must be an array of objects with `{ "code": "...", "name": "..." }`.

## Configuration
Environment variables:
- `DATA_CUACA_BASE_URL` (default: `https://raw.githubusercontent.com/infoBMKG/data-cuaca/main`)
- `DATA_PATH_TEMPLATE` (default: `data/{code}.json`)
- `CITIES_PATH` (default: `app/data/cities.json`)
- `SUGGEST_LIMIT` (default: `5`)
