import os

os.environ[
    'PYSPARK_SUBMIT_ARGS'] = '--jars /opt/spark/jars/postgresql-42.2.29.jre7.jar,/opt/spark/jars/clickhouse-jdbc-0.6.0.jar pyspark-shell'

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, FloatType, BooleanType, \
    TimestampType

# schema_of_persons = StructType([
#     StructField("id", IntegerType(), False),
#     StructField("f_name", StringType(), False),
#     StructField("l_name", StringType(), False),
#     StructField("national_code", StringType(), False),
#     StructField("place_of_birth", StringType(), False),
#     StructField("birthday", DateType(), False),
#     StructField("time_stamp", TimestampType(), False)
# ])
#
# schema_of_houses = StructType([
#     StructField("id", IntegerType(), False),
#     StructField("area", IntegerType(), False),
#     StructField("number_of_bedroom", FloatType(), False),
#     StructField("number_of_bathroom", FloatType(), False),
#     StructField("year", StringType(), False),
#     StructField("plot_size", IntegerType(), False),
#     StructField("floor", IntegerType(), False),
#     StructField("is_plot_owned", BooleanType(), False),
#     StructField("parking_lot_owned", IntegerType(), False),
#     StructField("is_single_unit", BooleanType(), False),
#     StructField("owner_id", IntegerType(), True),
#     StructField("time_stamp", TimestampType(), False)
# ])

spark = SparkSession.builder \
    .appName("Postgres to ClickHouse") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.jars", "/opt/spark/jars/postgresql-42.2.29.jre7.jar,/opt/spark/jars/clickhouse-jdbc-0.6.0.jar") \
    .getOrCreate()

postgres_url = "jdbc:postgresql://postgres:5432/internship_project"
persons_df = spark.read \
    .format("jdbc") \
    .option("url", postgres_url) \
    .option("dbtable", "persons") \
    .option("driver", "org.postgresql.Driver") \
    .option("user", "admin") \
    .option("password", "password") \
    .load()

persons_df = persons_df \
    .withColumnRenamed("f_name", "first_name") \
    .withColumnRenamed("l_name", "last_name")

persons_df = persons_df.withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name")))

houses_df = spark.read \
    .format("jdbc") \
    .option("url", postgres_url) \
    .option("dbtable", "houses") \
    .option("driver", "org.postgresql.Driver") \
    .option("user", "admin") \
    .option("password", "password") \
    .load()

houses_df = houses_df.na.drop()

houses_df = houses_df.withColumnRenamed("owner_id", "person_id")

joined_df = houses_df.join(
    persons_df,
    houses_df["person_id"] == persons_df["id"],
    "left_outer"
).select(
    houses_df["*"], persons_df["full_name"]
)


def write_to_clickhouse(df):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:clickhouse://clickhouse:8123") \
        .option("dbtable", "houses") \
        .option("user", "default") \
        .option("password", "") \
        .mode("append") \
        .save()


write_to_clickhouse(joined_df)
