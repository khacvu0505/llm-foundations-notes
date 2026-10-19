# Buổi 11 — Project #1 (p2): Smart Copilot Widget — Frontend

Code **không** nằm ở thư mục này: frontend ở `projects/p1-smart-copilot/web/`, cạnh `backend/` của Buổi 10. Thư mục
`weeks/week02/session11/` chỉ có đề bài (file này) + `notes.md`.

Luật chơi như cũ: tự viết code, tra docs chính thức khi cần. Next.js bản cài là **16.x**: đọc docs trong
`web/node_modules/next/dist/docs/` trước khi viết (xem `web/AGENTS.md`), không dựa vào trí nhớ về Next.js cũ.

## Sản phẩm

Widget chat nhúng được vào trang khác: bấm bong bóng góc phải → mở khung chat → hỏi → thấy trạng thái tool → thấy
**component** (bảng / chart / card) → chữ chảy ra. Backend giữ nguyên của Buổi 10.

Hợp đồng event từ backend (`backend/app/main.py`, Buổi 10 Bài 2):

| event         | data                                                                              |
| ------------- | --------------------------------------------------------------------------------- |
| `delta`       | `{"content": "<mảnh chữ>"}`                                                       |
| `tool_call`   | `{"call_id", "name", "arguments": {...}}`                                          |
| `tool_result` | `{"call_id", "name", "ok": true, "data": ...}` hoặc `{"ok": false, "error": "..."}` |
| `done`        | `{"input_tokens", "output_tokens", "cost_usd", "steps", "incomplete"}`            |
| `error`       | `{"message": "..."}`                                                              |

Hình dạng `data` của từng tool (`backend/app/tools.py`) → component:

| Tool            | `data`                                                                                    | Component    |
| --------------- | ----------------------------------------------------------------------------------------- | ------------ |
| `query_orders`  | `{orders: [{order_id, customer, product, quantity, unit_price, status, created_at, city}], order_count, total_amount_vnd}` | Bảng |
| `sales_summary` | **list** `[{label, revenue_vnd, order_count}]` (đã sắp xếp sẵn)                           | Chart        |
| `get_weather`   | `{city, temperature_c, condition, observed_at}`                                           | Card         |

Chép code từ: `session09/web/app/page.tsx` (đọc stream bằng `fetch` + `getReader()`, tách event theo `\n\n`, nút
Dừng). Mỗi buổi 1 code độc lập: **chép**, không import chéo.

## Bài 1 — Route Handler: key nằm ở server (~20ph)

Buổi 9 gọi thẳng FastAPI từ trình duyệt với `NEXT_PUBLIC_APP_API_KEY` → key lộ trong bundle JS (Buổi 9 Bài 5B).
Giờ làm đúng:

- `app/api/chat/route.ts` (`POST`): đọc body → `fetch` FastAPI `/chat/stream` kèm header `X-API-Key` lấy từ
  `process.env.APP_API_KEY` (**không** có `NEXT_PUBLIC_`) → trả stream về trình duyệt.
  Đường đi: `Trình duyệt → /api/chat (Next server) → FastAPI → OpenAI`.
- Lỗi trước stream (401 / 422 / 429) của FastAPI: chuyển tiếp **đúng status**, và với 429 giữ header `Retry-After`.
- Nút Dừng phải dừng được **tới tận FastAPI**: trình duyệt huỷ → Route Handler huỷ request tới FastAPI → backend ghi
  `status: cancelled` trong `logs/cost.jsonl`. Gợi ý: `request.signal`.
- Trình duyệt giờ gọi `/api/chat` **cùng origin** → frontend không cần CORS nữa.

Gợi ý:
- Docs: `01-app/01-getting-started/15-route-handlers.md`, `01-app/02-guides/streaming.md` mục "Streaming in Route
  Handlers" và "What can affect streaming" (compression, proxy buffer).
- Chuyển tiếp stream: `res.body` của `fetch` đã là `ReadableStream` → có cần tự đọc rồi ghi lại không?

Câu hỏi ghi notes: mở DevTools → Network + Sources, còn tìm thấy key không? Chữ có còn chảy từng mảnh hay bị dồn
cục (nếu dồn thì do lớp nào buffer)? Bấm Dừng thì backend có ghi `cancelled` không?

## Bài 2 — Đọc stream có type + state của 1 tin nhắn (~20ph)

- `lib/sse.ts`: hàm tách event SSE (chép từ Buổi 9, tách khỏi component) trả về object có type.
- Khai báo **discriminated union** cho 5 event (`type ChatEvent = { event: "delta"; data: {...} } | ...`). So với
  Python: giống `Literal` + `TypedDict` của backend — 2 bên phải khớp tay, sửa 1 bên thì phải sửa bên kia.
- Model 1 tin nhắn assistant gồm nhiều **part** theo thứ tự đến:
  `parts: (TextPart | ToolPart)[]`, `ToolPart = { call_id, name, arguments, status: "running" | "ok" | "error", data?, error? }`.
- Viết **hàm thuần** `applyEvent(message, event) → message mới` (không gọi `setState` bên trong): `delta` nối vào
  text part cuối, `tool_call` thêm ToolPart `running`, `tool_result` tìm theo **`call_id`** rồi đổi `ok` / `error`,
  `done` gắn usage. Component chỉ gọi `setMessage(m => applyEvent(m, ev))`.
- Lỗi trước stream: 401 / 429 / 5xx / mất mạng → câu báo gọn cho người dùng; 429 hiện "thử lại sau N giây" từ
  `Retry-After`.

Câu hỏi ghi notes: vì sao ghép `tool_result` theo `call_id` mà không theo thứ tự / theo `name` (nhớ lần model gọi 2
tool **cùng 1 bước** ở Buổi 10)? Vì sao tách `applyEvent` thành hàm thuần?

## Bài 3 — Generative UI (~35ph, cốt lõi)

- 3 component: `OrdersTable`, `SalesChart`, `WeatherCard`, nhận đúng `data` của tool (bảng trên).
- **Registry** `name → component` (giống `TOOLS_REGISTRY` ở backend). Tool lạ / chưa có component → fallback
  hiện JSON gọn, không crash.
- Mỗi ToolPart hiển thị theo `status`:
  - `running` → trạng thái theo tên tool ("Đang tra đơn hàng…", "Đang xem thời tiết Đà Nẵng…") — Buổi 10 đo TTFT có
    tool 3–7s nên phần này **bắt buộc**.
  - `ok` → component.
  - `error` → dòng cảnh báo nhỏ (`error` từ backend), chữ của model vẫn hiện bên dưới.
- Tiền định dạng VND (`Intl.NumberFormat("vi-VN", ...)`), ngày giờ đọc được.
- Chart: tự quyết **thư viện** (vd Recharts) hay **tự vẽ** bằng `div` + chiều rộng %. Ghi lý do.
- Thử: 3 câu mẫu Buổi 10 + câu cần 2 tool ("So sánh doanh thu theo ngày với thời tiết Hà Nội hôm nay").

Gợi ý:
- `data` đến từ mạng, TypeScript **không** kiểm lúc chạy. Type cast là đủ cho project này, hay cần validate (Zod)?
  Quyết định và ghi lại (so với Buổi 5: Pydantic validate ở backend).
- `sales_summary` trả **list**, 2 tool kia trả **object** → component nhận props thế nào cho gọn?

Câu hỏi ghi notes: Generative UI kiểu này (backend trả data, frontend chọn component) khác gì để LLM sinh
HTML/JSX? Ưu / nhược (an toàn, kiểm soát giao diện, token)?

## Bài 4 — Widget nhúng được + streaming UI mượt (~20ph)

- `components/ChatWidget.tsx`: bong bóng cố định góc phải dưới → bấm mở khung chat, đóng lại được. Danh sách tin
  nhắn (user + assistant), input + Gửi + Dừng.
- Mượt:
  - Trước `delta` đầu tiên: có chỉ báo "đang trả lời…" (không để khung trống).
  - Tự cuộn xuống khi chữ chảy, **nhưng** không kéo người dùng xuống nếu họ đang cuộn lên đọc.
  - Khoá Gửi lúc đang stream; bấm Dừng thì **giữ** phần chữ đã có + ghi "đã dừng".
  - Hiện usage / cost nhỏ dưới tin nhắn (đã có từ Buổi 9).
- "Nhúng được": trang `app/embed/page.tsx` chỉ có widget, nhúng bằng `<iframe>` từ **1 trang HTML ở origin khác**
  (vd file `embed-test.html` mở bằng `python3 -m http.server 5500`) → widget vẫn chạy.

Lưu ý: backend `ChatRequest` chỉ nhận **1** `message`, không có lịch sử → mỗi câu hỏi độc lập, model không nhớ câu
trước. Giao diện hiện nhiều tin nhắn nhưng **chưa** là hội thoại nhiều lượt. Giữ nguyên buổi này, ghi lại.

Câu hỏi ghi notes: iframe có bị chặn không (`X-Frame-Options` / CSP `frame-ancestors` mặc định của Next.js là gì)?
Nhúng bằng iframe vs nhúng bằng `<script>` tạo widget thẳng trong trang chủ: khác gì về CSS, cookie, bảo mật?

## Bài 5 — Kiểm tra (~15ph)

- **Route giả** `app/api/chat-mock/route.ts`: trả 1 kịch bản SSE viết tay (`tool_call → tool_result → delta… →
  done`, và 1 kịch bản `tool_result ok:false`) → kiểm UI **không tốn tiền OpenAI**, chủ động tạo được case lỗi (giống
  OpenAI giả ở test backend Buổi 10).
- Kiểm tay, ghi kết quả vào bảng trong `notes.md`: 4 câu thật, tool lỗi (route giả), lỗi giữa stream, Dừng giữa
  chừng, bắn 6 câu liên tiếp → câu thứ 6 hiện thông báo 429.
- `pnpm lint` và `pnpm exec tsc --noEmit` sạch.
- (Tuỳ chọn) Vitest cho `lib/sse.ts` và `applyEvent` (hàm thuần → test dễ).

## Buổi 12 (xem trước, chưa làm)

Polish Project #1: README (kiến trúc, GIF demo), deploy backend (Railway / Render) + frontend (Vercel), kiểm lại
rate limit sau proxy (IP thật). **Rebuild test**: repo trắng, dựng lại "hỏi → tool call → stream → render UI" trong 1
buổi, không nhìn code cũ.
