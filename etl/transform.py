from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# S3 output path
s3_output_path = os.getenv("S3_PARQUET_PATH", "s3://arsenal-etl-pipeline/processed/arsenal_stats.parquet")

def run_transformation(csv_path="arsenal_matches.csv"):
    # Initialize Spark with S3 support (using s3a and environment variable credentials)
    spark = SparkSession.builder \
        .appName("ArsenalStatsETL") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.EnvironmentVariableCredentialsProvider") \
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID")) \
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY")) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

    # Load match data from CSV
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    print(f"✅ Loaded {df.count()} match records")
    df.show(5)

    # Cast score columns
    df = df.withColumn("goals_for", col("goals_for").cast("int"))
    df = df.withColumn("goals_against", col("goals_against").cast("int"))

    # Add goal difference
    df = df.withColumn("goal_difference", col("goals_for") - col("goals_against"))

    # Calculate average stats
    df.groupBy("home_or_away").agg(avg("goals_for")).show()
    df.groupBy("home_or_away").agg(avg("goal_difference")).show()
    
    df.printSchema()
    # Write to S3 as Parquet
    try:
        df.write.mode("overwrite").parquet(s3_output_path)
        print(f"✅ Transformed data saved to S3: {s3_output_path}")
    except Exception as e:
        print(f"❌ Failed to write to S3: {e}")

    # Optional: read back and validate
    try:
        df_loaded = spark.read.parquet(s3_output_path)
        print(f"✅ Read back {df_loaded.count()} rows from S3")
        df_loaded.show(5)
    except Exception as e:
        print(f"❌ Error reading back from S3: {e}")