// Claude sửa theo yêu cầu, 2026-10-19 — khớp tay với backend/app/main.py (format_sse) + tools.py

// payload của từng event (key = tên event SSE)
export type ChatEventMap = {
  delta: {
    content: string;
  };
  tool_call: {
    call_id: string;
    name: string;
    // backend parse sẵn (parse_args), JSON hỏng → { _raw: "..." }
    arguments: Record<string, unknown>;
  };
  tool_result:
    | { call_id: string; name: string; ok: true; data: unknown }
    | { call_id: string; name: string; ok: false; error: string };
  done: {
    input_tokens: number;
    output_tokens: number;
    cost_usd: number;
    steps: number;
    incomplete: boolean;
  };
  error: {
    message: string;
  };
};

// discriminated union sinh từ map: { event: "delta"; data: {...} } | { event: "tool_call"; ... } | ...
export type ChatEvent = {
  [K in keyof ChatEventMap]: { event: K; data: ChatEventMap[K] };
}[keyof ChatEventMap];

export type Usage = ChatEventMap["done"];

export type TextPart = {
  type: "text";
  text: string;
};

export type ToolPart = {
  type: "tool";
  call_id: string;
  name: string;
  arguments: Record<string, unknown>;
  status: "running" | "ok" | "error";
  data?: unknown;
  error?: string;
};

export type AssistantMessage = {
  parts: (TextPart | ToolPart)[];
  usage?: Usage;
  error?: string;
};

export type UserMessage = {
  id: string;
  role: "user";
  text: string;
};

export type AssistantTurn = {
  id: string;
  role: "assistant";
  status: "streaming" | "done" | "stopped";
  message: AssistantMessage;
};

export type ChatMessage = UserMessage | AssistantTurn;
