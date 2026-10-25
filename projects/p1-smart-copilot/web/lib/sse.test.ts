// Claude viết theo yêu cầu, 2026-10-20 — Bài 5 (tuỳ chọn): Vitest cho lib/sse.ts.
// Chuyển các case của script test tạm Bài 2 (scratchpad, không commit) vào repo → `pnpm test` chạy lại được.

import { afterEach, describe, expect, it, vi } from "vitest";
import { parseEvent, readEvents } from "./sse";
import type { ChatEvent } from "./types";

const encoder = new TextEncoder();

// đúng dạng backend/app/sse.py
const sse = (event: string, data: unknown) => `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;

// stream giả: mỗi phần tử = 1 chunk mạng
function streamOf(chunks: (string | Uint8Array)[]): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      for (const c of chunks) controller.enqueue(typeof c === "string" ? encoder.encode(c) : c);
      controller.close();
    },
  });
}

async function collect(body: ReadableStream<Uint8Array>): Promise<ChatEvent[]> {
  const out: ChatEvent[] = [];
  for await (const ev of readEvents(body)) out.push(ev);
  return out;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("parseEvent", () => {
  it("đọc event đúng thành { event, data }", () => {
    expect(parseEvent('event: delta\ndata: {"content":"Xin"}')).toEqual({ event: "delta", data: { content: "Xin" } });
  });

  it("tool_result ok:false giữ nguyên error", () => {
    const raw = sse("tool_result", { call_id: "a", name: "query_orders", ok: false, error: "Tool lỗi" }).trim();
    expect(parseEvent(raw)).toEqual({
      event: "tool_result",
      data: { call_id: "a", name: "query_orders", ok: false, error: "Tool lỗi" },
    });
  });

  it("trả null khi JSON hỏng / tên event lạ / thiếu data", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(parseEvent("event: delta\ndata: {hỏng")).toBeNull();
    expect(warn).toHaveBeenCalledOnce(); // JSON hỏng thì có log để debug
    expect(parseEvent("event: ping\ndata: {}")).toBeNull();
    expect(parseEvent("event: delta")).toBeNull();
  });
});

describe("readEvents", () => {
  it("2 event trong 1 chunk → ra đủ 2", async () => {
    const body = streamOf([sse("delta", { content: "a" }) + sse("delta", { content: "b" })]);
    expect(await collect(body)).toEqual([
      { event: "delta", data: { content: "a" } },
      { event: "delta", data: { content: "b" } },
    ]);
  });

  it("1 event bị cắt làm 2 chunk → vẫn ra 1 event nguyên", async () => {
    const raw = sse("delta", { content: "Xin chào" });
    const body = streamOf([raw.slice(0, 10), raw.slice(10)]);
    expect(await collect(body)).toEqual([{ event: "delta", data: { content: "Xin chào" } }]);
  });

  it("chữ nhiều byte bị cắt đôi giữa 2 chunk vẫn nguyên vẹn", async () => {
    const bytes = encoder.encode(sse("delta", { content: "ạ" }));
    // "ạ" = E1 BA A1 trong UTF-8 → cắt ngay sau byte đầu
    const cut = bytes.indexOf(0xe1) + 1;
    const body = streamOf([bytes.slice(0, cut), bytes.slice(cut)]);
    expect(await collect(body)).toEqual([{ event: "delta", data: { content: "ạ" } }]);
  });

  it("event cuối không có \\n\\n vẫn ra (flush sau vòng lặp)", async () => {
    const body = streamOf([sse("delta", { content: "a" }) + 'event: done\ndata: {"steps":1}']);
    const events = await collect(body);
    expect(events.at(-1)).toEqual({ event: "done", data: { steps: 1 } });
  });

  it("dừng sớm (như break) → nhả lock", async () => {
    const body = streamOf([sse("delta", { content: "a" }), sse("delta", { content: "b" })]);
    const gen = readEvents(body);
    await gen.next();
    await gen.return(undefined); // for await + break gọi return() → chạy finally
    expect(body.locked).toBe(false);
  });

  it("stream lỗi giữa chừng → lỗi lên tới caller, không lặp vô hạn, nhả lock", async () => {
    let pulls = 0;
    const body = new ReadableStream<Uint8Array>({
      pull(controller) {
        if (pulls++ === 0) controller.enqueue(encoder.encode(sse("delta", { content: "a" })));
        else controller.error(new DOMException("Aborted", "AbortError"));
      },
    });
    const got: ChatEvent[] = [];
    await expect(
      (async () => {
        for await (const ev of readEvents(body)) got.push(ev);
      })(),
    ).rejects.toThrow("Aborted");
    expect(got).toEqual([{ event: "delta", data: { content: "a" } }]);
    expect(body.locked).toBe(false);
  });
});
