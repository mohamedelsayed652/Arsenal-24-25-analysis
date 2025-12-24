import pandas as pd
import pytest

from etl.validation import validate_matches_df


def _sample_df():
    return pd.DataFrame(
        {
            "match_id": [1, 2],
            "date": ["2023-08-01", "2023-08-08"],
            "opponent": ["Team A", "Team B"],
            "home_or_away": ["Home", "Away"],
            "goals_for": [2, 1],
            "goals_against": [0, 1],
            "goal_difference": [2, 0],
            "result": ["W", "D"],
            "rolling_goals_for_5": [2.0, 1.5],
            "rolling_goal_diff_5": [2.0, 1.0],
        }
    )


def test_validate_matches_df_passes_on_good_data():
    df = _sample_df()
    validated = validate_matches_df(df)
    assert len(validated) == 2


def test_validate_matches_df_raises_on_bad_enum():
    df = _sample_df()
    df.loc[0, "home_or_away"] = "Neutral"
    with pytest.raises(Exception):
        validate_matches_df(df)
