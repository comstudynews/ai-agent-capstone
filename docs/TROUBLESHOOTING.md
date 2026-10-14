# 문제 해결 — 먼저 확인할 곳

실습 명령은 `ai-agent-capstone/` 최상위 폴더에서 실행합니다. 문제가 생기면 오류 메시지의 **처음 발생한 원인**을 먼저 확인하세요.

| 증상 | 확인 순서 |
| --- | --- |
| `uv: command not found` | [공식 설치 방법](https://docs.astral.sh/uv/getting-started/installation/) 확인 → 새 터미널 열기 → `uv --version` |
| `python` 실행 실패 | `uv python install 3.11` → `uv run python --version` |
| `No module named pytest` | `uv sync --group dev` → `uv run python -m pytest -q` |
| `No module named mcp` | `uv sync --extra agent` → `uv run --extra agent python -m app.mcp_client` |
| MCP Server에 아무 출력이 없음 | 정상일 수 있습니다. stdio는 메시지를 기다립니다. MCP Client로 검증하세요. |
| Inspector 설치 또는 연결 실패 | Node.js 22.19 이상 및 네트워크 확인 → Inspector에서 Start/Connect → stderr 로그 확인 |
| MCP 표준출력 오류 | MCP 서버 내부 `print()`가 프로토콜을 방해하는지 확인. 로그는 stderr로 보냅니다. |
| Qdrant 연결 실패 | Qdrant가 실행 중인지, `QDRANT_URL`과 컬렉션 이름이 같은지 확인 |
| PostgreSQL 연결 거부 | 포트 5432 충돌, `DATABASE_URL`, 계정 및 권한 확인 |
| FastAPI 8000 충돌 | 다른 터미널의 서버를 종료하거나 포트를 변경 |
| 브라우저 CORS 오류 | Next.js 3000 / FastAPI 8000이 실행 중인지, 요청 Origin 확인 |
| SSE 답변이 마지막에 몰림 | `curl -N`, 브라우저 Network, 프록시 버퍼링 확인 |
| LLM 401/429 | API Key 및 모델 권한·요금제·Rate Limit 확인 |

## MCP 서버 직접 실행과 Client 실행 구분

**서버 직접 실행:** `uv run --extra agent python -m app.mcp_server`는 stdio 요청을 기다립니다. 이 상태에서 `curl localhost:포트`를 사용하는 것은 올바른 검사법이 아닙니다.

**실제 연결 확인:** `uv run --extra agent python -m app.mcp_client`는 Client가 서버 프로세스를 **자동 실행**하고 Tool·Resource·Prompt를 호출한 뒤 종료합니다. 별도 서버 터미널이 필요하지 않습니다.

**Inspector:** `npx -y @modelcontextprotocol/inspector uv run --extra agent python -m app.mcp_server`로 화면에서 Tool을 선택하고 인수를 입력합니다.

## 자격증명·데이터 주의

실제 API Key 또는 비밀번호를 명령 실행 화면·오류 스크린샷·공개 코드에 포함하지 않습니다. 티켓 생성 API는 학습용 로컬 예제이며 공용 서버에 노출하지 않습니다.
