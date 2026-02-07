from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


@dataclass(frozen=True)
class Settings:
    base_url: str
    data_path_template: str
    cities_path: Path
    suggest_limit: int


def load_settings() -> Settings:
    base_url = os.getenv(
        "DATA_CUACA_BASE_URL",
        "https://raw.githubusercontent.com/infoBMKG/data-cuaca/main",
    )
    data_path_template = os.getenv("DATA_PATH_TEMPLATE", "data/{code}.json")
    cities_path = Path(
        os.getenv("CITIES_PATH", Path(__file__).parent / "data" / "cities.json")
    )
    suggest_limit = int(os.getenv("SUGGEST_LIMIT", "5"))
    return Settings(
        base_url=base_url,
        data_path_template=data_path_template,
        cities_path=cities_path,
        suggest_limit=suggest_limit,
    )


class City(BaseModel):
    code: str
    name: str


class CityMatch(BaseModel):
    status: str
    message: str
    city: City | None = None
    suggestions: list[City] = []


class WeatherResponse(BaseModel):
    city: City
    date: str | None
    data: Any


def normalize_name(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def load_cities(path: Path) -> list[City]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing cities file at {path}. Update it using the data-cuaca repo."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [City(**entry) for entry in payload]


def find_city(
    cities: list[City],
    query: str,
    limit: int,
) -> CityMatch:
    normalized_query = normalize_name(query)
    normalized_map = {normalize_name(city.name): city for city in cities}

    if normalized_query in normalized_map:
        city = normalized_map[normalized_query]
        return CityMatch(
            status="found",
            message=f"City '{city.name}' found.",
            city=city,
            suggestions=[],
        )

    regex_matches = [
        city for city in cities if re.search(re.escape(query), city.name, re.IGNORECASE)
    ]
    if regex_matches:
        suggestions = regex_matches[:limit]
        return CityMatch(
            status="suggestions",
            message="City not found. Did you mean one of these?",
            suggestions=suggestions,
        )

    close_names = get_close_matches(
        normalized_query,
        list(normalized_map.keys()),
        n=limit,
        cutoff=0.6,
    )
    suggestions = [normalized_map[name] for name in close_names]
    message = (
        "City not found. Please retype the city or try another name."
        if not suggestions
        else "City not found. Here are the closest matches."
    )
    return CityMatch(
        status="suggestions" if suggestions else "not_found",
        message=message,
        suggestions=suggestions,
    )


settings = load_settings()
app = FastAPI(
    title="BMKG Data Cuaca API",
    description=(
        "Simple FastAPI wrapper for the infoBMKG/data-cuaca repository with city "
        "autocomplete and suggestions."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def load_city_data() -> None:
    app.state.cities = load_cities(settings.cities_path)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/cities", response_model=CityMatch)
def cities(q: str = Query(..., min_length=1)) -> CityMatch:
    return find_city(app.state.cities, q, settings.suggest_limit)


@app.get("/weather", response_model=WeatherResponse)
async def weather(
    city: str = Query(..., description="City name"),
    at: str | None = Query(None, description="YYYY-MM-DD"),
) -> WeatherResponse:
    match = find_city(app.state.cities, city, settings.suggest_limit)
    if match.status != "found" or match.city is None:
        raise HTTPException(status_code=404, detail=match.dict())

    data_path = settings.data_path_template.format(code=match.city.code)
    url = f"{settings.base_url}/{data_path}"

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Failed to fetch data from data-cuaca repository.",
                    "status_code": response.status_code,
                    "url": url,
                },
            )

    try:
        payload = response.json()
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Response from data-cuaca is not valid JSON.",
                "error": str(error),
                "url": url,
            },
        ) from error

    return WeatherResponse(city=match.city, date=at, data=payload)
