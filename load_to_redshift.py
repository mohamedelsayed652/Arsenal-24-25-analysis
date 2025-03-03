import psycopg2
import os

# Load database credentials from environment variables
DB_NAME = os.getenv("REDSHIFT_DB", "your_db")
DB_USER = os.getenv("REDSHIFT_USER", "your_user")
DB_PASSWORD = os.getenv("REDSHIFT_PASSWORD", "your_password")
DB_HOST = os.getenv("REDSHIFT_HOST", "your_redshift_cluster")
IAM_ROLE = os.getenv("REDSHIFT_IAM_ROLE", "your-redshift-role")
S3_BUCKET = "s3://your-bucket-name/processed/arsenal_stats.parquet"

try:
    # Connect to Redshift
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cur = conn.cursor()

    # Copy Data from S3 to Redshift
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
    if cur:
        cur.close()
    if conn:
        conn.close()