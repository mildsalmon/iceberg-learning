# R1 P1/P2 Notebook Remediation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** R1 리뷰에서 나온 P1/P2 개선사항을 노트북/유틸/README에 반영해 재현성, 실무성, 학습 전이를 강화한다.

**Architecture:** 변경은 세 축으로 나눈다. (1) 실행 재현성(README + setup util), (2) 기술/실무 정확성(MOR 호환성, 실패 복구, 중복 데이터), (3) 학습 흐름 강화(개념 선행 설명, decision tree, Puffin/카탈로그 핵심 보강). 노트북은 셀 단위로 최소 수정하여 기존 실행 흐름을 유지한다.

**Tech Stack:** Markdown, Jupyter Notebook(JSON), PySpark SQL, Iceberg system procedures

---

### Task 1: First-Run 온보딩 게이트 추가

**Files:**
- Modify: `iceberg/README.md`
- Modify: `iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb`

**Step 1: README에 선행 조건 섹션 추가**
- `0_setup` 선실행, 검증 기준(JAR 존재, Spark session 생성 성공), 최소 요구사항을 추가한다.

**Step 2: 아키텍처 노트북에 선행 실행 안내 삽입**
- 환경 설정 앞 셀에 `0_setup` 미완료 시 중단 안내를 추가한다.

**Step 3: 확인**
- Run: `rg -n "First-run|0_setup|선행" iceberg/README.md iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb`
- Expected: 신규 안내 문구가 검색된다.

### Task 2: setup 의존성 보강 (`requests`)

**Files:**
- Modify: `iceberg/notebooks/utils/spark_setup.py`
- Modify: `iceberg/notebooks/0_setup/01-environment-setup.ipynb`

**Step 1: 패키지 목록 보강**
- `REQUIRED_PACKAGES`에 `requests`를 추가한다.

**Step 2: setup 노트북 안내 업데이트**
- 패키지 설치 셀 설명에 다운로드 의존성 포함 사실을 명시한다.

**Step 3: 확인**
- Run: `rg -n "requests" iceberg/notebooks/utils/spark_setup.py iceberg/notebooks/0_setup/01-environment-setup.ipynb`
- Expected: util + setup notebook 모두에서 확인된다.

### Task 3: 3-Layer 설명 강화 (Hidden Partitioning + Atomic Pointer)

**Files:**
- Modify: `iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb`

**Step 1: Hidden Partitioning 선행 설명 추가**
- `PARTITIONED BY (months(order_date))` 실행 전에 transform 의미와 관찰 포인트를 서술한다.

**Step 2: Catalog Layer 핵심 요구사항 보강**
- metadata pointer atomic update, linear history, 카탈로그별 포인터 저장 예시를 명시한다.

**Step 3: 확인**
- Run: `rg -n "atomic|pointer|Hidden Partitioning|months\\(order_date\\)" iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb`
- Expected: 핵심 키워드가 노트북 내 존재한다.

### Task 4: MOR 멀티엔진 호환성 경고 반영

**Files:**
- Modify: `iceberg/notebooks/2_write_modes/02-mor-in-action.ipynb`
- Modify: `iceberg/notebooks/2_write_modes/03-cow-vs-mor-comparison.ipynb`

**Step 1: MOR 노트북 경고/체크리스트 추가**
- Delete File reader 지원 여부를 엔진별로 확인해야 한다는 경고를 추가한다.

**Step 2: 비교 노트북에 운영 체크포인트 추가**
- COW/MOR 선택 가이드에 엔진 호환성 점검 항목을 삽입한다.

**Step 3: 확인**
- Run: `rg -n "Delete File|호환성|Trino|Flink|엔진" iceberg/notebooks/2_write_modes/02-mor-in-action.ipynb iceberg/notebooks/2_write_modes/03-cow-vs-mor-comparison.ipynb`
- Expected: 경고/체크리스트 문구가 검색된다.

### Task 5: Duplicate Key 엣지케이스 실습 추가

**Files:**
- Modify: `iceberg/notebooks/2_write_modes/01-cow-in-action.ipynb`
- Modify: `iceberg/notebooks/5_practice/01-end-to-end-scenario.ipynb`

**Step 1: 중복 `order_id` 주입 예시 추가**
- 소규모 중복 데이터를 append 후 중복 존재를 확인한다.

**Step 2: 정리(De-dup) 절차 추가**
- `MERGE` 또는 윈도우 기반 dedup/overwrite 시나리오로 정리하고 결과 검증을 추가한다.

**Step 3: 확인**
- Run: `rg -n "duplicate|중복|de-dup|MERGE" iceberg/notebooks/2_write_modes/01-cow-in-action.ipynb iceberg/notebooks/5_practice/01-end-to-end-scenario.ipynb`
- Expected: 중복 주입 + 정리 + 검증 흐름이 검색된다.

### Task 6: 실패 주입 및 복구 절차 (COW/MOR 비교 노트북)

**Files:**
- Modify: `iceberg/notebooks/2_write_modes/03-cow-vs-mor-comparison.ipynb`

**Step 1: 실패 유도 섹션 추가**
- 의도적 스키마 불일치 append 등 실패를 재현한다.

**Step 2: 복구/재시도 가이드 추가**
- 스냅샷 확인, `VERSION AS OF` 검증, rollback 혹은 안전 재시도 경로를 제시한다.

**Step 3: 확인**
- Run: `rg -n "실패|recovery|rollback|VERSION AS OF|예외" iceberg/notebooks/2_write_modes/03-cow-vs-mor-comparison.ipynb`
- Expected: 실패-복구 시퀀스가 검색된다.

### Task 7: Schema Evolution Drop Column 리스크 실습

**Files:**
- Modify: `iceberg/notebooks/3_features/02-schema-evolution.ipynb`

**Step 1: `DROP COLUMN` 시나리오 추가**
- 컬럼 제거 전후 스키마/조회 차이를 확인한다.

**Step 2: Time Travel과 연결**
- 이전 스냅샷에서 제거 컬럼 조회 가능함을 보여준다.

**Step 3: 확인**
- Run: `rg -n "DROP COLUMN|Time Travel|VERSION AS OF|field ID" iceberg/notebooks/3_features/02-schema-evolution.ipynb`
- Expected: drop 리스크 및 복구 관찰 포인트가 존재한다.

### Task 8: Metadata/Puffin + Advanced Tuning 진입 기준 보강

**Files:**
- Modify: `iceberg/notebooks/1_fundamentals/03-metadata-layer-deep-dive.ipynb`
- Modify: `iceberg/notebooks/4_optimization/04-advanced-tuning.ipynb`

**Step 1: Metadata 노트북에 Puffin 개념 추가**
- Puffin(Theta sketch 포함) 역할과 실습 범위(개념 중심)를 명시한다.

**Step 2: Advanced Tuning decision tree 추가**
- compaction/partitioning/maintenance 이후에도 병목이 남을 때 진입하도록 흐름을 명확화한다.

**Step 3: 고급 통계 항목 보강**
- Puffin/Theta sketch를 튜닝 레버 맥락에 포함한다.

**Step 4: 확인**
- Run: `rg -n "Puffin|Theta|decision tree|진입 기준|DataSketches" iceberg/notebooks/1_fundamentals/03-metadata-layer-deep-dive.ipynb iceberg/notebooks/4_optimization/04-advanced-tuning.ipynb`
- Expected: 관련 설명이 추가되어 검색된다.

### Final Verification

**Step 1: JSON 유효성 검사**
- Run: `python3 - <<'PY'\nimport json,glob\npaths=glob.glob('iceberg/notebooks/**/*.ipynb', recursive=True)\nfor p in paths:\n    json.load(open(p, encoding='utf-8'))\nprint(f'validated {len(paths)} notebooks')\nPY`
- Expected: 모든 노트북 파싱 성공

**Step 2: 변경 범위 확인**
- Run: `git -C iceberg status --short`
- Expected: 계획된 파일만 수정되어 있다.

