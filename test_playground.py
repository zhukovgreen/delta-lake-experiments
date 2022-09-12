import pathlib

import pyspark
import pytest

from delta import configure_spark_with_delta_pip
from loguru import logger
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col
from pyspark.sql.utils import AnalysisException


def build_spark_session() -> SparkSession:
    builder = (
        pyspark.sql.SparkSession.builder.appName("MyApp")
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )

    return configure_spark_with_delta_pip(builder).getOrCreate()


def read_data_from_csv_path(
    spark: SparkSession,
    p: pathlib.Path,
) -> DataFrame:
    return (
        spark.read.option(
            "header",
            "true",
        )
        .option(
            "header",
            "true",
        )
        .option(
            "inferSchema",
            "true",
        )
        .csv(p.as_posix())
        .withColumn("partition", col("date").substr(0, 4))
    )


def test_cases():
    spark = build_spark_session()
    df = read_data_from_csv_path(
        spark,
        pathlib.Path("./data/departuredelays.csv"),
    )
    df1 = read_data_from_csv_path(
        spark,
        pathlib.Path("./data/append.csv"),
    )
    df2 = read_data_from_csv_path(
        spark,
        pathlib.Path("./data/append_1.csv"),
    )
    df_bad_data = read_data_from_csv_path(
        spark,
        pathlib.Path("./data/append_bad_data.csv"),
    )

    (
        df.write.format("delta")
        .partitionBy(["partition"])
        .option("mergeSchema", "true")
        .option("overwriteSchema", "true")
        .mode("overwrite")
        .save("./tmp/departuredelays")
    )
    res = spark.read.format("delta").load("./tmp/departuredelays")
    res.printSchema()
    logger.info(f"Number of records after df : {res.count(): 10}")

    (
        df1.write.format("delta")
        .partitionBy(["partition"])
        .option("mergeSchema", "true")
        .mode("append")
        .save("./tmp/departuredelays")
    )
    res = spark.read.format("delta").load("./tmp/departuredelays")
    res.printSchema()
    logger.info(f"Number of records after df1: {res.count(): 10}")

    (
        df2.write.format("delta")
        .partitionBy(["partition"])
        .option("mergeSchema", "true")
        .option("overwriteSchema", "true")
        .mode("overwrite")
        .save("./tmp/departuredelays")
    )
    res = spark.read.format("delta").load("./tmp/departuredelays")
    res.printSchema()
    logger.info(f"Number of records after df2: {res.count(): 10}")

    with pytest.raises(
        AnalysisException,
        match=(
            "Failed to merge fields 'delay' and 'delay'. "
            "Failed to merge incompatible data types "
            "IntegerType and StringType"
        ),
    ):
        (
            df_bad_data.write.format("delta")
            .partitionBy(["partition"])
            .mode("append")
            .save("./tmp/departuredelays")
        )
