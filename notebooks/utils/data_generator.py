"""랜덤 주문 데이터 생성 유틸리티."""

import random
from datetime import datetime, timedelta

PRODUCTS = {
    "iPhone 14": 999.99,
    "iPhone 14 Pro": 1199.99,
    "MacBook Pro": 1999.99,
    "MacBook Air": 1299.99,
    "iPad Air": 649.99,
    "iPad Pro": 899.99,
    "AirPods": 199.99,
    "AirPods Pro": 299.99,
    "Apple Watch": 399.99,
    "Magic Mouse": 99.99,
    "Magic Keyboard": 199.99,
    "iMac": 1499.99,
    "Mac Studio": 2199.99,
    "Apple TV": 149.99,
    "HomePod": 349.99,
    "iPhone 13": 799.99,
    "iPhone SE": 449.99,
    "Mac Mini": 799.99,
    "Studio Display": 1799.99,
    "Pro Display": 5999.99,
}

STATUSES = ["completed", "pending", "shipped", "cancelled", "processing"]


def generate_orders(
    num_records=100,
    start_date="2024-01-01",
    end_date="2024-03-31",
    id_offset=1,
    seed=None,
):
    """랜덤 주문 데이터를 dict 리스트로 생성한다.

    Parameters
    ----------
    num_records : int
        생성할 레코드 수.
    start_date, end_date : str
        주문 날짜 범위 (YYYY-MM-DD).
    id_offset : int
        order_id 시작값.
    seed : int or None
        재현 가능한 결과를 위한 시드값.

    Returns
    -------
    list[dict]
        order_id, customer_id, product_name, order_date, amount, status 키를 가진 딕셔너리 리스트.
    """
    if seed is not None:
        random.seed(seed)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    day_range = (end - start).days

    product_names = list(PRODUCTS.keys())
    data = []
    for i in range(num_records):
        product = random.choice(product_names)
        base_price = PRODUCTS[product]
        variation = random.uniform(0.8, 1.2)
        order_date = start + timedelta(days=random.randint(0, day_range))

        data.append(
            {
                "order_id": id_offset + i,
                "customer_id": random.randint(100, 999),
                "product_name": product,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "amount": round(base_price * variation, 2),
                "status": random.choice(STATUSES),
            }
        )
    return data


def to_spark_df(spark, data):
    """dict 리스트를 Spark DataFrame으로 변환한다 (order_date를 DATE 타입으로).

    Usage::

        from utils.data_generator import generate_orders, to_spark_df
        orders = generate_orders(100)
        df = to_spark_df(spark, orders)
        df.write.format("iceberg").mode("append").saveAsTable("demo.lab.my_table")
    """
    import pandas as pd
    from pyspark.sql.functions import col

    pdf = pd.DataFrame(data)
    sdf = spark.createDataFrame(pdf)
    sdf = sdf.withColumn("order_date", col("order_date").cast("date"))
    return sdf
