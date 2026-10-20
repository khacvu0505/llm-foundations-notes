// Claude viết theo yêu cầu, 2026-10-20 — Bài 5 (tuỳ chọn): Vitest cho lib/applyEvent.ts (hàm thuần → test không cần React).

import { describe, expect, it } from "vitest";
import { applyEvent } from "./applyEvent";
import type { AssistantMessage, ChatEvent } from "./types";

// áp lần lượt nhiều event, như vòng for await trong ChatWidget
const applyAll = (events: ChatEvent[], start: AssistantMessage = { parts: [] }) => events.reduce(applyEvent, start);

// đóng băng sâu: module ESM chạy strict mode → hàm nào lỡ sửa message cũ (push, gán parts[i]) là ném lỗi ngay
function deepFreeze<T>(value: T): T {
  if (value && typeof value === "object") {
    Object.values(value).forEach(deepFreeze);
    Object.freeze(value);
  }
  return value;
}

const weather = (call_id: string, city: string): ChatEvent => ({
  event: "tool_call",
  data: { call_id, name: "get_weather", arguments: { city } },
});

describe("applyEvent", () => {
  it("delta nối vào text part cuối; sau tool thì mở text part mới", () => {
    const m = applyAll([
      { event: "delta", data: { content: "Xin " } },
      { event: "delta", data: { content: "chào" } },
      weather("a", "Hà Nội"),
      { event: "delta", data: { content: "Trời đẹp" } },
    ]);
    expect(m.parts).toMatchObject([
      { type: "text", text: "Xin chào" },
      { type: "tool", call_id: "a", status: "running" },
      { type: "text", text: "Trời đẹp" },
    ]);
  });

  it("tool_result ghép theo call_id: 2 tool cùng tên, kết quả về ngược thứ tự", () => {
    const m = applyAll([
      weather("a", "Hà Nội"),
      weather("b", "Đà Nẵng"),
      { event: "tool_result", data: { call_id: "b", name: "get_weather", ok: true, data: { city: "Đà Nẵng" } } },
      { event: "tool_result", data: { call_id: "a", name: "get_weather", ok: true, data: { city: "Hà Nội" } } },
    ]);
    expect(m.parts).toMatchObject([
      { call_id: "a", status: "ok", data: { city: "Hà Nội" } },
      { call_id: "b", status: "ok", data: { city: "Đà Nẵng" } },
    ]);
  });

  it("tool_result ok:false → status error + câu lỗi", () => {
    const m = applyAll([
      weather("a", "Hà Nội"),
      { event: "tool_result", data: { call_id: "a", name: "get_weather", ok: false, error: "Tool lỗi" } },
    ]);
    expect(m.parts[0]).toMatchObject({ status: "error", error: "Tool lỗi" });
  });

  it("done gắn usage", () => {
    const usage = { input_tokens: 10, output_tokens: 5, cost_usd: 0.0001, steps: 1, incomplete: false };
    expect(applyAll([{ event: "done", data: usage }]).usage).toEqual(usage);
  });

  it("error giữa chừng giữ chữ đã có + thêm error", () => {
    const m = applyAll([
      { event: "delta", data: { content: "Doanh thu là" } },
      { event: "error", data: { message: "Có lỗi" } },
    ]);
    expect(m).toMatchObject({ parts: [{ type: "text", text: "Doanh thu là" }], error: "Có lỗi" });
  });

  it("không sửa message cũ, gọi 2 lần ra cùng kết quả (Strict Mode gọi updater 2 lần)", () => {
    // part cuối là TEXT → delta đi vào nhánh "nối vào text part cuối" (nhánh dễ lỡ sửa part cũ nhất)
    const old = deepFreeze(applyAll([weather("a", "Hà Nội"), { event: "delta", data: { content: "Xin " } }]));
    const events: ChatEvent[] = [
      { event: "delta", data: { content: "chào" } },
      { event: "tool_result", data: { call_id: "a", name: "get_weather", ok: true, data: {} } },
    ];
    for (const ev of events) {
      expect(applyEvent(old, ev)).toEqual(applyEvent(old, ev));
    }
  });
});
