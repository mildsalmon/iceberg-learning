"""Spark + Iceberg 세션 생성 유틸리티."""

import hashlib
import importlib.util
import os
import subprocess
import sys
import time

ICEBERG_JAR_URL = (
    "https://repo1.maven.org/maven2/org/apache/iceberg/"
    "iceberg-spark-runtime-3.4_2.12/1.4.3/"
    "iceberg-spark-runtime-3.4_2.12-1.4.3.jar"
)
ICEBERG_JAR_PATH = "/home/jovyan/iceberg-spark.jar"
WAREHOUSE_PATH = "file:///home/jovyan/data/warehouse"
INSTALL_RETRIES = 3
DOWNLOAD_RETRIES = 3
RETRY_WAIT_SECONDS = 2

REQUIRED_PACKAGES = [
    "pyspark==3.4.0",
    "pandas",
    "matplotlib",
    "fastavro",
    "pyarrow",
    "requests",
]


def _module_name_from_requirement(requirement):
    """요구사항 문자열에서 import 가능한 모듈명을 추출한다."""
    base = requirement.split(";", 1)[0]
    base = base.split("[", 1)[0]
    for op in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if op in base:
            base = base.split(op, 1)[0]
            break
    return base.strip().replace("-", "_")


def _is_module_available(requirement):
    module_name = _module_name_from_requirement(requirement)
    return importlib.util.find_spec(module_name) is not None


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def install_packages(
    packages=None,
    max_retries=INSTALL_RETRIES,
    retry_wait_sec=RETRY_WAIT_SECONDS,
):
    """필요한 Python 패키지를 설치한다."""
    packages = packages or REQUIRED_PACKAGES
    installed = 0
    skipped = 0
    failed = []

    for pkg in packages:
        if _is_module_available(pkg):
            skipped += 1
            print(f"SKIP: {pkg} (이미 설치됨)")
            continue

        for attempt in range(1, max_retries + 1):
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-q", pkg]
                )
                installed += 1
                print(f"OK: {pkg}")
                break
            except subprocess.CalledProcessError as exc:
                print(
                    f"WARN: {pkg} 설치 실패 ({attempt}/{max_retries}) - {exc}"
                )
                if attempt < max_retries:
                    time.sleep(retry_wait_sec)
        else:
            failed.append(pkg)

    if failed:
        raise RuntimeError(
            "패키지 설치 실패: "
            + ", ".join(failed)
            + ". 네트워크/패키지 인덱스 상태를 확인한 뒤 다시 실행하세요."
        )

    print(
        f"{len(packages)}개 점검 완료 "
        f"(신규 설치 {installed}, 기존 설치 {skipped}, 실패 0)."
    )


def download_iceberg_jar(
    url=ICEBERG_JAR_URL,
    path=ICEBERG_JAR_PATH,
    expected_sha256=None,
    timeout=(5, 60),
    max_retries=DOWNLOAD_RETRIES,
    retry_wait_sec=RETRY_WAIT_SECONDS,
):
    """Iceberg Spark Runtime JAR이 없으면 다운로드한다."""
    expected_sha256 = (
        expected_sha256
        or os.getenv("ICEBERG_JAR_SHA256")
    )

    def validate_checksum(file_path):
        if not expected_sha256:
            return
        actual = _sha256(file_path)
        if actual.lower() != expected_sha256.lower():
            raise RuntimeError(
                "JAR 체크섬 불일치: "
                f"expected={expected_sha256}, actual={actual}"
            )

    if os.path.exists(path):
        validate_checksum(path)
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"JAR 이미 존재: {path} ({size_mb:.1f} MB)")
        if expected_sha256:
            print("SHA256 검증 완료.")
        return path

    import requests

    tmp_path = f"{path}.tmp"
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Iceberg JAR 다운로드 중 ... ({attempt}/{max_retries})")
            with requests.get(url, timeout=timeout, stream=True) as resp:
                resp.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)

            validate_checksum(tmp_path)
            os.replace(tmp_path, path)
            size_mb = os.path.getsize(path) / 1024 / 1024
            print(f"JAR 다운로드 완료: {path} ({size_mb:.1f} MB)")
            if expected_sha256:
                print("SHA256 검증 완료.")
            return path
        except Exception as exc:
            last_error = exc
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(
                f"WARN: JAR 다운로드 실패 ({attempt}/{max_retries}) - {exc}"
            )
            if attempt < max_retries:
                time.sleep(retry_wait_sec)

    raise RuntimeError(
        "Iceberg JAR 다운로드 실패. 네트워크 상태를 확인하거나 "
        "잠시 후 다시 시도하세요."
    ) from last_error


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
