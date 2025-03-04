import psycopg2
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load database credentials from environment variables
DB_NAME = os.getenv("REDSHIFT_DB", "your_db")
DB_USER = os.getenv("REDSHIFT_USER", "your_user")
DB_HOST = os.getenv("REDSHIFT_HOST", "your_redshift_cluster")
DB_PORT = os.getenv("REDSHIFT_PORT", "5439")
IAM_ROLE = os.getenv("REDSHIFT_IAM_ROLE", "your-redshift-role")
S3_BUCKET = "s3://your-bucket-name/processed/arsenal_stats.parquet"

# Generate a temporary authentication token
boto_client = boto3.client("redshift-serverless")
creds = boto_client.get_credentials(workgroupName="arsenal-stats-analysis")

try:
    # Connect to Redshift using IAM authentication
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=creds["dbUser"],
        password=creds["dbPassword"],
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
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
