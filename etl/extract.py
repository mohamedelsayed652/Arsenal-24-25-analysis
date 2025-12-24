import logging
import os
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()

API_URL = "https://v3.football.api-sports.io/"
API_KEY = os.getenv("API_FOOTBALL_KEY")
TEAM_ID = 42  # Arsenal

log = logging.getLogger(__name__)


def _build_headers() -> Dict[str, str]:
    if not API_KEY:
        raise ValueError("API_FOOTBALL_KEY is not set. Add it to your .env file.")
    return {"x-apisports-key": API_KEY}


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(requests.RequestException),
)
def _fetch(url: str) -> requests.Response:
    return requests.get(url, headers=_build_headers(), timeout=30)


def run_extraction(season: int = 2023) -> pd.DataFrame:
    """
    Fetch Arsenal matches from API-Football and return as DataFrame.
    """
    url = f"{API_URL}fixtures?team={TEAM_ID}&season={season}"
    log.info("Requesting fixtures: season=%s", season)
    try:
        response = _fetch(url)
    except requests.RequestException as exc:
        raise ConnectionError(f"Network error while calling API-Football: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"❌ API Error: {response.status_code}, {response.text}")

    data = response.json()

    if "response" not in data or not data["response"]:
        raise RuntimeError("❌ Unexpected API response structure or no data returned.")

    matches: List[dict] = data["response"]
    log.info("Fetched %d fixtures", len(matches))

    df_matches = pd.DataFrame([{
        "match_id": match["fixture"]["id"],
        "date": match["fixture"]["date"],
        "opponent": match["teams"]["away"]["name"] if match["teams"]["home"]["id"] == TEAM_ID else match["teams"]["home"]["name"],
        "home_or_away": "Home" if match["teams"]["home"]["id"] == TEAM_ID else "Away",
        "goals_for": match["goals"]["home"] if match["teams"]["home"]["id"] == TEAM_ID else match["goals"]["away"],
        "goals_against": match["goals"]["away"] if match["teams"]["home"]["id"] == TEAM_ID else match["goals"]["home"],
    } for match in matches])

    return df_matches
