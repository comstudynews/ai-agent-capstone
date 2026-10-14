# AI Agent Capstone — 실전 AI 서비스 개발 Cookbook

MCP · RAG · LangGraph · FastAPI · Next.js로 가상의 IT 운영 지원 AI 서비스를 단계별로 만들어 봅니다. 먼저 API Key 없이 프로그램의 구조를 익히고, 이후 실제 MCP 통신과 LLM을 연결합니다.

## 시작 전에 알아둘 점

- 모든 명령은 별도 안내가 없다면 **프로젝트 최상위 폴더**(`ai-agent-capstone/`)에서 입력합니다.
- **기본 실습**: 가상 데이터와 Python 프로그램으로 입출력·HTTP·SSE 원리를 확인합니다. 실제 LLM이나 MCP 호출과 구별합니다.
- **연동 실습**: MCP SDK, 모델 API, VectorDB, PostgreSQL, Next.js를 개별적으로 연결하여 확인합니다. 연결하려는 서비스에 따라 인터넷·API Key·Docker·Node.js가 필요합니다.
- 예제 데이터만 사용하고, `.env`·API Key·개인 정보는 GitHub에 올리지 않습니다.

## 1. 개발 도구 확인

먼저 [Python 3.11](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads), [uv](https://docs.astral.sh/uv/getting-started/installation/)를 설치합니다. 웹 UI 및 Inspector를 사용하려면 Node.js 22.19 이상을 권장합니다.

```bash
python --version
uv --version
git --version
node --version
npm --version
```

**Windows:** `python` 대신 `py -3.11`을 사용할 수 있습니다. `uv`가 설치되지 않았다면 [공식 설치 절차](https://docs.astral.sh/uv/getting-started/installation/)를 운영체제에 맞게 먼저 진행하고 터미널을 다시 엽니다.

## 2. 프로젝트 다운로드와 uv 가상환경

```bash
git clone https://github.com/comstudynews/ai-agent-capstone.git
cd ai-agent-capstone
uv python install 3.11
uv sync --python 3.11 --group dev
uv run python scripts/check_env.py
uv run python -m pytest -q
uv run python -m app.lesson 1
```

`uv sync`는 `pyproject.toml`의 의존성을 설치하고 `.venv` 가상환경을 만듭니다. 패키지 다운로드를 위한 인터넷이 필요합니다. 생성된 `uv.lock`은 **잠금 파일 생성 이후**에 사용하므로, 첫 설치에서 패키지 해결 시간이 걸릴 수 있습니다. 명령이 실패하면 오류 내용을 읽고 [문제 해결 표](docs/TROUBLESHOOTING.md)를 확인합니다.

**정상 결과:** `pytest` 테스트가 성공하고, Recipe 01에서 Tool·Resource·Prompt 기능 목록이 JSON으로 출력됩니다. 이는 기초 실습 결과입니다.

> 이후 명령은 `uv run ...`을 사용합니다. 매번 `source .venv/bin/activate`를 입력할 필요가 없습니다.

## 3. FastAPI 실행 (터미널 두 개)

**터미널 A** — 프로젝트 루트에서 서버 실행:

```bash
uv run python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

**터미널 B** — 같은 프로젝트 루트에서 확인:

```bash
curl http://127.0.0.1:8000/health
```

정상 응답 예: `{"status":"ok","mode":"demo"}`. 브라우저에서 <http://127.0.0.1:8000/docs>를 열고 `POST /chat`에 `{"message":"payment-api 500 상태"}`를 입력해 봅니다. 터미널 A는 실행 상태로 두고, 종료할 때는 `Ctrl+C`를 누릅니다.

## 4. 실제 MCP 서버·클라이언트 통신 확인

MCP는 HTTP API 서버와 별개입니다. 여기서는 **stdio 기반 MCP Client가 MCP Server 자식 프로세스를 자동으로 시작**합니다.

```bash
uv sync --python 3.11 --group dev --extra agent
uv run --extra agent python -m app.mcp_client
```

성공하면 `tools`, `resource`, `prompt`, `tool_result` 값이 출력됩니다. Tool 4개, Runbook Resource, 진단 Prompt, 가상 모니터링 결과를 확인합니다. 티켓 생성 Tool은 서명된 승인 토큰이 없으면 실행되지 않습니다.

**서버만 직접 실행해 보기(선택):**

```bash
uv run --extra agent python -m app.mcp_server
```

이 명령은 stdio의 입력을 기다릴 수 있어 **화면에 아무것도 표시되지 않아도 오류가 아닙니다**. 일반 HTTP 서버처럼 포트를 열지 않습니다. `Ctrl+C`로 종료합니다. 실제 기능 테스트는 앞의 Client 명령으로 진행합니다.

**Inspector에서 확인(선택):**

```bash
npx -y @modelcontextprotocol/inspector uv run --extra agent python -m app.mcp_server
```

Inspector가 안내하는 접속 주소를 브라우저로 열고 `Connect`한 다음 `Tools`, `Resources`, `Prompts`를 차례대로 선택합니다. `read_monitoring_status`의 인수 `service`에 `payment-api`를 입력하면 상태 `DEGRADED`를 확인할 수 있습니다. Inspector 명령은 Node.js와 패키지 다운로드가 필요합니다.

**혼동하지 마세요:** `uv run python -m app.lesson 2`는 MCP **형태를 익히는 가상 데이터 실습**이고, `uv run --extra agent python -m app.mcp_client`가 **실제 MCP 프로토콜 연결 실습**입니다.

## 5. 웹 채팅 UI 실행

**터미널 C** — 서버와 별도 터미널에서:

```bash
cd frontend
npm install
npm run dev
```

<http://localhost:3000>에서 질문하고 응답을 확인합니다. `.env`에 실제 키가 없어도 기본 실습 화면은 사용할 수 있습니다. **Next.js와 AI SDK는 Node.js/npm 버전 호환성을 먼저 확인**합니다. 브라우저 접속이 어려울 경우 FastAPI `/docs`에서 먼저 확인합니다.

## 6. 고급 연동으로 확장

1. LLM: `uv sync --extra agent` 후 `.env`에 `AGENT_MODE=llm`, 사용 가능한 `OPENAI_MODEL` 및 본인 `OPENAI_API_KEY`를 설정합니다. 인증정보는 코드·스크린샷에 넣지 않습니다.
2. RAG: Qdrant를 실행하고 `uv sync --extra rag` 후 `uv run --extra rag python scripts/index_rag.py`로 가상 문서를 색인합니다. 
3. 상태 영속화: PostgreSQL을 실행하고 `uv sync --extra persistence`, `.env`의 `CHECKPOINT_MODE=postgres` 및 `DATABASE_URL`을 설정합니다.
4. 오류·실행 검증: [환경 및 오류 해결](docs/TROUBLESHOOTING.md)과 [실습 점검표](docs/VALIDATION.md)를 확인합니다.

각 외부 연동은 준비한 패키지·서버·키가 필요하므로, 개별 실습의 실행 결과를 확인하고 다음 단계로 넘어갑니다. 기본 실습 성공만으로 모든 외부 연동까지 실행되었다고 판단하지 않습니다.

## 7. 서비스별 질문과 후속 질문 확인

API 서버를 실행한 뒤 \`/docs\`의 \`POST /chat\`에서 다음 순서로 실습합니다. 같은 대화에 대해서는 \`thread_id\`를 동일하게 입력하세요.

1. \`inventory-api 상태\`: 상태가 \`OK\`로 표시되는지 확인합니다.
2. \`search-api 상태\`: 상태가 \`DEGRADED\`로 표시되는지 확인합니다.
3. 2번에서 사용한 \`thread_id\`로 \`그 서비스 상태는?\`을 묻습니다. \`search-api\`가 이어지는지 확인합니다.
4. 새로운 \`thread_id\`로 같은 질문을 보내면 서비스명을 묻는지 확인합니다.
5. \`티켓 상태 알려줘\`는 서비스 장애가 아니라 티켓 조회로 분류됩니다.

티켓 생성은 \`/tickets/approve\`와 개인 실습용 \`DEMO_ADMIN_KEY\`가 있어야 실행됩니다. 동일한 \`request_id\`로 같은 내용을 반복하면 새 티켓을 만들지 않고, 같은 ID로 다른 내용을 보내면 HTTP 409 오류를 반환합니다.

## 8. Recipe별 학습

각 장의 [단계별 Recipe](steps)는 `uv run python -m app.lesson N`(N=1~15)으로 작은 결과를 먼저 확인합니다. 이후 `steps/stepNN/README.md`에서 코드 파일, 통합 확인 방법, 오류를 해결하는 순서를 따라갑니다. 공통 코드는 `app/`에서 함께 사용됩니다.

- [전체 프로그램의 동작 원리](docs/ARCHITECTURE.md)
- [단계별 학습 방법](docs/LEARNING_GUIDE.md)
- [문제 해결](docs/TROUBLESHOOTING.md)
- [실습 점검표](docs/VALIDATION.md)
