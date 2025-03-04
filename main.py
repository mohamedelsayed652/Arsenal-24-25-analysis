import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
API_URL = "https://v3.football.api-sports.io/"
API_KEY = os.getenv("API_FOOTBALL_KEY")  # Store this in .env

# Fetch Arsenal Team Info
team_id = 42  # Arsenal's ID in API-Football
headers = {"x-apisports-key": API_KEY}

# Fetch Matches
matches_response = requests.get(f"{API_URL}fixtures?team={team_id}&season=2023", headers=headers)

# Print raw API response
print("RAW API RESPONSE:", matches_response.json())

# Validate API Response
if matches_response.status_code != 200:
    print(f"❌ API Error: {matches_response.json()}")
    exit()

matches_data = matches_response.json()

# Check if 'response' exists in JSON
if "response" not in matches_data or not matches_data["response"]:
    print("❌ Unexpected API response structure or no data returned.")
    exit()

matches = matches_data["response"]

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

# Save to CSV for transformation
df_matches.to_csv("arsenal_matches.csv", index=False)
