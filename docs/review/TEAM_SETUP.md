# Iceberg 디렉토리 리뷰 팀 설정

## 목적
- `iceberg/` 하위 노트북과 문서의 기술 정확성, 학습 완성도, 재현성, 실무 적합성을 다각도로 검증한다.
- 중복 지적을 줄이고, 우선순위(P0/P1/P2) 기반으로 수정 대상을 빠르게 확정한다.

## 최종 팀 구성 (7명)
| 역할 | 담당자 | 책임 범위 |
|---|---|---|
| CDO | Review Orchestrator | 모든 의견 취합/조율, 충돌 의사결정, P0/P1/P2 우선순위 확정, 최종 리포트 승인 |
| Senior DE #1 | Iceberg Internals Auditor | 노트북의 Iceberg 기술 정확성 검증 (metadata, snapshot, COW/MOR, partitioning) |
| Senior DE #2 | Data Education Architect | 학습 흐름/난이도/용어 정의/챕터 연결성 개선 |
| Senior DE #3 | MD Reflection Auditor | `docs/*.md` 내용이 노트북에 정확히 반영됐는지 매핑 검토 |
| Senior DE #4 | PDF Source-of-Truth Reviewer | `docs/apache-iceberg-TDG_ER1.pdf` 기준 누락/보강 포인트 제안 |
| Junior DE #1 | First-run Repro Tester | 초행 사용자 관점에서 환경 설정~셀 실행 재현성 점검 |
| Junior DE #2 | Edge-case Hunter | 스키마 변경, null/중복, 실패 복구, 성능 저하 등 엣지케이스 점검 |

## 공통 제출 포맷
아래 5개 항목을 순서대로 반드시 포함한다.

`[문제 요약] [근거] [수정 제안] [심각도] [대상 노트북/셀]`

## 심각도 정의
- `P0`: 기술적으로 잘못된 내용, 실행 불가/재현 불가, 데이터 손상/오해를 유발할 가능성이 큰 문제
- `P1`: 학습 흐름 단절, 설명 누락/불명확, 성능 해석 오류, 실무 적용 시 오작동 가능성이 있는 문제
- `P2`: 표현/가독성/구조 개선, 예시 보강, 부가 설명 개선

## 리뷰 범위
- 노트북: `notebooks/**/*.ipynb`
- 문서: `docs/**/*.md`
- 원문 기준서: `docs/apache-iceberg-TDG_ER1.pdf`
- 실행 환경: `docker-compose.yml`, `README.md`, `notebooks/utils/*`

## 운영 절차
1. CDO가 리뷰 라운드 시작 시점과 대상 범위를 확정한다.
2. 6명의 리뷰어가 역할별로 독립 리뷰를 수행한다.
3. CDO가 중복 이슈를 병합하고 충돌 의견을 조정한다.
4. CDO가 P0/P1/P2 우선순위를 확정하고 최종 리포트를 승인한다.

## 최종 리포트 규칙
- 저장 위치: `docs/review/reports/`
- 파일명: `YYYY-MM-DD-iceberg-review-round<N>.md`
- 정렬 순서: `P0 -> P1 -> P2`
- 각 이슈는 공통 제출 포맷을 그대로 유지한다.

## 셀 참조 규칙
- 가능한 경우 셀 번호를 명시한다.
- 표기 예시: `notebooks/2_write_modes/01-cow-in-action.ipynb#cell-12`
- 셀 번호 확인이 어려우면 섹션 제목/코드 스니펫 키워드를 함께 기록한다.
