import pandas as pd
from pathlib import Path

from etl.transform import run_transformation


def test_run_transformation_writes_parquet(tmp_path: Path):
    csv_path = tmp_path / "arsenal_matches.csv"
    df = pd.DataFrame(
        {
            "match_id": [1, 2, 3],
            "date": ["2023-08-01", "2023-08-08", "2023-08-15"],
            "opponent": ["Team A", "Team B", "Team C"],
            "home_or_away": ["Home", "Away", "Home"],
            "goals_for": [2, 1, 3],
            "goals_against": [0, 1, 2],
        }
    )
    df.to_csv(csv_path, index=False)

    output_path = tmp_path / "out" / "arsenal.parquet"
    result_df = run_transformation(csv_path=str(csv_path), output_path=str(output_path))

    assert output_path.exists()
    assert "goal_difference" in result_df.columns
    assert "rolling_goals_for_5" in result_df.columns
    assert result_df.iloc[-1]["result"] == "W"
