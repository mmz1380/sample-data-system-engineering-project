import os

os.environ[
    'PYSPARK_SUBMIT_ARGS'] = '--jars /opt/spark/jars/postgresql-42.2.29.jre7.jar,/opt/spark/jars/clickhouse-jdbc-0.6.0.jar pyspark-shell'

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, expr
from pyspark.sql import functions as F
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
    .appName("Kafka Spark Streaming") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.jars", "/opt/spark/jars/clickhouse-jdbc-0.6.0.jar") \
    .config("spark.executor.extraClassPath", "/opt/spark/jars/clickhouse-jdbc-0.6.0.jar") \
    .config("spark.driver.extraClassPath", "/opt/spark/jars/clickhouse-jdbc-0.6.0.jar") \
    .getOrCreate()

kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "dbserver1.public.persons,dbserver1.public.houses") \
    .load()

persons_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string") \
    .select(F.from_json(col("json_string"), schema_of_persons).alias("data")) \
    .select("data.*")

persons_df = persons_df \
    .withColumnRenamed("f_name", "first_name") \
    .withColumnRenamed("l_name", "last_name") \
    .withColumnRenamed('id', 'person_pk') \
    .withColumnRenamed('time_stamp', 'person_time_stamp')

persons_df = persons_df.withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name")))

houses_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string") \
    .select(F.from_json(col("json_string"), schema_of_houses).alias("data")) \
    .select("data.*")

houses_df = houses_df.na.drop()

houses_df = houses_df.withColumnRenamed("owner_id", "person_id") \
    .withColumnRenamed('time_stamp', 'house_time_stamp')

persons_df = persons_df.withWatermark("person_time_stamp", "10 minutes")
houses_df = houses_df.withWatermark("house_time_stamp", "10 minutes")

joined_df = houses_df.join(
    persons_df,
    expr("""
        person_id = person_pk AND
        house_time_stamp >= person_time_stamp - INTERVAL 10 MINUTES AND
        house_time_stamp <= person_time_stamp + INTERVAL 10 MINUTES
    """),
    "left_outer"
).select(
    houses_df["*"], persons_df["full_name"]
)


def write_to_clickhouse(df, epoch_id):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:clickhouse://clickhouse:8123") \
        .option("dbtable", "houses") \
        .option("user", "default") \
        .option("password", "") \
        .mode("append") \
        .save()


query = joined_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_clickhouse) \
    .start()

query.awaitTermination()
