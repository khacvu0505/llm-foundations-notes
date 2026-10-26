"use client";

// Claude viết theo yêu cầu, 2026-10-20 — Bài 5: chọn kịch bản → widget gọi /api/chat-mock?scenario=… (không tốn tiền OpenAI).
// Client page + useState thay vì đọc searchParams ở server: không phải bọc <Suspense> khi bật cacheComponents.

import { useState } from "react";
import { ChatWidget } from "@/components/ChatWidget";

const SCENARIOS = [
  {
    id: "ok",
    label: "Đường vui",
    expect:
      "“Đang trả lời…” → “Đang xem thời tiết…” → card → chữ chảy → usage 0 token",
  },
  {
    id: "tool-error",
    label: "Tool lỗi",
    expect: "cảnh báo nhỏ dưới tool, chữ vẫn chảy, kết thúc bằng usage",
  },
  {
    id: "mid-error",
    label: "Lỗi giữa stream",
    expect: "giữ chữ đã có + câu báo lỗi đỏ, không có usage",
  },
  {
    id: "unknown-tool",
    label: "Tool lạ",
    expect: "fallback JSON gọn, không crash",
  },
  {
    id: "rate-limit",
    label: "429",
    expect: "“Bạn hỏi nhanh quá, thử lại sau 42 giây”",
  },
];

export default function MockClient() {
  const [scenario, setScenario] = useState("ok");

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-4 p-6">
      <h1 className="text-xl font-semibold">
        Route giả — kiểm UI không tốn tiền
      </h1>
      <p className="text-sm text-zinc-500">
        Chọn kịch bản, mở bong bóng 💬, hỏi câu bất kỳ. Widget gọi{" "}
        <code>/api/chat-mock?scenario={scenario}</code>.
      </p>

      <fieldset className="flex flex-col gap-2 text-sm">
        <legend className="mb-2 font-medium">Kịch bản</legend>
        {SCENARIOS.map((s) => (
          <label key={s.id} className="flex cursor-pointer gap-2">
            <input
              type="radio"
              name="scenario"
              value={s.id}
              checked={scenario === s.id}
              onChange={() => setScenario(s.id)}
            />
            <span>
              <b>{s.label}</b>{" "}
              <span className="text-zinc-500">— {s.expect}</span>
            </span>
          </label>
        ))}
      </fieldset>

      <ChatWidget endpoint={`/api/chat-mock?scenario=${scenario}`} />
    </main>
  );
}
