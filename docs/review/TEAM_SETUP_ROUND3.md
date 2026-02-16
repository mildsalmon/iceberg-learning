# Iceberg Review Team Setup - Round 3 (2026-02-16)

## 최종 팀 구성 (7명, 신규 편성)
1. CDO - Review Orchestrator  
역할: 리뷰 범위 고정, 역할 간 충돌 조율, P0/P1/P2 우선순위 최종 확정, 라운드 리포트 승인.

2. Principal DE #1 - Runtime Reliability Lead  
역할: `notebooks/utils/spark_setup.py` 및 `0_setup` 실행 경로의 재현성/회귀 리스크 점검.

3. Principal DE #2 - Supply-chain Security Lead  
역할: 패키지 설치 및 JAR 다운로드 경로의 무결성/보안 리스크 점검.

4. Senior DE #1 - Docs-Execution Consistency Reviewer  
역할: `README.md`, `docker-compose.yml`, `0_setup` 노트북 간 실행 절차 정합성 검증.

5. Senior DE #2 - Learning Flow Reviewer  
역할: 선행 학습/의존성 안내 누락 여부와 사용자 실패 유발 구간 검토.

6. Senior DE #3 - Repo Hygiene Reviewer  
역할: 추적 중인 생성 산출물, `.gitignore` 정책, 리뷰 산출물 관리 품질 점검.

7. Junior DE #1 - Evidence Verifier  
역할: 에이전트 주장에 대한 최소 증거 수집(`git ls-files`, 핵심 파일 라인 검증) 지원.

## 공통 제출 포맷
[문제 요약] [근거] [수정 제안] [심각도] [대상 노트북/셀]
