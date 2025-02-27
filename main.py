import requests
import pandas as pd

# API Credentials
API_URL = "https://v3.football.api-sports.io/"
API_KEY = "73eb37e4a4909127f5a336492ef64ebb"

# Fetch Arsenal Team Info
team_id = 42  # Arsenal's ID in API-Football
headers = {"x-apisports-key": API_KEY}

# Fetch Matches
matches_response = requests.get(f"{API_URL}fixtures?team={team_id}&season=2024", headers=headers)
matches = matches_response.json()["response"]

# Convert to DataFrame
df_matches = pd.DataFrame([{
    "match_id": match["fixture"]["id"],
    "date": match["fixture"]["date"],
    "opponent": match["teams"]["away"]["name"] if match["teams"]["home"]["id"] == team_id else match["teams"]["home"]["name"],
    "home_or_away": "Home" if match["teams"]["home"]["id"] == team_id else "Away",
    "goals_for": match["goals"]["home"] if match["teams"]["home"]["id"] == team_id else match["goals"]["away"],
    "goals_against": match["goals"]["away"] if match["teams"]["home"]["id"] == team_id else match["goals"]["home"],
} for match in matches])

print(df_matches.head())