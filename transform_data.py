import argparse
import os

from etl.transform import run_transformation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the transformation step on an existing arsenal_matches.csv file."
    )
    parser.add_argument(
        "--input",
        default="arsenal_matches.csv",
        help="Path to the CSV produced by the extraction step.",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("S3_PARQUET_PATH", "arsenal_avg_goals.parquet"),
        help="Parquet output path (local path or s3://bucket/key).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_transformation(csv_path=args.input, output_path=args.output)


if __name__ == "__main__":
    main()
