"""Spark + Iceberg 세션 생성 유틸리티."""

import subprocess
import sys
import os


ICEBERG_JAR_URL = (
    "https://repo1.maven.org/maven2/org/apache/iceberg/"
    "iceberg-spark-runtime-3.4_2.12/1.4.3/"
    "iceberg-spark-runtime-3.4_2.12-1.4.3.jar"
)
ICEBERG_JAR_PATH = "/home/jovyan/iceberg-spark.jar"
WAREHOUSE_PATH = "file:///home/jovyan/data/warehouse"

REQUIRED_PACKAGES = [
    "pyspark==3.4.0",
    "pyiceberg[pyarrow,duckdb]",
    "pandas",
    "matplotlib",
    "fastavro",
]


def install_packages(packages=None):
    """필요한 Python 패키지를 설치한다."""
    packages = packages or REQUIRED_PACKAGES
    for pkg in packages:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", pkg]
        )
    print(f"{len(packages)}개 패키지 설치 완료.")


def download_iceberg_jar(url=ICEBERG_JAR_URL, path=ICEBERG_JAR_PATH):
    """Iceberg Spark Runtime JAR이 없으면 다운로드한다."""
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"JAR 이미 존재: {path} ({size_mb:.1f} MB)")
        return path

    import requests

    print("Iceberg JAR 다운로드 중 ...")
    resp = requests.get(url)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"JAR 다운로드 완료: {path} ({size_mb:.1f} MB)")
    return path


def create_spark_session(
    app_name="IcebergLab",
    warehouse=WAREHOUSE_PATH,
    jar_path=ICEBERG_JAR_PATH,
):
    """Iceberg가 설정된 SparkSession을 생성하여 반환한다.

    Usage::

        from utils.spark_setup import create_spark_session
        spark = create_spark_session()
    """
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName(app_name)
        .config("spark.jars", jar_path)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            "spark.sql.catalog.demo",
            "org.apache.iceberg.spark.SparkCatalog",
        )
        .config("spark.sql.catalog.demo.type", "hadoop")
        .config("spark.sql.catalog.demo.warehouse", warehouse)
        .getOrCreate()
    )
    print(f"Spark + Iceberg 세션 준비 완료 (warehouse: {warehouse})")
    return spark
