# Iceberg 2차 리뷰 (2026-02-16)

검토 범위:
- `README.md`
- `docker-compose.yml`
- `notebooks/utils/spark_setup.py`
- 수정/핵심 노트북 실행 스모크 (`0_setup`, `1_fundamentals`, `2_write_modes`, `3_features`, `4_optimization`, `5_practice`)

실행 근거:
- 컨테이너: `iceberg-jupyter`
- 스모크 실행 시점: 2026-02-16
- 관찰된 대표 실패: `pyspark==3.4.0` 설치 단계 hash mismatch -> 이후 노트북 `ModuleNotFoundError: pyspark`

---

[문제 요약]
0_setup의 런타임 패키지 설치는 외부 네트워크/패키지 인덱스 상태에 따라 간헐 실패 가능성이 있습니다.

[근거]
- `notebooks/0_setup/01-environment-setup.ipynb` Cell 2에서 `install_packages()`를 무조건 실행합니다.
- `notebooks/utils/spark_setup.py:25`~`notebooks/utils/spark_setup.py:30`는 각 패키지를 `pip install -q`로 즉시 설치합니다.
- 2026-02-16 1차 스모크에서는 `pyspark==3.4.0` 설치 중 hash mismatch가 관찰되었습니다.
- 같은 환경 재검증(2026-02-16)에서 `pip install -q pyspark==3.4.0` 2회 연속 성공하여, 고정 재현 결함은 아님을 확인했습니다.

[수정 제안]
- `install_packages()`를 "필요 시 설치"로 바꿔 `import` 가능하면 skip하도록 변경.
- 설치 실패 시 즉시 종료하지 말고 에러 원인/복구 가이드를 출력(재시도 옵션 포함).
- 장기적으로는 Docker 이미지에 필수 패키지를 bake-in 하거나, 검증된 `requirements.lock` 기반 설치로 전환.

[심각도]
P2

[대상 노트북/셀]
- `notebooks/0_setup/01-environment-setup.ipynb` Cell 2
- `notebooks/utils/spark_setup.py:25`

---

[문제 요약]
`__pycache__/*.pyc`가 Git에 추적되어 로컬 실행만으로도 불필요 diff가 발생합니다.

[근거]
- 현재 변경: `notebooks/utils/__pycache__/file_explorer.cpython-310.pyc`, `notebooks/utils/__pycache__/spark_setup.cpython-310.pyc`
- 추적 파일: `notebooks/utils/__pycache__/__init__.cpython-310.pyc` 등 다수
- `.gitignore`에 `**/__pycache__/`가 추가되어도(`.gitignore:3`), 이미 추적 중인 `.pyc`는 계속 변경 대상으로 남습니다.

[수정 제안]
- 기존 추적 `.pyc`를 `git rm --cached notebooks/utils/__pycache__/*.pyc`로 인덱스에서 제거.
- 필요 시 `.gitignore`에 `*.pyc`를 추가해 디렉토리 외 위치의 바이트코드도 방지.

[심각도]
P1

[대상 노트북/셀]
- `notebooks/utils/__pycache__/file_explorer.cpython-310.pyc`
- `notebooks/utils/__pycache__/spark_setup.cpython-310.pyc`
- `.gitignore:3`

---

[문제 요약]
JAR 다운로드 경로가 네트워크 장애에 취약하며, 실패 시 원인 식별이 어렵습니다.

[근거]
- `notebooks/utils/spark_setup.py:43`에서 `requests.get(url)`에 timeout/retry가 없습니다.
- `notebooks/utils/spark_setup.py:45`~`notebooks/utils/spark_setup.py:46`에서 다운로드 본문을 바로 파일에 기록하며, checksum 검증이 없습니다.

[수정 제안]
- `requests.get(..., timeout=(5, 60))` + 재시도(backoff) 적용.
- 다운로드 후 SHA256 검증 추가.
- 실패 시 URL/HTTP 코드/재시도 횟수/다음 액션을 포함한 에러 메시지 제공.

[심각도]
P2

[대상 노트북/셀]
- `notebooks/utils/spark_setup.py:33`
