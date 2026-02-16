# Iceberg Review Report - R1 (2026-02-16)

## 라운드 메타
- 라운드: `R1`
- 오케스트레이터: `CDO - Review Orchestrator`
- 범위: `iceberg/README.md`, `iceberg/docs/*.md`, `iceberg/docs/apache-iceberg-TDG_ER1.pdf`, `iceberg/notebooks/**/*.ipynb`, `iceberg/notebooks/utils/*`

## P0
- 없음

## P1
1. [문제 요약] 초행 사용자에게 `0_setup` 선행 실행이 강제되지 않아 `1_fundamentals`부터 실행 시 세션/의존성 오류를 만날 가능성이 큼. [근거] 커리큘럼은 순서를 나열하지만 선행 완료 조건이 명시되지 않았고, `1_fundamentals` 초반 셀에서 바로 `create_spark_session()`을 호출한다. [수정 제안] README 상단과 각 실습 시작 셀에 `First-run checklist`를 추가하고 `notebooks/0_setup/01-environment-setup.ipynb` 완료 확인 항목을 강제한다. [심각도] P1 [대상 노트북/셀] `iceberg/README.md`, `iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb#cell-3`, `iceberg/notebooks/0_setup/01-environment-setup.ipynb#cell-2`

2. [문제 요약] JAR 다운로드 경로에서 `requests` 의존성이 누락되어 클린 환경에서 초기 셀이 실패할 수 있음. [근거] `download_iceberg_jar`는 `requests` import를 사용하지만 설치 목록에 `requests`가 포함되지 않았다. [수정 제안] `REQUIRED_PACKAGES`에 `requests`를 추가하거나 다운로드 함수 내부에서 자체 설치/대체 클라이언트를 사용하도록 수정한다. [심각도] P1 [대상 노트북/셀] `iceberg/notebooks/utils/spark_setup.py`, `iceberg/notebooks/0_setup/01-environment-setup.ipynb#cell-4`

3. [문제 요약] MOR 실습에서 Delete File 읽기 엔진 호환성 경고가 없어 실무 적용 시 잘못된 결과를 초래할 수 있음. [근거] `docs`의 MOR 설명에는 엔진 호환성 확인 필요가 있지만, MOR 실습 노트북은 생성/비교 위주로 진행되어 사전 호환성 체크가 빠져 있다. [수정 제안] MOR 실습 앞부분에 “엔진이 Delete File을 읽는지 확인” 체크리스트와 검증 절차를 추가한다. [심각도] P1 [대상 노트북/셀] `iceberg/notebooks/2_write_modes/02-mor-in-action.ipynb#cell-11`, `iceberg/notebooks/2_write_modes/03-cow-vs-mor-comparison.ipynb#cell-10`

4. [문제 요약] 중복 키(`order_id`) 유입 시나리오가 없어 현실 데이터 품질 이슈를 다루지 못함. [근거] 샘플 데이터 생성은 일관되게 고유 `order_id`만 만들고, 실습에서도 중복 충돌/정합성 회복 검증이 없다. [수정 제안] 중복 레코드 배치를 의도적으로 주입해 `MERGE`/dedup/검증 쿼리를 추가하고 스냅샷 결과 정합성을 확인한다. [심각도] P1 [대상 노트북/셀] `iceberg/notebooks/utils/data_generator.py`, `iceberg/notebooks/2_write_modes/01-cow-in-action.ipynb#cell-7`, `iceberg/notebooks/5_practice/01-end-to-end-scenario.ipynb#cell-6`

5. [문제 요약] 쓰기 실패 및 커밋 실패 후 복구(rollback/time travel) 실전 절차가 빠져 장애 대응 학습이 불충분함. [근거] 대량 INSERT/UPDATE/DELETE 경로는 성공 흐름 중심이며 실패 유도/복구 검증 셀이 없다. [수정 제안] 실패를 유도하는 데이터/스키마 시나리오를 추가하고 `VERSION AS OF` 또는 rollback 절차까지 포함한 복구 실습을 추가한다. [심각도] P1 [대상 노트북/셀] `iceberg/notebooks/2_write_modes/03-cow-vs-mor-comparison.ipynb#cell-8`

## P2
1. [문제 요약] Hidden partitioning 개념 설명보다 코드 실행이 먼저 나와 초반 학습자 이해 단절 가능성이 있음. [근거] `months(order_date)`를 사용하는 테이블 생성 셀이 개념 정의보다 앞서 등장한다. [수정 제안] 생성 셀 앞에 hidden partitioning/transform 의미와 디렉토리-메타데이터 관찰 포인트를 추가한다. [심각도] P2 [대상 노트북/셀] `iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb#cell-5`

2. [문제 요약] Advanced tuning 섹션이 “언제 이 단계로 들어와야 하는지” 기준이 약해 학습 동선이 불명확함. [근거] 다수 튜닝 레버를 소개하지만 선행 섹션 결과 기반 진입 조건이 충분히 제시되지 않는다. [수정 제안] compaction/partition/maintenance 이후에도 병목이 남을 때 진입하는 결정 트리와 증상별 적용 기준을 추가한다. [심각도] P2 [대상 노트북/셀] `iceberg/notebooks/4_optimization/04-advanced-tuning.ipynb#cell-0`

3. [문제 요약] Schema Evolution에서 `DROP COLUMN` 및 필드 ID 관련 리스크 시나리오가 누락되어 변화 비용 인지가 약함. [근거] ADD/RENAME 중심 실습이며 필드 제거 후 영향/회복 확인이 없다. [수정 제안] DROP 이후 과거 스냅샷 조회, 재추가 시 유의점, 회복 절차를 포함한 셀을 추가한다. [심각도] P2 [대상 노트북/셀] `iceberg/notebooks/3_features/02-schema-evolution.ipynb#cell-6`

4. [문제 요약] Metadata deep dive에서 Puffin 파일 설명/확인이 빠져 문서-노트북 매핑이 일부 비어 있음. [근거] metadata/manifest 체인은 상세히 다루지만 Puffin 역할과 확인 방법이 없다. [수정 제안] Puffin 파일 개념 및 확인 절차(존재 확인/용도 설명) 셀을 추가한다. [심각도] P2 [대상 노트북/셀] `iceberg/notebooks/1_fundamentals/03-metadata-layer-deep-dive.ipynb#cell-10`

5. [문제 요약] Catalog 계층의 핵심인 metadata pointer의 원자적 갱신 의미가 노트북에서 상대적으로 약하게 전달됨. [근거] PDF 기준으로 catalog 핵심 요구사항은 atomic pointer update인데, 아키텍처 실습에서 강조 수준이 낮다. [수정 제안] 3-layer 소개에 atomic pointer update와 linear history 의미를 명시하고 카탈로그별 pointer 저장 예시를 짧은 표로 보강한다. [심각도] P2 [대상 노트북/셀] `iceberg/notebooks/1_fundamentals/01-architecture-overview.ipynb#cell-1`

6. [문제 요약] 고급 튜닝에서 Puffin/Theta sketch 관점이 빠져 metadata 기반 최적화 맥락이 약함. [근거] PDF의 고급 통계 구조 설명 대비 튜닝 노트북은 해당 항목을 다루지 않는다. [수정 제안] advanced-tuning에 Puffin/Theta sketch 소개와 활용/확인 포인트를 추가한다. [심각도] P2 [대상 노트북/셀] `iceberg/notebooks/4_optimization/04-advanced-tuning.ipynb#cell-0`

## CDO 메모
- Senior DE #1(Internals Auditor)은 핵심 기술 정확성(메타데이터 체인, 스냅샷 의미, COW/MOR 기본 동작, 파티셔닝)에서 치명 오류를 보고하지 않음.
- 본 라운드는 정확성 “유지”보다 재현성/실무성/학습 전이 관점의 보강 과제가 중심임.
