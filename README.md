# 갤럭시 스마트 기기 검색 신호 알림 (테스트 케이스)

네이버 데이터랩 검색 신호로 삼성 갤럭시 4개 제품(Z플립·북·버즈·워치)과 경쟁 제품(제품당 3개)의 급등을 감지해 Slack으로 알립니다.
에스트라 알림 시스템과 같은 계산(config.json의 weights·layers·threshold만 다름)을 다른 산업에 적용해 보는 용도입니다.

- 매일 07:30 KST 실행 (.github/workflows/daily.yml), 월요일에는 주간 브리핑 포함
- 필요한 Secrets: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, SLACK_WEBHOOK_URL / Variables: PAGE_URL
- 알림 기준: config.json 의 threshold (현재 1.0)
- 한계: 연결 강도는 학습 기간·키워드풀에 따라 달라지고, 알림은 검색이 오른 시점에 같이 오는 것이며 미리 알려주지 않습니다.
