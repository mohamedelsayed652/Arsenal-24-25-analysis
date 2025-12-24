import logging
import os

from etl.extract import run_extraction
from etl.transform import run_transformation
from etl.transform_spark import run_transformation_spark
from etl.load import run_load


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def main():
    configure_logging()
    log = logging.getLogger("run_etl")
    log.info("🚀 Starting Arsenal ETL pipeline...")

    output_path = os.getenv("S3_PARQUET_PATH", "arsenal_avg_goals.parquet")
    use_spark = os.getenv("USE_SPARK", "").lower() in ("1", "true", "yes")

    # Step 1: Extract
    try:
        df = run_extraction(season=2023)
        df.to_csv("arsenal_matches.csv", index=False)
        log.info("✅ Data extracted and saved to arsenal_matches.csv")
    except Exception as e:
        log.error("❌ Extraction failed: %s", e)
        return

    # Step 2: Transform
    try:
        if use_spark:
            log.info("Using Spark-based transform (USE_SPARK=%s)", use_spark)
            run_transformation_spark(csv_path="arsenal_matches.csv", output_path=output_path)
        else:
            run_transformation(csv_path="arsenal_matches.csv", output_path=output_path)
    except Exception as e:
        log.error("❌ Transformation failed: %s", e)
        return

    # Step 3: Load
    try:
        if output_path.startswith("s3://"):
            run_load(parquet_path=output_path)
        else:
            log.info("ℹ️ S3_PARQUET_PATH is not an s3:// path; skipping Redshift load step.")
    except Exception as e:
        log.error("❌ Load failed: %s", e)
        return

    log.info("🎉 ETL pipeline completed successfully!")


if __name__ == "__main__":
    main()
