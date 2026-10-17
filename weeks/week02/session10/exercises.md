# Buổi 10 — Project #1 (p1): Smart Copilot Widget — Backend

Code **không** nằm ở thư mục này: Project #1 sống ở `projects/p1-smart-copilot/` (Buổi 10, 11, 12 cùng làm
trên 1 code, Buổi 12 deploy). Thư mục `weeks/week02/session10/` chỉ có đề bài (file này) + `notes.md`.

Luật chơi như cũ: tự viết code, tra docs chính thức khi cần. Setup làm theo mục "Setup (tự làm)" trong `notes.md`.

## Sản phẩm

**Copilot cho chủ quán cà phê**: chủ quán hỏi bằng tiếng Việt, bot gọi tool lấy số liệu thật rồi trả lời,
chữ chảy ra theo SSE. Mỗi tool trả data có cấu trúc để Buổi 11 vẽ thành UI (Generative UI):

| Tool             | Có sẵn?             | Câu hỏi mẫu                                    | Buổi 11 render |
| ---------------- | ------------------- | ---------------------------------------------- | -------------- |
| `query_orders`   | Buổi 7              | "Đơn nào của An đang giao?"                    | Bảng           |
| `sales_summary`  | **Mới**             | "Tuần này món nào bán chạy nhất?"              | Chart          |
| `get_weather`    | Buổi 7              | "Mai Đà Nẵng mưa không, có nên giao đơn không?" | Card           |

Chép code từ: `session09/exercises.py` (chat stream, SSE, auth, test client giả),
`session07/exercises.py` (tools, `execute_call`, `MAX_STEPS`). Mỗi buổi 1 code độc lập: **chép**, không import chéo.

## Bài 1 — Dựng backend, chạy lại được những gì đã có (~20ph)

- Tách file thay vì 1 `exercises.py` (gợi ý, tự quyết):
  `app/main.py` (FastAPI app, routes), `app/sse.py` (`format_sse`), `app/tools.py` (tools + schema + registry),
  `app/auth.py` (`verify_api_key`), `app/llm.py` (client, `MODEL`, `PRICES`, `cost_usd`).
  So với TS: giống tách module trong `src/`, import bằng `from app.sse import format_sse`.
- Chạy được: `/health`, `/chat/stream` như cuối Buổi 9 (chưa có tool).
- Chép 4 test của Buổi 9 sang `tests/`, sửa import cho đúng cấu trúc mới → pass.

Câu hỏi ghi notes: tách file xong, import kiểu gì để `uv run fastapi dev`, `pytest`, `pyright` cùng chạy được?
Có cần `__init__.py` không?

## Bài 2 — Tool loop **bên trong** stream (~40ph, cốt lõi)

Buổi 7 = vòng lặp tool (không stream). Buổi 9 = stream (không tool). Bài này ghép 2 cái:

- `/chat/stream` gửi `tools=TOOLS` cho model. Lặp tối đa `MAX_STEPS` bước, mỗi bước 1 lời gọi `stream=True`:
  - Có delta chữ → gửi `event: delta` như cũ.
  - Model yêu cầu tool → gửi `event: tool_call`, chạy tool, gửi `event: tool_result`, đưa kết quả vào input,
    gọi bước tiếp.
  - Bước nào không có tool call → xong → `event: done`.
- Định dạng event (data là JSON):

  | event         | data                                                                  |
  | ------------- | --------------------------------------------------------------------- |
  | `delta`       | `{"content": "<mảnh chữ>"}`                                           |
  | `tool_call`   | `{"call_id": ..., "name": ..., "arguments": {...}}`                   |
  | `tool_result` | `{"call_id": ..., "name": ..., "ok": true, "data": {...}}` hoặc `ok: false` + `error` |
  | `done`        | `{"input_tokens", "output_tokens", "cost_usd", "steps", "incomplete"}` |
  | `error`       | `{"message": "<câu gọn>"}`                                            |

- Viết tool mới `sales_summary(group_by: "day" | "product", status: ... | None)`: trả danh sách
  `{label, revenue_vnd, order_count}` sắp xếp sẵn → đủ để vẽ chart, LLM không phải tự cộng (Buổi 7: để tool tính).
- Thử 3 câu hỏi mẫu ở bảng trên + 1 câu cần **2 tool** (vd "So sánh doanh thu với thời tiết Hà Nội hôm nay").

Gợi ý:
- Lấy function call từ stream: event `response.output_item.done` (item `type == "function_call"`), hoặc
  đọc `event.response.output` ở `response.completed`. Thử cả 2, chọn 1, ghi lý do.
- Tool trong `async` generator: `get_weather` Buổi 7 dùng `httpx2.get` **sync** → chặn event loop (Buổi 8).
  Đổi sang client async (Buổi 7 Bài 3 có `get_weather_parallel`). `query_orders` đọc CSV bằng pandas (sync, file
  nhỏ): chấp nhận được không? Ghi lại quyết định.
- Lỗi tool: `execute_call` Buổi 7 đã có 3 lớp (tool lạ / JSON hỏng / tool lỗi) → ở đây thành `tool_result` với
  `ok: false`, **không** `event: error` (stream vẫn tiếp, model tự xử lý).

Câu hỏi ghi notes: tool lỗi vs OpenAI lỗi giữa stream khác nhau thế nào (cái nào gửi `tool_result ok:false`, cái
nào gửi `event: error`)? TTFT khi có tool call dài ra bao nhiêu, vì sao? UI nên hiện gì trong lúc chờ tool?

## Bài 3 — Cost log (~20ph)

- 1 câu hỏi = nhiều lời gọi OpenAI (mỗi bước tool loop 1 lần) → cộng `usage` qua mọi bước.
- Mỗi request ghi **1 dòng** ra terminal **và** 1 dòng JSON vào `logs/cost.jsonl` (thêm `logs/` vào `.gitignore`):
  `ts`, `model`, `steps`, `tools` (tên các tool đã gọi), `input_tokens`, `output_tokens`, `cost_usd`,
  `ttft_ms`, `latency_ms`, `status` (`ok` / `error` / `cancelled` / `incomplete`).
- Ghi trong `finally` → request bị Dừng giữa chừng (Buổi 9) **cũng** có dòng log.
- Hỏi 5 câu khác nhau, đọc lại `cost.jsonl`: câu nào đắt nhất, vì sao? Token của tool schema chiếm bao nhiêu
  (Buổi 7 đo được ~167 token / lời gọi)?

Câu hỏi ghi notes: bị cancel giữa stream thì usage lấy ở đâu (có `response.completed` không)? Log thế nào cho
đúng thay vì ghi 0?

## Bài 4 — Chống spam tối thiểu (~20ph)

- **Rate limit theo IP** (in-memory, vd 5 request / 60s): `Depends(rate_limit)` chạy **trước** stream → vượt thì
  `HTTPException(429)` kèm header `Retry-After`. IP lấy từ `request.client.host`.
- **Luôn đặt** `max_output_tokens` (đã có) + giới hạn độ dài input (`max_length` ở `ChatRequest`, đã có).
- **429 từ OpenAI**: SDK tự retry (`max_retries`, mặc định 2 — `openai/_constants.py`). Đặt rõ trong code, ghi
  lại SDK retry những lỗi nào (tra docs SDK mục "Retries").
- Thử: bắn 7 request liên tiếp bằng curl → 5 cái 200, 2 cái 429.

Câu hỏi ghi notes: rate limit in-memory hỏng khi nào (nhiều worker / nhiều server / restart)? Sau proxy (Railway,
Vercel) thì `request.client.host` còn là IP thật của user không?

## Bài 5 — Test (~20ph)

- Client OpenAI giả (mở rộng từ Buổi 9) trả **kịch bản nhiều bước**: lần gọi 1 → 1 function call `query_orders`,
  lần gọi 2 → vài delta + completed. Kiểm thứ tự event: `tool_call → tool_result → delta... → done`,
  `done.steps == 2`, usage cộng đủ 2 bước.
- Test tool lỗi → `tool_result` có `ok: false`, stream vẫn kết thúc bằng `done`.
- Test lỗi OpenAI giữa stream (nợ Buổi 9) → có `event: error`.
- Test rate limit: request thứ 6 trong 60s → 429. Nhớ reset bộ đếm giữa các test.
- Test `sales_summary` thuần (không qua API): input CSV nhỏ → output đúng.

## Buổi 11 (xem trước, chưa làm)

Frontend `projects/p1-smart-copilot/web/`: widget chat nhúng được, đi qua **Route Handler** của Next.js (key
nằm ở server, Buổi 9 Bài 5B), Generative UI: `tool_result` → component (bảng / chart / card), streaming UI mượt,
nút Dừng.
