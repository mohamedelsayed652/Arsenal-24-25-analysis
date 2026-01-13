import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    lit,
    round as spark_round,
    when,
)
from pyspark.sql.window import Window

# Load environment variables
load_dotenv()

DEFAULT_OUTPUT_PATH = os.getenv("S3_PARQUET_PATH", "arsenal_avg_goals.parquet")
log = logging.getLogger(__name__)


def _split_s3_path(path: str) -> Tuple[str, str]:
    without_scheme = path.replace("s3://", "", 1)
    bucket, _, key = without_scheme.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 path: {path}")
    return bucket, key


def build_spark(app_name: str = "ArsenalStatsETL") -> SparkSession:
    builder = (
        SparkSession.builder.appName(app_name)
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901",
        )
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.EnvironmentVariableCredentialsProvider",
        )
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID"))
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY"))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com")
    )
    return builder.getOrCreate()


def run_transformation_spark(csv_path: str = "arsenal_matches.csv", output_path: Optional[str] = None) -> None:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Match CSV not found at {csv_path}. Run extraction first.")

    output_path = output_path or DEFAULT_OUTPUT_PATH
    spark = build_spark()

    df = (
        spark.read.csv(csv_path, header=True, inferSchema=True)
        .withColumn("date", col("date").cast("timestamp"))
        .withColumn("goals_for", col("goals_for").cast("int"))
        .withColumn("goals_against", col("goals_against").cast("int"))
    )

    df = df.withColumn("goal_difference", col("goals_for") - col("goals_against"))
    df = df.withColumn(
        "result",
        when(col("goal_difference") > 0, lit("W"))
        .when(col("goal_difference") < 0, lit("L"))
        .otherwise(lit("D")),
    )

    rolling_window = Window.orderBy(col("date")).rowsBetween(-4, 0)
    df = df.withColumn(
        "rolling_goals_for_5",
        spark_round(avg(col("goals_for")).over(rolling_window), 2),
    )
    df = df.withColumn(
        "rolling_goal_diff_5",
        spark_round(avg(col("goal_difference")).over(rolling_window), 2),
    )

    # Log quick aggregates to mirror pandas path validation visibility.
    df.groupBy("home_or_away").agg(
        spark_round(avg("goals_for"), 2).alias("avg_goals_for"),
        spark_round(avg("goal_difference"), 2).alias("avg_goal_diff"),
    ).show()

    if output_path.startswith("s3://"):
        df.write.mode("overwrite").parquet(output_path)
        log.info("Spark wrote parquet to %s", output_path)
    else:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.write.mode("overwrite").parquet(str(path))
        log.info("Spark wrote parquet to %s", path)

    spark.stop()
