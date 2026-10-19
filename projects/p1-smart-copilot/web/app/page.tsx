"use client";

// Claude viết theo yêu cầu, 2026-10-19 — trang thử Bài 2: readEvents + applyEvent + errors.
// Render tạm bằng <pre>, Bài 3 thay bằng component (bảng / chart / card).

import { useRef, useState } from "react";
import { applyEvent } from "@/lib/applyEvent";
import { errorFromException, errorFromResponse } from "@/lib/errors";
import { readEvents } from "@/lib/sse";
import type { AssistantMessage } from "@/lib/types";

type Status = "idle" | "streaming" | "stopped";

export default function Home() {
  const [input, setInput] = useState("");
  const [message, setMessage] = useState<AssistantMessage>({ parts: [] });
  const [status, setStatus] = useState<Status>("idle");
  const abortRef = useRef<AbortController | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = input.trim();
    if (!text || status === "streaming") return;

    setMessage({ parts: [] });
    setStatus("streaming");
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      // cùng origin → không cần CORS, không có key ở trình duyệt (Bài 1)
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) {
        const error = await errorFromResponse(res);
        setMessage((m) => ({ ...m, error }));
        setStatus("idle");
        return;
      }
      for await (const ev of readEvents(res.body)) {
        setMessage((m) => applyEvent(m, ev));
      }
      setStatus("idle");
    } catch (err) {
      // AbortError có thể ném ở fetch hoặc giữa lúc đọc stream → cùng 1 chỗ xử lý
      const error = errorFromException(err);
      if (error === null) {
        setStatus("stopped"); // bấm Dừng: giữ chữ đã có
      } else {
        setMessage((m) => ({ ...m, error }));
        setStatus("idle");
      }
    } finally {
      abortRef.current = null;
    }
  }

  function handleStop() {
    abortRef.current?.abort();
  }

  const streaming = status === "streaming";

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-4 p-6">
      <h1 className="text-xl font-semibold">
        Smart Copilot (Bài 2 — trang thử)
      </h1>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Hỏi gì đó, vd: Đơn nào của An đang giao?"
          maxLength={500}
          className="flex-1 rounded border px-3 py-2"
        />
        {streaming ? (
          <button
            type="button"
            onClick={handleStop}
            className="rounded border px-4 py-2"
          >
            Dừng
          </button>
        ) : (
          <button
            type="submit"
            disabled={!input.trim()}
            className="rounded border px-4 py-2 disabled:opacity-50"
          >
            Gửi
          </button>
        )}
      </form>

      {streaming && <p className="text-sm text-zinc-500">Đang trả lời…</p>}
      {status === "stopped" && <p className="text-sm text-zinc-500">Đã dừng</p>}
      {message.error && <p className="text-sm text-red-600">{message.error}</p>}

      <pre className="overflow-x-auto rounded bg-zinc-100 p-3 text-xs dark:bg-zinc-900">
        {JSON.stringify(message, null, 2)}
      </pre>
    </main>
  );
}
