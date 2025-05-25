import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("REDSHIFT_DB", "your_db")
DB_USER = os.getenv("REDSHIFT_USER", "")
DB_PASSWORD = os.getenv("REDSHIFT_PASSWORD", "")
DB_HOST = os.getenv("REDSHIFT_HOST", "your_redshift_cluster")
DB_PORT = os.getenv("REDSHIFT_PORT", "5439")
IAM_ROLE = os.getenv("REDSHIFT_IAM_ROLE", "your-redshift-role")
S3_BUCKET = os.getenv("S3_PARQUET_PATH", "s3://your-bucket-name/processed/arsenal_stats.parquet")


def run_load():
    """
    Loads processed data from S3 into Redshift using COPY command.
    """
    try:
        # Connect to Redshift using credentials
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

        copy_sql = f"""
            COPY arsenal_matches
            FROM '{S3_BUCKET}'
            IAM_ROLE '{IAM_ROLE}'
            FORMAT AS PARQUET;
        """

        cur.execute(copy_sql)
        conn.commit()
        print("✅ Data loaded into Redshift successfully!")

    except Exception as e:
        print(f"❌ Error loading data into Redshift: {e}")

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()