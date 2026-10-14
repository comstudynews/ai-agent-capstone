# Next.js Streaming UI

This UI intentionally uses a small custom SSE parser to teach the browser transport boundary. `useChat` from Vercel AI SDK uses a **different** UI Message Stream protocol, so it cannot consume this backend's custom `event: token` frames directly. Add a protocol adapter and integration test before switching to `useChat`.

```bash
cd frontend
npm install
npm run dev
```

Check http://localhost:3000 while the FastAPI server is running at http://127.0.0.1:8000. The API allows localhost:3000 origins only.

**Prerequisite:** Node.js compatible with this Next.js major version. The npm lockfile is not committed until a connected package-registry installation can generate and validate it. Do not advertise an untested build as verified.

## Optional AI SDK tutorial route

`http://localhost:3000/ai-sdk` uses `useChat` with a FastAPI adapter at `/chat/ui-stream`. The adapter emits UI Message Stream v1 frames (`start`, `text-start`, `text-delta`, `text-end`, `finish`, `[DONE]`) rather than custom `event: token` messages. See the [official specification](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol). Backend protocol tests run offline, but the npm/Next.js build is not verified here.
