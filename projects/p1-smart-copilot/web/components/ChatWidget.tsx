"use client";

// Claude viết theo yêu cầu, 2026-10-20 — Bài 4 bước 2: khung widget (bong bóng + khung chat).
// Bước 3: danh sách tin nhắn + gửi /api/chat, mỗi event cập nhật đúng tin assistant theo id.
// Bước 4: nút Dừng (AbortController → huỷ tới tận FastAPI) + khoá Gửi lúc đang stream.
// Bước 5: dưới từng tin assistant — "Đang trả lời…", lỗi, usage.
// Bước 6: tự cuộn theo chữ, nhưng không kéo xuống nếu người dùng đang cuộn lên đọc.
// Bài 5: prop `endpoint` → trang /mock trỏ sang /api/chat-mock (route giả, không tốn tiền OpenAI).

import { useEffect, useRef, useState } from "react";
import { ToolView } from "@/components/ToolView";
import { applyEvent } from "@/lib/applyEvent";
import { errorFromException, errorFromResponse } from "@/lib/errors";
import { readEvents } from "@/lib/sse";
import type { AssistantTurn, ChatMessage } from "@/lib/types";

export function ChatWidget({ endpoint = "/api/chat" }: { endpoint?: string }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  // ref, không phải state: cuộn tới đâu set tới đó → state sẽ re-render liên tục
  const nearBottomRef = useRef(true);

  // chỉ đo lúc CUỘN (người dùng cuộn, hoặc chính effect dưới cuộn). Nội dung dài thêm không bắn scroll
  // → giá trị giữ từ lần cuộn trước: đang ở đáy thì vẫn true dù tool vừa chèn card cao 300px
  function handleScroll(e: React.UIEvent<HTMLDivElement>) {
    const el = e.currentTarget;
    nearBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 50;
  }

  // mỗi lần messages đổi (mỗi delta) hoặc vừa mở khung → đang ở đáy thì cuộn theo.
  // Gán scrollTop thẳng, không behavior "smooth": cuộn mượt chưa xong thì delta sau tới,
  // scroll event giữa chừng đo ra "không ở đáy" → tự ngừng theo.
  useEffect(() => {
    const el = listRef.current;
    if (el && nearBottomRef.current) el.scrollTop = el.scrollHeight;
  }, [messages, open]);

  // suy ra từ state, không giữ state riêng; cũng không dùng abortRef (đổi ref không render lại → nút không đổi)
  const streaming = messages.some((m) => m.role === "assistant" && m.status === "streaming");

  // sửa đúng 1 tin assistant theo id. Luôn qua updater: `messages` đọc trong vòng lặp là giá trị cũ (stale closure)
  function updateTurn(id: string, fn: (t: AssistantTurn) => AssistantTurn) {
    setMessages((ms) => ms.map((m) => (m.id === id && m.role === "assistant" ? fn(m) : m)));
  }

  async function handleSubmit(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = input.trim();
    // ẩn nút Gửi chưa đủ: form chỉ có 1 ô nhập → Enter vẫn submit
    if (!text || streaming) return;

    // tạo id NGOÀI updater: Strict Mode gọi updater 2 lần → tạo bên trong sẽ ra 2 id khác nhau
    const userId = crypto.randomUUID();
    const id = crypto.randomUUID();
    setMessages((ms) => [
      ...ms,
      { id: userId, role: "user", text },
      { id, role: "assistant", status: "streaming", message: { parts: [] } },
    ]);
    setInput("");
    // tự gửi câu mới = muốn xem câu trả lời → kéo xuống đáy dù trước đó đang cuộn lên
    nearBottomRef.current = true;

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      // cùng origin → không cần CORS, không có key ở trình duyệt (Bài 1)
      // signal: huỷ ở đây → Route Handler thấy request.signal bị huỷ → huỷ fetch tới FastAPI (Bài 1)
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) {
        const error = await errorFromResponse(res);
        updateTurn(id, (t) => ({ ...t, status: "done", message: { ...t.message, error } }));
        return;
      }
      for await (const ev of readEvents(res.body)) {
        updateTurn(id, (t) => ({ ...t, message: applyEvent(t.message, ev) }));
      }
      updateTurn(id, (t) => ({ ...t, status: "done" }));
    } catch (err) {
      // AbortError có thể ném ở fetch hoặc giữa lúc đọc stream; null = bấm Dừng → giữ parts đã có
      const error = errorFromException(err);
      updateTurn(id, (t) =>
        error === null ? { ...t, status: "stopped" } : { ...t, status: "done", message: { ...t.message, error } },
      );
    } finally {
      // chỉ dọn nếu ref vẫn là controller của lần này
      if (abortRef.current === controller) abortRef.current = null;
    }
  }

  function handleStop() {
    abortRef.current?.abort();
  }

  return (
    <>
      {/* w-96 × h-[32rem] cách đáy bottom-20 → vừa iframe 420×640 ở bước 8; đổi kích thước thì đổi cả iframe */}
      {open && (
        <section
          aria-label="Smart Copilot"
          className="fixed right-4 bottom-20 z-50 flex h-[32rem] w-96 max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-xl dark:border-zinc-700 dark:bg-zinc-900"
        >
          <header className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-700">
            <h2 className="text-sm font-semibold">Smart Copilot</h2>
          </header>

          <div
            ref={listRef}
            onScroll={handleScroll}
            className="flex flex-1 flex-col gap-3 overflow-y-auto p-4 text-sm"
          >
            {messages.length === 0 && <p className="text-zinc-500">Hỏi về đơn hàng, doanh thu hoặc thời tiết.</p>}
            {messages.map((m) =>
              m.role === "user" ? (
                <p
                  key={m.id}
                  className="max-w-[85%] self-end rounded-lg bg-zinc-900 px-3 py-2 whitespace-pre-wrap text-white dark:bg-white dark:text-zinc-900"
                >
                  {m.text}
                </p>
              ) : (
                <div key={m.id} className="flex flex-col gap-2">
                  {/* trước part đầu tiên (1.4–3.9s, notes Bài 2–3) → không để trống; có tool rồi thì ToolView tự hiện "Đang tra…" */}
                  {m.status === "streaming" && m.message.parts.length === 0 && (
                    <>
                      <p className="animate-pulse text-zinc-500">Đang trả lời…</p>
                      {/* Buổi 12 A3: Render free ngủ sau 15ph, dậy mất 50–75s. Bình thường event đầu tới ở 2–3.5s
                          → 5s chưa có gì thì báo. CSS delay (globals.css), không timer: có event là cả khối tự biến mất */}
                      <p className="animate-appear-late text-xs text-zinc-500">Máy chủ có thể đang khởi động (~1 phút)…</p>
                    </>
                  )}
                  {m.message.parts.map((p, i) =>
                    p.type === "text" ? (
                      // text part không có id; parts chỉ thêm vào cuối, không chèn giữa → index làm key được
                      <p key={`text-${i}`} className="whitespace-pre-wrap">
                        {p.text}
                      </p>
                    ) : (
                      <ToolView key={p.call_id} part={p} />
                    ),
                  )}
                  {/* lỗi trước stream (429 / 401 / mất mạng) hoặc event error giữa chừng → chữ đã có vẫn giữ ở trên */}
                  {m.message.error && <p className="text-red-600 dark:text-red-400">{m.message.error}</p>}
                  {m.status === "stopped" && <p className="text-xs text-zinc-500">Đã dừng</p>}
                  {m.message.usage && (
                    <p className="text-xs text-zinc-500">
                      {m.message.usage.input_tokens} in · {m.message.usage.output_tokens} out · $
                      {m.message.usage.cost_usd.toFixed(5)}
                      {m.message.usage.incomplete && " · bị cắt (incomplete)"}
                    </p>
                  )}
                </div>
              ),
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2 border-t border-zinc-200 p-3 dark:border-zinc-700">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Hỏi gì đó, vd: Đơn nào của An đang giao?"
              maxLength={500}
              className="flex-1 rounded border px-3 py-2 text-sm"
            />
            {/* ô nhập để mở: gõ trước câu sau được, chỉ chưa gửi được.
                key khác nhau → React tạo nút MỚI thay vì đổi type="button" → "submit" trên cùng 1 nút:
                không có key, bấm Dừng xong nút thành submit ngay trong lúc click → form gửi luôn câu đang gõ (đã tái hiện) */}
            {streaming ? (
              // type="button": trong form, button mặc định là submit
              <button key="stop" type="button" onClick={handleStop} className="rounded border px-3 py-2 text-sm">
                Dừng
              </button>
            ) : (
              <button
                key="send"
                type="submit"
                disabled={!input.trim()}
                className="rounded border px-3 py-2 text-sm disabled:opacity-50"
              >
                Gửi
              </button>
            )}
          </form>
        </section>
      )}

      {/* 1 nút vừa mở vừa đóng: mở rồi thì đổi thành ✕ */}
      <button
        type="button"
        onClick={() => {
          // khung đóng = list bị bỏ khỏi DOM, mở lại thì scrollTop về 0 → mở ra thì về đáy (tin mới nhất)
          if (!open) nearBottomRef.current = true;
          setOpen(!open);
        }}
        aria-label={open ? "Đóng khung chat" : "Mở khung chat"}
        aria-expanded={open}
        className="fixed right-4 bottom-4 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-zinc-900 text-xl text-white shadow-lg hover:bg-zinc-700 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
      >
        {open ? "✕" : "💬"}
      </button>
    </>
  );
}
