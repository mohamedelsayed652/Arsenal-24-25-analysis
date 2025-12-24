import logging
import os
from typing import Optional
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("REDSHIFT_DB", "your_db")
DB_USER = os.getenv("REDSHIFT_USER", "")
DB_PASSWORD = os.getenv("REDSHIFT_PASSWORD", "")
DB_HOST = os.getenv("REDSHIFT_HOST", "your_redshift_cluster")
DB_PORT = os.getenv("REDSHIFT_PORT", "5439")
IAM_ROLE = os.getenv("REDSHIFT_IAM_ROLE", "your-redshift-role")
S3_PARQUET_PATH = os.getenv("S3_PARQUET_PATH", "")

log = logging.getLogger(__name__)


def _validate_s3_path(path: str) -> None:
    parsed = urlparse(path)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.strip("/"):
        raise ValueError("S3_PARQUET_PATH must be an s3://bucket/key path to load into Redshift.")


def run_load(parquet_path: Optional[str] = None) -> None:
    """
    Loads processed data from S3 into Redshift using COPY command.
    """
    s3_path = parquet_path or S3_PARQUET_PATH
    _validate_s3_path(s3_path)

    try:
        conn_params = {
            "dbname": DB_NAME,
            "host": DB_HOST,
            "port": DB_PORT,
            "sslmode": "require"
        }

        if DB_USER:
            conn_params["user"] = DB_USER
        if DB_PASSWORD:
            conn_params["password"] = DB_PASSWORD

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # Ensure target table exists and clear it before COPY (preserves dependent views)
        cur.execute(
            """
            create table if not exists arsenal_matches (
                match_id            bigint primary key,
                date                timestamp not null,
                opponent            varchar(128) not null,
                home_or_away        varchar(8) not null,
                goals_for           integer not null,
                goals_against       integer not null,
                goal_difference     integer not null,
                result              varchar(1) not null,
                rolling_goals_for_5 double precision,
                rolling_goal_diff_5 double precision
            );
            """
        )
        cur.execute("truncate table arsenal_matches;")

        copy_sql = f"""
            COPY arsenal_matches
            FROM '{s3_path}'
            IAM_ROLE '{IAM_ROLE}'
            FORMAT AS PARQUET;
        """

        cur.execute(copy_sql)
        conn.commit()
        log.info("Data loaded into Redshift successfully")

    except Exception as e:
        log.error("Error loading data into Redshift: %s", e)
        raise

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
