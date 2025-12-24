import pandera as pa
from pandera import Column, DataFrameSchema, Check

matches_schema = DataFrameSchema(
    {
        "match_id": Column(pa.Int64, nullable=False, unique=True),
        "date": Column(pa.Timestamp, nullable=False),
        "opponent": Column(pa.String, nullable=False),
        "home_or_away": Column(pa.String, Check.isin(["Home", "Away"]), nullable=False),
        "goals_for": Column(pa.Int64, nullable=False),
        "goals_against": Column(pa.Int64, nullable=False),
        "goal_difference": Column(pa.Int64, nullable=False),
        "result": Column(pa.String, Check.isin(["W", "D", "L"]), nullable=False),
        "rolling_goals_for_5": Column(pa.Float64, nullable=True),
        "rolling_goal_diff_5": Column(pa.Float64, nullable=True),
    },
    coerce=True,
)


def validate_matches_df(df):
    """
    Validate the transformed matches DataFrame; raises a SchemaError on failure.
    """
    return matches_schema.validate(df, lazy=True)
