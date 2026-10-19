import type { ChatEvent } from "./types";

const EVENT_NAMES = [
  "delta",
  "tool_call",
  "error",
  "done",
  "tool_result",
] as const;
type EventName = (typeof EVENT_NAMES)[number];
function isEventName(x: string): x is EventName {
  return (EVENT_NAMES as readonly string[]).includes(x);
}

export function parseEvent(raw: string): ChatEvent | null {
  const lines = raw.split("\n");
  let eventName = "";
  let data = "";
  for (const line of lines) {
    if (line.startsWith("event:")) {
      eventName = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      data = line.slice(5).trim();
    }
  }
  try {
    if (!data || !isEventName(eventName)) return null;

    return {
      event: eventName,
      data: JSON.parse(data),
    };
  } catch (error) {
    console.warn("[sse] bad event:", raw, error);
    return null;
  }
}

export async function* readEvents(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<ChatEvent> {
  let buffer = "";
  const reader = body.getReader();
  const decoder = new TextDecoder();
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";
      for (const part of parts) {
        const event = parseEvent(part);
        if (event) yield event;
      }
    }
    buffer += decoder.decode();
    if (buffer.trim().length > 0) {
      const event = parseEvent(buffer);
      if (event) yield event;
    }
  } finally {
    reader.releaseLock();
  }
}
