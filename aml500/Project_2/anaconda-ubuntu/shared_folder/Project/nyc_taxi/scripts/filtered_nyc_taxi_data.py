import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, lit, to_timestamp, unix_timestamp

# Get job arguments
args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "year", "month", "bucket_name", "s3_key_prefix"]
)

# Initialize Glue context and Spark session
spark = SparkSession.builder.appName("ClassFilterNYCTaxiData").getOrCreate()
glueContext = GlueContext(spark)
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Read arguments
year = int(args["year"])
month = int(args["month"])
bucket_name = args["bucket_name"]
s3_key_prefix = args["s3_key_prefix"]

# Define S3 paths
input_s3_key = f"s3://{bucket_name}/{s3_key_prefix}/year={year}/month={month:02}/yellow_tripdata_{year}-{month:02}.parquet"
output_s3_key = f"s3://{bucket_name}/{s3_key_prefix.replace('raw', 'glue-filtered')}/year={year}/month={month:02}/yellow_tripdata_{year}-{month:02}.parquet"

# Read the Parquet file into a Spark DataFrame
rides = spark.read.parquet(input_s3_key)

# Total records before any filtering
total_records = rides.count()

# Define the start and end date for filtering
start_date = f"{year}-{month:02}-01"
end_date = f"{year + (month // 12)}-{(month % 12) + 1:02}-01"

# Filter and clean the data
rides_clean = rides.filter(
    (col("tpep_pickup_datetime").isNotNull())
    & (col("tpep_dropoff_datetime").isNotNull())
    & (col("total_amount").isNotNull())
    & (col("PULocationID").isNotNull())
    & (col("DOLocationID").isNotNull())
    & (col("trip_distance").isNotNull())
    & (col("passenger_count").isNotNull())
)

# Records dropped due to missing values
dropped_missing = total_records - rides_clean.count()

rides_clean = rides_clean.filter(
    (col("tpep_pickup_datetime") >= start_date)
    & (col("tpep_pickup_datetime") < end_date)
)

# Records dropped by date range filter
dropped_date_range = total_records - dropped_missing - rides_clean.count()

# Convert duration to seconds for compatibility with approxQuantile
rides_clean = rides_clean.withColumn(
    "duration",
    (unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")),
)

# Calculate quantiles for filtering
quantiles = rides_clean.approxQuantile(
    ["duration", "total_amount", "trip_distance"], [0.999], 0.01
)
max_duration, max_total_amount, max_distance = (
    quantiles[0][0],
    quantiles[1][0],
    quantiles[2][0],
)

# Apply additional filters
rides_filtered = rides_clean.filter(
    (col("duration") > lit(0)) & (col("duration") <= lit(max_duration))
)
dropped_duration = rides_clean.count() - rides_filtered.count()

rides_filtered = rides_filtered.filter(
    (col("total_amount") >= lit(2.5)) & (col("total_amount") <= lit(max_total_amount))
)
dropped_total_amount = rides_clean.count() - rides_filtered.count()

rides_filtered = rides_filtered.filter(
    (col("trip_distance") > lit(0)) & (col("trip_distance") <= lit(max_distance))
)
dropped_distance = rides_clean.count() - rides_filtered.count()

rides_filtered = rides_filtered.filter(~col("PULocationID").isin([1, 264, 265]))
dropped_location = rides_clean.count() - rides_filtered.count()

rides_filtered = rides_filtered.filter(
    (col("passenger_count") >= lit(1)) & (col("passenger_count") <= lit(5))
)
dropped_passenger_count = rides_clean.count() - rides_filtered.count()

# Final record count
valid_records = rides_filtered.count()
records_dropped = total_records - valid_records
percent_dropped = (records_dropped / total_records) * 100

# Combine all logging information into one output string
stats_msg = (
    f"Total records: {total_records:,}\n"
    f"Valid records: {valid_records:,}\n"
    f"Records dropped: {records_dropped:,} ({percent_dropped:.2f}%)\n"
    f"Records dropped due to missing values: {dropped_missing:,}\n"
    f"Records dropped by date range filter: {dropped_date_range:,}\n"
    f"Records dropped by duration filter: {dropped_duration:,}\n"
    f"Records dropped by total amount filter: {dropped_total_amount:,}\n"
    f"Records dropped by distance filter: {dropped_distance:,}\n"
    f"Records dropped by NYC location filter: {dropped_location:,}\n"
    f"Records dropped by passenger count filter: {dropped_passenger_count:,}"
)
print(stats_msg)

# Rename columns and cast to the required data types
rides_final = (
    rides_filtered.withColumnRenamed("tpep_pickup_datetime", "pickup_datetime")
    .withColumnRenamed("tpep_dropoff_datetime", "dropoff_datetime")
    .withColumnRenamed("PULocationID", "pickup_location_id")
    .withColumnRenamed("DOLocationID", "dropoff_location_id")
    .select(
        col("pickup_datetime").cast("timestamp"),
        col("dropoff_datetime").cast("timestamp"),
        col("pickup_location_id").cast("int"),
        col("dropoff_location_id").cast("int"),
        col("trip_distance").cast("double"),
        col("fare_amount").cast("double"),
        col("tip_amount").cast("double"),
        col("payment_type").cast("int"),
        col("passenger_count").cast("int"),
    )
)

# Write the filtered data back to S3
rides_final.write.mode("overwrite").parquet(output_s3_key)

print(f"Filtered data written to {output_s3_key}")

# Commit the job
job.commit()