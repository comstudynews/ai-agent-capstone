/** A streaming SSE parser that tolerates CRLF split between arbitrary network chunks. */
export type EventData = { event: string; payload: Record<string, unknown> };
export class SSEParser {
  private buffer = "";
  feed(chunk: string): EventData[] {
    this.buffer += chunk;
    const result: EventData[] = [];
    while (true) {
      // Do not normalize CRLF before a complete separator is present.
      const matched = /\r\n\r\n|\n\n|\r\r/.exec(this.buffer);
      if (!matched) break;
      const current = this.buffer.slice(0, matched.index);
      this.buffer = this.buffer.slice(matched.index + matched[0].length);
      let event = "message";
      const data: string[] = [];
      for (const line of current.replace(/\r\n|\r/g, "\n").split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
      }
      if (data.length) {
        const value: unknown = JSON.parse(data.join("\n"));
        if (value && typeof value === "object" && !Array.isArray(value)) {
          result.push({ event, payload: value as Record<string, unknown> });
        }
      }
    }
    return result;
  }
}
