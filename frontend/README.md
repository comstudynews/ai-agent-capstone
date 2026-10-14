# Next.js 채팅 화면 실행하기

먼저 프로젝트 루트에서 FastAPI 서버를 실행하세요.

```bash
uv run python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

**다른 터미널**에서 프론트엔드 폴더로 이동합니다.

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 <http://localhost:3000>에 접속한 뒤 예제 질문을 입력합니다.

- 답변이 점진적으로 출력되면 SSE의 전송 결과를 확인한 것입니다.
- 오류가 나오면 FastAPI 서버 실행 여부, 포트 8000·3000, CORS 설정을 차례대로 확인하세요.
- `/ai-sdk`는 AI SDK의 메시지 스트림 형식과 일반 SSE의 차이를 살펴보는 응용 실습입니다.

Node.js 22.19 이상을 권장하며, 설치된 Node.js·npm에 따라 패키지 요구 버전을 확인하세요.
