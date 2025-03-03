from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

# Initialize Spark
spark = SparkSession.builder.appName("ArsenalStatsETL").getOrCreate()

# Load Match Data into Spark
df_spark = spark.createDataFrame(df_matches)

# Calculate Arsenal's Average Goals per Match
df_spark.groupBy("home_or_away").agg(avg("goals_for").alias("avg_goals_for")).show()

# Calculate Goal Difference Trend
df_spark = df_spark.withColumn("goal_difference", col("goals_for") - col("goals_against"))

# Stronger at Home or Away?
df_spark.groupBy("home_or_away").agg(avg("goal_difference").alias("avg_goal_difference")).show()