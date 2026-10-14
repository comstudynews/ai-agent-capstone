# Recipe 02. MCP Server와 Inspector

## 1. 무엇을 배우는가?
MCP Server가 Host에 기능을 알리는 방식과 Tool·Resource·Prompt 호출 과정을 구분합니다.

## 2. 시작 전 확인
- 이전 Recipe를 실행했고 프로젝트 폴더 `ai-agent-capstone/`에 있는지 확인합니다.
- 외부 계정이 없어도 기본 예제를 실행할 수 있습니다.
- 문제가 생기면 [공통 문제 해결 가이드](../../docs/TROUBLESHOOTING.md)를 참고합니다.

## 3. 가장 작은 예제부터 실행

```bash
uv run python -m app.lesson 2
```

**예상되는 출력의 핵심 키:** `manual, runbook`. 출력 내용을 보고 이 단계에서 무엇을 배웠는지 한 문장으로 설명해 보세요.

같은 예제의 실행 파일을 별도로 확인하려면 다음 명령을 사용합니다.

```bash
uv run python -m steps.step02.complete
```

**주의:** 실제 MCP 통신은 아래 별도 명령을 실행해야 합니다.

## 4. 코드 읽기

[`app/mcp_server.py`](../../app/mcp_server.py) 파일을 열고 입력값, 반환값, 변경되는 상태가 무엇인지 찾아봅니다. 화면에 나온 결과와 소스코드의 함수가 어떻게 연결되어 있는지 확인하세요.

## 5. 응용 연습

Runbook 하나를 선택하여 Resource URI와 반환 문자열을 비교하세요.

## 6. 오류 해결·완료 확인

- [ ] 명령을 프로젝트 폴더에서 실행했습니다.
- [ ] 예제 출력에서 `manual, runbook` 항목을 찾았습니다.
- [ ] 해당 함수를 읽고 입력과 출력을 설명할 수 있습니다.
- [ ] 예제 값을 바꾼 뒤 다시 실행했습니다.

전체 프로젝트 연결 과정은 [교재 제1장](https://app.notion.com/p/3f991bd5a9ac817a87bfd13dc433069c)에서 확인합니다.

[이전 단계](../step01/README.md) · [전체 Recipe 목차](../../README.md) · [다음 단계](../step03/README.md)

## 7. 실제 MCP 연결까지 확인하기

기본 예제에 성공했다면 다음 명령으로 실제 MCP 프로토콜을 사용합니다.

```bash
uv sync --extra agent
uv run --extra agent python -m app.mcp_client
```

**예상:** Tool 목록 4개, Resource, Prompt, 모니터링 상태 `DEGRADED`가 출력됩니다. Client가 MCP Server를 자동 시작하므로 별도 서버 실행은 필요 없습니다.

Inspector 화면에서 검사하려면:

```bash
npx -y @modelcontextprotocol/inspector uv run --extra agent python -m app.mcp_server
```

Inspector 브라우저 화면에서 Tools, Resources, Prompts를 하나씩 눌러 검증합니다.
