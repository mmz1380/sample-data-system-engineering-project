import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PostgresToClickHouse")

# PySpark environment variables
os.environ[
    'PYSPARK_SUBMIT_ARGS'] = '--jars /opt/spark/jars/postgresql-42.2.29.jre7.jar,/opt/spark/jars/clickhouse-jdbc-0.6.0.jar pyspark-shell'


def initialize_spark_session():
    logger.info("Initializing Spark session...")
    return SparkSession.builder \
        .appName("Postgres to ClickHouse") \
        .master("spark://spark-master:7077") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "2g") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.2.29.jre7.jar,/opt/spark/jars/clickhouse-jdbc-0.6.0.jar") \
        .getOrCreate()


def read_postgres_table(spark, table_name):
    logger.info(f"Reading '{table_name}' table from PostgreSQL...")
    try:
        df = spark.read \
            .format("jdbc") \
            .option("url", postgres_url) \
            .option("dbtable", table_name) \
            .option("driver", "org.postgresql.Driver") \
            .option("user", "admin") \
            .option("password", "password") \
            .load()
        count = df.count()
        logger.info(f"Successfully read '{table_name}' table with {count} records.")
        return df
    except Exception as e:
        logger.error(f"Error reading table '{table_name}' from PostgreSQL: {str(e)}")
        raise


def read_clickhouse_existing_ids():
    logger.info("Reading existing 'houses' data from ClickHouse to check for duplicates...")
    try:
        existing_df = spark.read \
            .format("jdbc") \
            .option("url", "jdbc:clickhouse://clickhouse:8123") \
            .option("dbtable", "houses") \
            .option("user", "default") \
            .option("password", "") \
            .load()
        logger.info(f"Successfully read existing 'houses' data with {existing_df.count()} records.")
        return existing_df.select("id").distinct()
    except Exception as e:
        logger.error(f"Error reading existing 'houses' data from ClickHouse: {str(e)}")
        raise


def filter_new_records(houses_df, existing_ids_df):
    logger.info("Filtering out records that already exist in ClickHouse...")
    try:
        filtered_df = houses_df.join(existing_ids_df, houses_df["id"] == existing_ids_df["id"], "left_anti")
        logger.info(f"Number of new records to be inserted: {filtered_df.count()}")
        return filtered_df
    except Exception as e:
        logger.error(f"Error filtering new records: {str(e)}")
        raise


def write_to_clickhouse(df):
    logger.info("Writing new records to ClickHouse...")
    try:
        df.write \
            .format("jdbc") \
            .option("url", "jdbc:clickhouse://clickhouse:8123") \
            .option("dbtable", "houses") \
            .option("user", "default") \
            .option("password", "") \
            .mode("append") \
            .save()
        logger.info("Successfully written new records to ClickHouse.")
    except Exception as e:
        logger.error(f"Error writing to ClickHouse: {str(e)}")
        raise


# Main logic
if __name__ == "__main__":
    try:
        spark = initialize_spark_session()
        postgres_url = "jdbc:postgresql://postgres:5432/internship_project"

        # Read PostgreSQL tables
        persons_df = read_postgres_table(spark, "persons") \
            .withColumnRenamed("f_name", "first_name") \
            .withColumnRenamed("l_name", "last_name")
        persons_df = persons_df.withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name")))

        houses_df = read_postgres_table(spark, "houses").na.drop().withColumnRenamed("owner_id", "person_id")

        # Join the data
        logger.info("Joining houses and persons DataFrames...")
        joined_df = houses_df.join(
            persons_df,
            houses_df["person_id"] == persons_df["id"],
            "left_outer"
        ).select(
            houses_df["*"], persons_df["full_name"]
        )
        joined_df = joined_df.withColumnRenamed('full_name', 'owner_full_name')

        # Read existing data from ClickHouse
        existing_ids_df = read_clickhouse_existing_ids()

        # Filter the joined DataFrame to get only new records
        new_records_df = filter_new_records(joined_df, existing_ids_df)

        # Write the filtered DataFrame to ClickHouse
        write_to_clickhouse(new_records_df)

        logger.info("Script completed successfully.")

    except Exception as main_exception:
        logger.error(f"An error occurred during the execution of the script: {str(main_exception)}")
