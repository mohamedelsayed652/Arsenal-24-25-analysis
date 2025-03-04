from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

# Initialize Spark
spark = SparkSession.builder.appName("ArsenalStatsETL").getOrCreate()

# Load Match Data from CSV
df_spark = spark.read.csv("arsenal_matches.csv", header=True, inferSchema=True)

# Print schema and confirm data is read correctly
print(f"✅ Total matches loaded: {df_spark.count()}")
df_spark.show(5)
df_spark.printSchema()

# Convert necessary columns to integer
df_spark = df_spark.withColumn("goals_for", col("goals_for").cast("int"))
df_spark = df_spark.withColumn("goals_against", col("goals_against").cast("int"))

# Calculate Arsenal's Average Goals per Match
df_avg_goals = df_spark.groupBy("home_or_away").agg(avg("goals_for").alias("avg_goals_for"))
df_avg_goals.show()
df_avg_goals.write.mode("overwrite").parquet("arsenal_avg_goals.parquet")

# Calculate Goal Difference Trend
df_spark = df_spark.withColumn("goal_difference", col("goals_for") - col("goals_against"))

# Stronger at Home or Away?
df_goal_diff = df_spark.groupBy("home_or_away").agg(avg("goal_difference").alias("avg_goal_difference"))
df_goal_diff.show()
df_goal_diff.write.mode("overwrite").parquet("arsenal_goal_diff.parquet")

# Save full transformed data
df_spark.write.mode("overwrite").parquet("arsenal_stats.parquet")

# Validate Output
df_loaded = spark.read.parquet("arsenal_stats.parquet")
print(f"✅ Final dataset rows: {df_loaded.count()}")
df_loaded.show(5)
