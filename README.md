# Apache Iceberg Hands-on Lab

Apache Iceberg의 아키텍처와 성능 최적화를 단계적으로 실습하는 프로젝트.

> 참고 도서: *Apache Iceberg: The Definitive Guide* (특히 Chapter 4: Optimizing the Performance of Iceberg Tables)

---

## 환경

| 구성 요소 | 버전 |
|---|---|
| PySpark | 3.4.0 |
| Iceberg | 1.4.3 (iceberg-spark-runtime JAR) |
| Catalog | Hadoop (로컬 파일시스템) |
| Jupyter | pyspark-notebook (Docker) |

```bash
docker-compose up -d
# Jupyter: http://localhost:8888 (token: iceberg)
```

---

## First-Run Checklist (필수)

아래 순서를 **반드시** 지켜서 실행합니다.

1. `docker-compose up -d`로 컨테이너를 띄운다.
2. `notebooks/0_setup/01-environment-setup.ipynb`를 처음부터 끝까지 실행한다.
3. 다음 조건이 모두 만족되는지 확인한다.
   - 패키지 설치 셀 성공 (`pyspark`, `pyarrow`, `fastavro`, `requests` 등)
   - Iceberg JAR 다운로드 완료
   - `create_spark_session()` 호출 성공
4. 위 검증이 끝난 뒤에만 `1_fundamentals` 이후 노트북을 실행한다.

> `1_fundamentals`부터 바로 실행하면 JAR/패키지 미설치로 실패할 수 있습니다.

---

## 커리큘럼

### 0_setup/ - 환경 설정

| 노트북 | 내용 |
|---|---|
| `01-environment-setup` | 패키지 설치, Iceberg JAR 다운로드, Spark 세션 동작 확인 |

---

### 1_fundamentals/ - Iceberg 구조 이해

Iceberg가 내부적으로 어떤 파일들로 구성되는지 직접 열어보고 이해한다.

| 노트북 | 핵심 질문 | 내용 |
|---|---|---|
| `01-architecture-overview` | Iceberg 테이블의 파일들은 각각 무슨 역할인가? | 3-layer 아키텍처 개요, 첫 테이블 생성, data/metadata 디렉토리 탐색 |
| `02-data-layer-deep-dive` | Parquet 파일 안에는 뭐가 들어있나? | Parquet 구조 분석, 파티션 디렉토리 레이아웃, 파일 크기/레코드 수 분석 |
| `03-metadata-layer-deep-dive` | Iceberg는 파일들을 어떻게 추적하나? | metadata.json 해부, manifest list/file 체인, column-level 통계, snapshot 구조 |

---

### 2_write_modes/ - 쓰기 방식 이해

데이터를 수정/삭제할 때 COW와 MOR이 파일을 어떻게 다르게 처리하는지 관찰한다.

| 노트북 | 핵심 질문 | 내용 |
|---|---|---|
| `01-cow-in-action` | COW에서 UPDATE 1건 하면 파일이 어떻게 바뀌나? | INSERT/UPDATE/DELETE 각 단계마다 파일 변화 추적 (전후 diff) |
| `02-mor-in-action` | MOR에서 DELETE하면 delete file에는 뭐가 기록되나? | Delete files 생성 관찰, positional delete 분석, 파일 구조 변화 |
| `03-cow-vs-mor-comparison` | 우리 워크로드에는 COW와 MOR 중 뭐가 맞나? | 동일 시나리오 비교 (파일 수, 크기, 쓰기/읽기 패턴), 선택 기준 정리 |

---

### 3_features/ - 핵심 기능

Iceberg가 제공하는 테이블 관리 기능을 실습한다.

| 노트북 | 핵심 질문 | 내용 |
|---|---|---|
| `01-time-travel` | 실수로 데이터를 날렸을 때 어떻게 복구하나? | VERSION AS OF, TIMESTAMP AS OF, rollback, 실수 복구 시나리오 |
| `02-schema-evolution` | 컬럼을 추가해도 기존 데이터는 깨지지 않나? | ADD/RENAME/ALTER COLUMN, NULL 호환성, schema history 확인 |

---

### 4_optimization/ - 성능 최적화 (핵심)

쿼리가 느린 이유를 진단하고, 단계적으로 최적화하는 방법을 익힌다.

> 이 섹션은 *The Definitive Guide* Chapter 4를 기반으로 구성.

#### 01-compaction-strategies - 파일 수 줄이기

> Ch4 Section 1 (Compaction) + Section 2 (Sorting) + Section 3 (Z-order)

| 단계 | 실습 내용 |
|---|---|
| Small File Problem | 소량 INSERT 반복 -> 파일 폭증 -> 쿼리 성능 저하 관찰 |
| **Binpack** | `strategy => 'binpack'` - 단순 병합, 가장 빠름, 정렬 없음 |
| **Sort** | `strategy => 'sort'` - 정렬 후 병합, min/max 통계 개선, 파일 프루닝 효과 |
| **Z-order** | `sort_order => 'zorder(col1, col2)'` - 다차원 정렬, 복합 필터 쿼리 최적화 |
| 타겟 컴팩션 | `where` 필터로 특정 파티션만 대상 |
| File Groups & Partial Progress | OOM 방지, 점진적 커밋으로 조기 이점 |

```
전략 비교:
Binpack  - 속도: ★★★★★  읽기 개선: ★★☆☆☆  적합: 스트리밍 SLA
Sort     - 속도: ★★★☆☆  읽기 개선: ★★★★☆  적합: 단일 필드 필터 중심
Z-order  - 속도: ★★★☆☆  읽기 개선: ★★★★★  적합: 다중 필드 필터 중심
```

#### 02-partitioning-deep-dive - 스캔 범위 줄이기

> Ch4 Section 4 (Partitioning)

| 단계 | 실습 내용 |
|---|---|
| 전통적 파티셔닝의 한계 | identity partition -> 파티션 60개 폭증, 파생 컬럼 필요 문제 |
| **Hidden Partitioning** | `PARTITIONED BY months(order_date)` - 파티션 3개로 축소, 자동 프루닝 |
| 변환 함수 | `year()`, `month()`, `day()`, `hour()`, `truncate()`, `bucket()` 비교 |
| **Partition Evolution** | year -> month 변경, 기존 데이터 유지, 새 데이터만 새 스펙 적용 |
| 메타데이터 테이블 | `table.partitions`, `table.files`로 파티션 상태 모니터링 |
| Hive vs Iceberg | 파티션 컬럼 유무, 쿼리 방식, 파티션 변경 비용 비교 |

#### 03-table-maintenance - 쓰레기 치우기

> Ch4 Section 6.2 (Rewriting Manifests) + Section 6.3 (Storage Optimization)

| 단계 | 실습 내용 |
|---|---|
| **Expire Snapshots** | `expire_snapshots` - older_than, retain_last, Time Travel과의 트레이드오프 |
| **Remove Orphan Files** | `remove_orphan_files` - dry_run으로 안전 확인, 실패한 작업의 잔해 정리 |
| **Rewrite Manifests** | `rewrite_manifests` - manifest 파일 병합 |
| 유지보수 순서 | compaction -> expire snapshots -> remove orphan files |
| 자동화 | Airflow/Dagster 스케줄링 전략, 실행 주기 가이드라인 |

#### 04-advanced-tuning - 세밀한 튜닝

> Ch4 Section 6.1, 6.4, 6.5, 6.6

| 단계 | 실습 내용 |
|---|---|
| **Metrics Collection** | none/counts/truncate(N)/full 레벨, 넓은 테이블에서 메트릭 제한 |
| **Write Distribution Mode** | none/hash/range, 파티셔닝과 분배 모드 조합 효과 |
| **Bloom Filters** | 비트 배열 + 해시 개념, 활성화 후 point lookup 성능 비교 |
| Object Storage | prefix 스로틀링 문제, `write.object-storage.enabled` |

---

### 5_practice/ - 실전 시나리오

| 노트북 | 내용 |
|---|---|
| `01-end-to-end-scenario` | 일별 배치 적재 + 상태 업데이트 + 스키마 변경 + 컴팩션 + 스냅샷 정리 + 장애 복구 |

---

## 학습 흐름

```
1_fundamentals          Iceberg가 뭔지 (구조)
       |
2_write_modes           데이터가 어떻게 써지는지 (COW/MOR)
       |
3_features              뭘 할 수 있는지 (Time Travel, Schema Evolution)
       |
4_optimization          어떻게 빠르게 만드는지
  |-- 01: 파일 수 줄이기     Compaction (binpack -> sort -> z-order)
  |-- 02: 스캔 범위 줄이기   Partitioning (hidden, transforms, evolution)
  |-- 03: 쓰레기 치우기      Maintenance (snapshots, orphans, manifests)
  |-- 04: 세밀하게 튜닝      Metrics, Distribution, Bloom filters
       |
5_practice              종합 시나리오
```

---

## 공통 유틸리티 (`utils/`)

각 노트북에서 반복되는 코드를 모듈로 분리.

| 모듈 | 역할 |
|---|---|
| `spark_setup.py` | Spark + Iceberg 세션 생성 |
| `data_generator.py` | 랜덤 주문 데이터 생성 |
| `file_explorer.py` | warehouse 디렉토리 트리 출력, 전후 diff |

```python
# 각 노트북 시작부
import sys; sys.path.append('..')
from utils.spark_setup import create_spark_session
from utils.data_generator import generate_orders
from utils.file_explorer import show_tree, diff_tree

spark = create_spark_session()
```

---

## 디렉토리 구조

```
iceberg/
├── docker-compose.yml
├── README.md
├── notebooks/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── spark_setup.py
│   │   ├── data_generator.py
│   │   └── file_explorer.py
│   ├── 0_setup/
│   │   └── 01-environment-setup.ipynb
│   ├── 1_fundamentals/
│   │   ├── 01-architecture-overview.ipynb
│   │   ├── 02-data-layer-deep-dive.ipynb
│   │   └── 03-metadata-layer-deep-dive.ipynb
│   ├── 2_write_modes/
│   │   ├── 01-cow-in-action.ipynb
│   │   ├── 02-mor-in-action.ipynb
│   │   └── 03-cow-vs-mor-comparison.ipynb
│   ├── 3_features/
│   │   ├── 01-time-travel.ipynb
│   │   └── 02-schema-evolution.ipynb
│   ├── 4_optimization/
│   │   ├── 01-compaction-strategies.ipynb
│   │   ├── 02-partitioning-deep-dive.ipynb
│   │   ├── 03-table-maintenance.ipynb
│   │   └── 04-advanced-tuning.ipynb
│   └── 5_practice/
│       └── 01-end-to-end-scenario.ipynb
└── data/
    └── warehouse/
```
