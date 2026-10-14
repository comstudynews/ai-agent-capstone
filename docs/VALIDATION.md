# 실습 점검표

결과가 예상과 다른 경우 오류 메시지와 실행 환경을 확인하고 [문제 해결](TROUBLESHOOTING.md)을 참고하세요.

## 1. 기본 실습 (외부 계정 불필요)

프로젝트 루트에서:

```bash
uv run python scripts/check_env.py
uv run python -m pytest -q
uv run python -m app.lesson 1
uv run python -m app.lesson 15
```

예상: 필수 Python 라이브러리 정보가 출력되고, 자동 테스트가 통과합니다. Recipe 01에서는 6개 Capability가, Recipe 15에서는 평가 결과와 운영 장애 처리 결과가 출력됩니다.

## 2. 실제 MCP 통신 확인

```bash
uv sync --extra agent
uv run --extra agent python -m app.mcp_client
```

- [ ] Tools 목록에서 검색·모니터링·티켓 조회·티켓 생성 기능을 확인했습니다.
- [ ] Runbook Resource를 URI로 읽었습니다.
- [ ] 장애 진단 Prompt의 메시지를 읽었습니다.
- [ ] 모니터링 Tool의 가상 서비스 상태가 `DEGRADED`로 반환됩니다.

## 3. API와 SSE 확인

터미널 A: `uv run python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload`

터미널 B:

```bash
curl http://127.0.0.1:8000/health
curl -N -X POST http://127.0.0.1:8000/chat/stream -H 'Content-Type: application/json' -d '{"message":"payment-api 500 상태"}'
```

- [ ] `start` 이후 `state`/`token`, 마지막에 `done` 이벤트가 보입니다.
- [ ] 서버가 실패하면 오류와 종료 상태를 구별합니다.

## 4. 웹 UI 연결

`cd frontend && npm ci && npm run dev` 실행 후 <http://localhost:3000> 접속:

- [ ] 질문을 보내면 답변이 한 번에 나타나지 않고 점진적으로 표시됩니다.
- [ ] 새 대화 시 이전 Thread ID가 분리됩니다.
- [ ] 네트워크 연결이 끊기면 사용자에게 오류가 표시됩니다.

## 5. 추가 서비스 실습

- [ ] Qdrant: 가상 문서 색인 후 검색 결과의 `source_id`를 확인했습니다.
- [ ] PostgreSQL: 같은 Thread ID로 질문한 뒤 서버를 재시작하고 대화 상태를 복원했습니다.
- [ ] 실제 LLM: 모델이 읽기 Tool을 선택하고, 승인 없이 티켓을 생성하지 않았습니다.
- [ ] 생성 작업: 같은 `request_id`와 동일한 내용은 한 번만 생성되며, 다른 내용은 HTTP 409로 거절됩니다.
- [ ] 직접 MCP 쓰기 Tool을 호출할 때 승인 토큰이 없으면 생성이 거절됩니다.
- [ ] `inventory-api`와 `search-api`의 모니터링 결과가 서로 다르게 표시됩니다.
- [ ] 같은 Thread에서 `그 서비스 상태는?`에 이전 서비스가 적용되지만 다른 Thread에는 이전 서비스 정보가 넘어가지 않습니다.
- [ ] `티켓 상태` 질문이 티켓 검색 경로를 선택합니다.
- [ ] VectorDB 점수는 실제 검색의 관련도 점수를 사용합니다.
- [ ] 평가: 같은 질문 집합으로 수정 전후 결과를 비교했습니다.

외부 서비스를 준비하지 않았다면 해당 확인 항목은 체크하지 않고 기본 실습만 먼저 진행하세요.
