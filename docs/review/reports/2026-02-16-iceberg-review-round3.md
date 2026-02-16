# Iceberg Review Report - R3 (2026-02-16)

## 라운드 메타
- 라운드: `R3`
- 팀 구성: `docs/review/TEAM_SETUP_ROUND3.md`
- 범위: `README.md`, `.gitignore`, `notebooks/0_setup/01-environment-setup.ipynb`, `notebooks/2_write_modes/01-cow-in-action.ipynb`, `notebooks/utils/spark_setup.py`, `docs/review/*`

## P0
- 없음

## P1
1. [문제 요약] `install_packages()`의 skip 로직이 버전/extra 조건을 검증하지 않아, 의도한 의존성 사양과 다른 환경이 그대로 통과될 수 있습니다. [근거] `notebooks/utils/spark_setup.py:22`~`notebooks/utils/spark_setup.py:24`는 `pyspark==3.4.0`, `pyiceberg[pyarrow,duckdb]`를 요구하지만, 실제 skip 판단은 import 가능 여부만 확인합니다(`notebooks/utils/spark_setup.py:42`~`notebooks/utils/spark_setup.py:44`, `notebooks/utils/spark_setup.py:66`~`notebooks/utils/spark_setup.py:70`). 따라서 기존에 다른 버전의 `pyspark` 또는 extra 없는 `pyiceberg`가 설치돼 있어도 설치를 건너뛸 수 있습니다. [수정 제안] requirement 파싱(`packaging`) + 설치된 distribution 버전/extra 검증(`importlib.metadata`) 후 불일치 시 설치하도록 변경하세요. [심각도] P1 [대상 노트북/셀] `notebooks/utils/spark_setup.py:22`, `notebooks/utils/spark_setup.py:42`, `notebooks/utils/spark_setup.py:66`

2. [문제 요약] `.ipynb_checkpoints`가 이미 Git 추적 상태라, 실행만으로도 불필요한 diff/충돌 노이즈가 계속 발생합니다. [근거] `.gitignore`에는 무시 규칙이 있으나(`.gitignore:1`), 현재도 체크포인트 노트북이 추적됩니다(예: `notebooks/0_setup/.ipynb_checkpoints/01-environment-setup-checkpoint.ipynb`, `notebooks/2_write_modes/.ipynb_checkpoints/03-cow-vs-mor-comparison-checkpoint.ipynb`). [수정 제안] 기존 추적 체크포인트를 인덱스에서 제거(`git rm --cached notebooks/**/.ipynb_checkpoints/*`)하고, PR 체크리스트/CI에서 체크포인트 추적 여부를 검사하세요. [심각도] P1 [대상 노트북/셀] `notebooks/0_setup/.ipynb_checkpoints/01-environment-setup-checkpoint.ipynb`

3. [문제 요약] 실습 생성 데이터 경로(`data/warehouse`)가 ignore되지 않아 재실행 시 대량 산출물이 다시 변경 목록에 쌓일 위험이 남아 있습니다. [근거] `.gitignore`에는 `data/warehouse` 관련 규칙이 없습니다(`.gitignore:1`~`.gitignore:4`). `0_setup`은 해당 경로를 직접 탐색하며 실습 전체가 이 경로에 산출물을 생성합니다(`notebooks/0_setup/01-environment-setup.ipynb`의 warehouse 탐색 셀). 과거에도 동일 경로 산출물로 대량 변경이 발생한 이력이 있습니다. [수정 제안] `data/warehouse/`, `*.parquet`, `*.crc`(또는 경로 한정 패턴)을 `.gitignore`에 추가하고, 필요 시 샘플 데이터만 별도 fixtures로 관리하세요. [심각도] P1 [대상 노트북/셀] `.gitignore:1`, `notebooks/0_setup/01-environment-setup.ipynb`

## P2
1. [문제 요약] JAR 무결성 검증이 선택사항이라(`ICEBERG_JAR_SHA256` 미설정 시 비활성), 네트워크/미러 이상 상황에서 변조 탐지력이 낮습니다. [근거] `download_iceberg_jar`는 checksum이 주어질 때만 검증합니다(`notebooks/utils/spark_setup.py:111`~`notebooks/utils/spark_setup.py:118`). 기본 실행 경로에서는 검증 없이 다운로드가 완료될 수 있습니다. [수정 제안] 프로젝트 기본 SHA256을 코드/설정에 고정하고, 불일치 시 실패하도록 기본 동작을 강화하세요. [심각도] P2 [대상 노트북/셀] `notebooks/utils/spark_setup.py:111`, `notebooks/utils/spark_setup.py:116`

2. [문제 요약] `2_write_modes/01-cow-in-action.ipynb` 초반부에 `0_setup` 선행 실행 안내가 없어 신규 사용자가 의존성 미준비 상태로 진입할 가능성이 있습니다. [근거] 노트북 초반은 바로 `utils.spark_setup` import 및 `create_spark_session()` 호출로 진행되며(`notebooks/2_write_modes/01-cow-in-action.ipynb` Cell 3~4), 같은 수준의 선행 안내가 해당 노트북 내부에는 없습니다. [수정 제안] `## 환경 설정` 섹션에 `0_setup` 선행 체크리스트(패키지/JAR/Spark 세션 성공)를 짧게 추가하세요. [심각도] P2 [대상 노트북/셀] `notebooks/2_write_modes/01-cow-in-action.ipynb` Cell 2~4

## CDO 메모
- 역할 분산 리뷰 결과, `R2`에서 반영한 복원력 개선 방향은 유효하나, skip 로직의 사양 검증 누락과 리포지토리 산출물 관리 정책은 추가 보강이 필요합니다.
- 실행 절차 정합성은 전반적으로 개선되었지만, 노트북 단위의 선행조건 안내 일관성은 아직 섹션별 편차가 있습니다.
