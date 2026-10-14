# 단계별 학습 방법

모든 Recipe는 **① 왜 필요한가 → ② 동작 원리 → ③ 작은 실행 → ④ 소스 확인 → ⑤ 서비스 연결 → ⑥ 오류 해결** 순서입니다.

## 명령어를 따라 할 때

1. 프로젝트 루트에서 새 터미널을 엽니다.
2. `uv run python -m app.lesson N`에서 N을 오늘 학습할 Recipe 번호(1~15)로 바꿉니다.
3. 출력에서 가장 중요한 키(`tools`, `route`, `events`, `answer` 등)를 찾아 의미를 설명합니다.
4. 각 `steps/stepNN/README.md`에 적힌 코드 파일을 열어 입력과 반환값을 확인합니다.
5. 같은 질문으로 FastAPI API까지 연결한 뒤 출력이 일치하는지 비교합니다.
6. 예제 데이터를 한 개 변경한 후 결과가 예상과 같게 바뀌는지 확인합니다.
7. 막히면 [문제 해결](TROUBLESHOOTING.md)에서 가장 비슷한 증상을 확인합니다.

## 난이도를 천천히 올리는 기준

| 단계 | 먼저 해볼 작은 결과 | 확장 실습 |
| --- | --- | --- |
| MCP | 기능 6개 분류 | 실제 stdio Tool·Resource·Prompt 호출 |
| API | `/health` | MCP Client·LLM·RAG |
| SSE | Token 이벤트 한 개 | 브라우저 스트리밍과 연결 종료 |
| 관측·평가 | 규칙 기반 평가 | LLM·Tool의 Trace 분석 |
| 상태 | SQLite 기반 기록 | PostgreSQL Graph Checkpointer |
| Routing | 조건문 분기 | 실제 Tool 연결 그래프 |
| Planning | 횟수 제한된 계획 | 실행 결과에 따른 계획 변경 |

**중요:** API Key 없이 실행한 가상 실습은 실제 MCP 또는 LLM 통신이 아닙니다. 실제 기능을 사용하려면 해당 Recipe에서 안내한 외부 서비스 설치·연결 확인이 필요합니다.
