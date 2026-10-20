// Claude viết theo yêu cầu, 2026-10-20 — Bài 5: route giả trả kịch bản SSE viết tay → kiểm UI không tốn tiền OpenAI,
// chủ động tạo được case lỗi (giống OpenAI giả ở test backend Buổi 10).
// POST /api/chat-mock?scenario=ok | tool-error | mid-error | unknown-tool | rate-limit

import type { ChatEvent } from "@/lib/types"

// wait = chờ bao lâu TRƯỚC khi gửi event (giả lúc model nghĩ / tool chạy) → thấy được "Đang trả lời…", "Đang tra…", Dừng kịp
type Step = ChatEvent & { wait: number }

// chia câu thành từng từ (giữ dấu cách) → chữ chảy ra như delta thật
function words(text: string, wait = 60): Step[] {
  return (text.match(/\S+\s*/g) ?? []).map((content) => ({ event: "delta", data: { content }, wait }))
}

// 0 token, $0 → nhìn usage là biết đang dùng route giả
const DONE: Step = {
  event: "done",
  data: { input_tokens: 0, output_tokens: 0, cost_usd: 0, steps: 2, incomplete: false },
  wait: 100,
}

// data khớp tay với backend/app/tools.py (giống component nhận ở Bài 3)
const SCENARIOS: Record<string, Step[]> = {
  // đường vui: trạng thái tool → card → chữ chảy → usage
  ok: [
    { event: "tool_call", data: { call_id: "mock_1", name: "get_weather", arguments: { city: "Đà Nẵng" } }, wait: 800 },
    {
      event: "tool_result",
      data: {
        call_id: "mock_1",
        name: "get_weather",
        ok: true,
        data: { city: "Đà Nẵng", temperature_c: 29.5, condition: "Ít mây", observed_at: "2026-10-20 12:00" },
      },
      wait: 1500,
    },
    ...words(
      "Đà Nẵng hiện ít mây, khoảng 29,5°C, chưa thấy dấu hiệu mưa nên vẫn giao đơn bình thường được. " +
        "Đây là câu trả lời giả từ route chat-mock: không gọi FastAPI, không gọi OpenAI, không tốn tiền. " +
        "Câu đủ dài để kịp bấm Dừng giữa chừng và xem chữ đã có còn giữ lại không.",
    ),
    DONE,
  ],
  // tool lỗi (giống execute_call trả ok:false) → cảnh báo nhỏ, chữ vẫn chảy, vẫn kết thúc bằng done
  "tool-error": [
    { event: "tool_call", data: { call_id: "mock_1", name: "query_orders", arguments: { customer: "An" } }, wait: 800 },
    {
      event: "tool_result",
      data: { call_id: "mock_1", name: "query_orders", ok: false, error: "Tool query_orders lỗi, thử lại sau" },
      wait: 1000,
    },
    ...words("Mình chưa tra được đơn hàng của An lúc này do hệ thống đơn hàng đang lỗi. Bạn thử lại sau ít phút nhé."),
    DONE,
  ],
  // lỗi giữa stream (giống main.py gửi event error khi OpenAI lỗi) → giữ chữ đã có + câu báo lỗi, không có done
  "mid-error": [
    ...words("Doanh thu tuần này đang dẫn đầu là trà đào cam sả, tiếp theo là", 80),
    { event: "error", data: { message: "Có lỗi khi tạo câu trả lời, thử lại sau" }, wait: 400 },
  ],
  // tool frontend chưa có component → ToolView fallback hiện JSON gọn, không crash
  "unknown-tool": [
    { event: "tool_call", data: { call_id: "mock_1", name: "get_stock", arguments: { product: "Trà đào" } }, wait: 800 },
    {
      event: "tool_result",
      data: { call_id: "mock_1", name: "get_stock", ok: true, data: { product: "Trà đào", in_stock: 42 } },
      wait: 800,
    },
    ...words("Kho còn 42 ly trà đào."),
    DONE,
  ],
}

function sleep(ms: number, signal: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    if (signal.aborted) return reject(signal.reason)
    const timer = setTimeout(resolve, ms)
    signal.addEventListener(
      "abort",
      () => {
        clearTimeout(timer)
        reject(signal.reason)
      },
      { once: true },
    )
  })
}

export async function POST(request: Request) {
  // trang giả không ra prod
  if (process.env.NODE_ENV === "production") {
    return new Response(null, { status: 404 })
  }

  const scenario = new URL(request.url).searchParams.get("scenario") ?? "ok"

  // lỗi trước stream: cùng dạng route thật ({ error } + Retry-After) → errorFromResponse xử lý như 429 thật
  if (scenario === "rate-limit") {
    return Response.json({ error: "Rate limit exceeded" }, { status: 429, headers: { "Retry-After": "42" } })
  }

  const steps = SCENARIOS[scenario]
  if (!steps) {
    return Response.json({ error: `Không có kịch bản "${scenario}"` }, { status: 400 })
  }

  const encoder = new TextEncoder()
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        for (const step of steps) {
          await sleep(step.wait, request.signal)
          // đúng dạng backend/app/sse.py: "event: X\ndata: {json}\n\n"
          controller.enqueue(encoder.encode(`event: ${step.event}\ndata: ${JSON.stringify(step.data)}\n\n`))
        }
        controller.close()
      } catch {
        // trình duyệt bấm Dừng → request.signal abort → ngừng gửi (route thật thì backend ghi "cancelled")
        console.log(`[api/chat-mock] ${scenario}: cancelled`)
      }
    },
  })

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  })
}
