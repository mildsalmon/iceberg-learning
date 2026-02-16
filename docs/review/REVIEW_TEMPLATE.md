# Iceberg Review 제출 템플릿

## 메타 정보
- 리뷰 라운드: `R1`
- 리뷰어 역할: `<CDO | Senior DE #1 | Senior DE #2 | Senior DE #3 | Senior DE #4 | Junior DE #1 | Junior DE #2>`
- 리뷰어 이름: `<name>`
- 리뷰 범위: `<경로 또는 챕터>`
- 리뷰 일시: `<YYYY-MM-DD>`

## 이슈 목록
아래 형식을 이슈마다 반복한다.

`[문제 요약] [근거] [수정 제안] [심각도] [대상 노트북/셀]`

### Issue 1
- [문제 요약] `<한 줄 요약>`
- [근거] `<재현 절차/문서 근거/PDF 근거/실행 로그>`
- [수정 제안] `<구체적 수정안>`
- [심각도] `<P0|P1|P2>`
- [대상 노트북/셀] `<예: notebooks/1_fundamentals/03-metadata-layer-deep-dive.ipynb#cell-21>`

### Issue 2
- [문제 요약] `<한 줄 요약>`
- [근거] `<재현 절차/문서 근거/PDF 근거/실행 로그>`
- [수정 제안] `<구체적 수정안>`
- [심각도] `<P0|P1|P2>`
- [대상 노트북/셀] `<예: notebooks/4_optimization/02-partitioning-deep-dive.ipynb#cell-17>`

## 역할별 체크포인트
- CDO: 중복 이슈 병합 여부, 우선순위 일관성, 최종 승인 상태
- Senior DE #1: Iceberg 내부 동작 정확성
- Senior DE #2: 학습 설계와 용어 정확성
- Senior DE #3: MD-Notebook 매핑 일치성
- Senior DE #4: PDF 기준 누락/과장/오해 소지
- Junior DE #1: 첫 실행 성공률, 설치/실행 장애
- Junior DE #2: 엣지케이스 및 운영 리스크
