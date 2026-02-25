import type { SSEEvent } from "./types";

/**
 * Async generator that streams SSE events from the backend.
 * Uses fetch() + ReadableStream to support POST-style long messages
 * (avoids EventSource's GET-only limitation).
 */
export async function* streamChat(
  sessionId: string,
  message: string,
  signal: AbortSignal
): AsyncGenerator<SSEEvent> {
  const url = `/api/sessions/${sessionId}/stream?message=${encodeURIComponent(message)}`;
  const response = await fetch(url, {
    signal,
    headers: { Accept: "text/event-stream" },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += value;

      // SSE chunks are separated by double newlines
      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";

      for (const part of parts) {
        const dataLine = part.split("\n").find((l) => l.startsWith("data: "));
        if (dataLine) {
          try {
            yield JSON.parse(dataLine.slice(6)) as SSEEvent;
          } catch {
            // malformed chunk — skip
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
