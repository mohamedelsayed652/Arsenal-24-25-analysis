import io
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import boto3
import pandas as pd
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

from etl.validation import validate_matches_df

# Load environment variables
load_dotenv()

DEFAULT_OUTPUT_PATH = os.getenv("S3_PARQUET_PATH", "arsenal_avg_goals.parquet")
log = logging.getLogger(__name__)


def _split_s3_path(path: str) -> Tuple[str, str]:
    """
    Splits an s3://bucket/key path into bucket and key components.
    """
    without_scheme = path.replace("s3://", "", 1)
    bucket, _, key = without_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 path: {path}")
    return bucket, key


def _write_parquet(df: pd.DataFrame, output_path: str) -> None:
    """
    Writes a DataFrame to Parquet locally or to S3.
    """
    try:
        if output_path.startswith("s3://"):
            bucket, key = _split_s3_path(output_path)
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)
            boto3.client("s3").upload_fileobj(buffer, bucket, key)
            log.info("Uploaded parquet to s3://%s/%s", bucket, key)
        else:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(path, index=False)
            log.info("Wrote parquet to %s", path)
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"Failed to upload parquet to {output_path}: {exc}") from exc
    except ModuleNotFoundError as exc:
        raise RuntimeError("Missing parquet engine. Install `pyarrow` (recommended) or `fastparquet`.") from exc


def run_transformation(csv_path: str = "arsenal_matches.csv", output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Cleans and enriches the extracted match data, then writes Parquet output
    locally or to S3 depending on S3_PARQUET_PATH.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Match CSV not found at {csv_path}. Run extraction first.")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("No rows found in extracted data.")

    # Normalize types and basic derived metrics.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["goals_for"] = pd.to_numeric(df["goals_for"], errors="coerce").fillna(0).astype(int)
    df["goals_against"] = pd.to_numeric(df["goals_against"], errors="coerce").fillna(0).astype(int)
    df["goal_difference"] = df["goals_for"] - df["goals_against"]

    def _result(row: pd.Series) -> str:
        if row["goal_difference"] > 0:
            return "W"
        if row["goal_difference"] < 0:
            return "L"
        return "D"

    df["result"] = df.apply(_result, axis=1)
    df = df.sort_values("date")
    df["rolling_goals_for_5"] = df["goals_for"].rolling(5, min_periods=1).mean().round(2)
    df["rolling_goal_diff_5"] = df["goal_difference"].rolling(5, min_periods=1).mean().round(2)

    # Validate schema
    validate_matches_df(df)

    # Helpful aggregates for quick validation.
    avg_by_venue = (
        df.groupby("home_or_away")[["goals_for", "goal_difference"]]
        .mean()
        .round(2)
        .reset_index()
    )
    log.info("Average goals/goal diff by venue:\n%s", avg_by_venue.to_string(index=False))

    output_path = output_path or DEFAULT_OUTPUT_PATH
    _write_parquet(df, output_path)
    log.info("Transformed data saved to %s", output_path)

    return df
