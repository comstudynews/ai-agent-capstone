"use client";
import { useMemo, useState } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export default function AISDKExample() {
  const [input, setInput] = useState("");
  const transport = useMemo(() => new DefaultChatTransport({ api: `${API}/chat/ui-stream` }), []);
  const { messages, sendMessage, status, error, stop } = useChat({ transport });
  return <main>
    <h1>AI SDK UI Message Stream 실습</h1>
    <p>커스텀 SSE와 달리 UI Message Stream v1 프로토콜을 사용합니다.</p>
    {messages.map(message => <section key={message.id}>
      <strong>{message.role === "user" ? "사용자" : "AI"}</strong>
      {message.parts.map((part, i) => part.type === "text" ? <p key={i}>{part.text}</p> : null)}
    </section>)}
    <input aria-label="질문" value={input} onChange={e => setInput(e.target.value)} />
    <button disabled={!input.trim() || status === "streaming"} onClick={() => {
      void sendMessage({ text: input }); setInput("");
    }}>전송</button>
    <button onClick={() => void stop()} disabled={status !== "streaming"}>중지</button>
    {error && <p role="alert">응답 처리에 실패했습니다.</p>}
  </main>;
}
