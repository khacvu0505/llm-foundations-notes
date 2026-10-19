import type { AssistantMessage, ChatEvent } from "./types";

export function applyEvent(
  msg: AssistantMessage,
  ev: ChatEvent,
): AssistantMessage {
  switch (ev.event) {
    // { } quanh case có const → const không lọt sang case khác (ESLint no-case-declarations)
    case "delta": {
      const last = msg.parts.at(-1);
      if (last && last.type === "text") {
        return {
          ...msg,
          parts: [
            ...msg.parts.slice(0, -1),
            { ...last, text: last.text + ev.data.content },
          ],
        };
      } else {
        return {
          ...msg,
          parts: [...msg.parts, { type: "text", text: ev.data.content }],
        };
      }
    }

    case "tool_call":
      return {
        ...msg,
        parts: [
          ...msg.parts,
          {
            type: "tool",
            status: "running",
            call_id: ev.data.call_id,
            name: ev.data.name,
            arguments: ev.data.arguments,
          },
        ],
      };

    case "tool_result": {
      const result = ev.data; // { call_id, name, ok: true, data } | { call_id, name, ok: false, error }
      return {
        ...msg,
        parts: msg.parts.map((p) => {
          // 1. not the part we're looking for → return it unchanged
          if (p.type !== "tool" || p.call_id !== result.call_id) return p;

          // 2. it's our tool part → return an updated copy
          if (result.ok) {
            return { ...p, status: "ok", data: result.data };
          }
          return { ...p, status: "error", error: result.error };
        }),
      };
    }

    case "done":
      return { ...msg, usage: ev.data };

    // Claude sửa theo yêu cầu, 2026-10-19: error giữ parts (chữ đã hiện), thêm câu báo lỗi
    case "error":
      return { ...msg, error: ev.data.message };

    default: {
      const _exhaustive: never = ev;
      return _exhaustive;
    }
  }
}
