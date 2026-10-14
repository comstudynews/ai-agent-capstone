"""Versioned SSE contract, safe with partial network chunks."""
import json
from dataclasses import dataclass, field


def frame(event: str, payload: dict) -> str:
    """One SSE message; JSON.stringify equivalent escapes newlines."""
    if "\n" in event or "\r" in event:
        raise ValueError("Invalid SSE event name")
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@dataclass
class SSEParser:
    """Feed decoded text in any chunk boundaries; CRLF normalized with carry."""
    buffer: str = ""
    events: list[tuple[str, dict]] = field(default_factory=list)

    def feed(self, chunk: str) -> list[tuple[str, dict]]:
        self.buffer += chunk
        parsed = []
        # Normalize only complete CRLF pairs, preserve incomplete '\r' for next chunk.
        while True:
            self.buffer = self.buffer.replace("\r\n", "\n")
            separator = self.buffer.find("\n\n")
            if separator < 0:
                break
            raw, self.buffer = self.buffer[:separator], self.buffer[separator + 2:]
            kind, pieces = "message", []
            for line in raw.split("\n"):
                if line.startswith("event:"):
                    kind = line[6:].strip()
                elif line.startswith("data:"):
                    pieces.append(line[5:].lstrip(" "))
            if pieces:
                parsed.append((kind, json.loads("\n".join(pieces))))
        self.events.extend(parsed)
        return parsed
