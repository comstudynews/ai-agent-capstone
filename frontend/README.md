# Next.js Streaming UI

This UI intentionally uses a small custom SSE parser to teach the browser transport boundary. `useChat` from Vercel AI SDK uses a **different** UI Message Stream protocol, so it cannot consume this backend's custom `event: token` frames directly. Add a protocol adapter and integration test before switching to `useChat`.

```bash
cd frontend
npm install
npm run dev
```

Check http://localhost:3000 while the FastAPI server is running at http://127.0.0.1:8000. The API allows localhost:3000 origins only.

**Prerequisite:** Node.js compatible with this Next.js major version. The npm lockfile is not committed until a connected package-registry installation can generate and validate it. Do not advertise an untested build as verified.
