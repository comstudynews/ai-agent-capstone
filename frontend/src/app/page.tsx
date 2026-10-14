"use client";
import { useRef, useState } from "react";
import { SSEParser } from "../lib/sse";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export default function Home() {
  const [question, setQuestion] = useState("payment-api 500 장애 상태를 알려주세요.");
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("질문을 입력하세요.");
  const [nodes, setNodes] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const threadId = useRef<string | null>(null);
  const abort = useRef<AbortController | null>(null);
  async function ask() {
    if (!question.trim() || busy) return;
    const controller = new AbortController();
    abort.current = controller;
    setBusy(true); setAnswer(""); setNodes([]); setStatus("연결 중");
    const parser = new SSEParser();
    let sawDone = false;
    try {
      const response = await fetch(`${API}/chat/stream`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question, thread_id: threadId.current }),
        signal: controller.signal,
      });
      if (!response.ok || !response.body) throw new Error(`HTTP ${response.status}`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          for (const item of parser.feed(decoder.decode(value, { stream: true }))) {
            const { event, payload } = item;
            if (event === "start") threadId.current = String(payload.thread_id);
            if (event === "token") setAnswer(current => current + String(payload.content ?? ""));
            if (event === "state") setNodes(current => [...current, `${payload.node}: ${payload.status}`]);
            if (event === "error") { setStatus(String(payload.message)); return; }
            if (event === "done") { sawDone = true; setStatus("완료"); }
          }
        }
      } finally { reader.releaseLock(); }
      if (!sawDone) setStatus("연결이 예기치 않게 종료되었습니다.");
    } catch (error) {
      setStatus(controller.signal.aborted ? "사용자가 중지했습니다." : String(error));
    } finally { setBusy(false); abort.current = null; }
  }
  return <main>
    <h1>ICT 운영 지원 AI Agent</h1>
    <p>가상 데이터 기반 실습입니다. 쓰기 작업은 별도 승인 API로 처리합니다.</p>
    <textarea aria-label="질문" value={question} onChange={e => setQuestion(e.target.value)} />
    <div>
      <button disabled={busy} onClick={() => void ask()}>질문</button>
      <button disabled={!busy} onClick={() => abort.current?.abort()}>중지</button>
      <button onClick={() => { threadId.current = null; setAnswer(""); setNodes([]); setStatus("새 대화"); }} disabled={busy}>새 대화</button>
    </div>
    <p aria-live="polite"><strong>상태:</strong> {status}</p>
    <h2>실행 단계</h2><ul>{nodes.map((x,i) => <li key={`${i}-${x}`}>{x}</li>)}</ul>
    <h2>응답</h2><pre aria-live="polite">{answer || "아직 답변이 없습니다."}</pre>
  </main>;
}
