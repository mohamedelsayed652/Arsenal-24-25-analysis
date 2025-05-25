from etl.extract import run_extraction
from etl.transform import run_transformation
from etl.load import run_load

import pandas as pd

def main():
    print("🚀 Starting Arsenal ETL pipeline...")

    # Step 1: Extract
    try:
        df = run_extraction(season=2023)
        df.to_csv("arsenal_matches.csv", index=False)
        print("✅ Data extracted and saved to arsenal_matches.csv")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return

    # Step 2: Transform
    try:
        run_transformation(csv_path="arsenal_matches.csv")
    except Exception as e:
        print(f"❌ Transformation failed: {e}")
        return

    # Step 3: Load
    try:
        run_load()
    except Exception as e:
        print(f"❌ Load failed: {e}")
        return

    print("🎉 ETL pipeline completed successfully!")

if __name__ == "__main__":
    main()