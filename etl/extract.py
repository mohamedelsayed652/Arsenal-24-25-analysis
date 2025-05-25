import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "https://v3.football.api-sports.io/"
API_KEY = os.getenv("API_FOOTBALL_KEY")
TEAM_ID = 42  # Arsenal

headers = {"x-apisports-key": API_KEY}

def run_extraction(season=2023) -> pd.DataFrame:
    """
    Fetch Arsenal matches from API-Football and return as DataFrame.
    """
    url = f"{API_URL}fixtures?team={TEAM_ID}&season={season}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ API Error: {response.status_code}, {response.json()}")

    data = response.json()

    if "response" not in data or not data["response"]:
        raise Exception("❌ Unexpected API response structure or no data returned.")

    matches = data["response"]

    df_matches = pd.DataFrame([{
        "match_id": match["fixture"]["id"],
        "date": match["fixture"]["date"],
        "opponent": match["teams"]["away"]["name"] if match["teams"]["home"]["id"] == TEAM_ID else match["teams"]["home"]["name"],
        "home_or_away": "Home" if match["teams"]["home"]["id"] == TEAM_ID else "Away",
        "goals_for": match["goals"]["home"] if match["teams"]["home"]["id"] == TEAM_ID else match["goals"]["away"],
        "goals_against": match["goals"]["away"] if match["teams"]["home"]["id"] == TEAM_ID else match["goals"]["home"],
    } for match in matches])

    return df_matches