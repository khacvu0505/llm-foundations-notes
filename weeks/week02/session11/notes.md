# Buổi 11 — Project #1 (p2): Smart Copilot Widget — Frontend (2h)

| Phần                                          | Thời lượng | Làm ở đâu                                    |
| --------------------------------------------- | ---------- | -------------------------------------------- |
| Setup: tạo app Next.js, `.env.local`          | ~10ph      | mục Setup                                    |
| Bài 1: Route Handler, key ở server            | ~20ph      | `web/app/api/chat/route.ts`                  |
| Bài 2: đọc stream có type + `applyEvent`      | ~20ph      | `web/lib/`                                   |
| Bài 3: Generative UI (bảng / chart / card)    | ~35ph      | `web/components/`                            |
| Bài 4: widget nhúng được + streaming UI mượt  | ~20ph      | `web/components/ChatWidget.tsx`, `app/embed` |
| Bài 5: route giả + kiểm tay                   | ~15ph      | `web/app/api/chat-mock/`, notes              |

Đề bài chi tiết: `exercises.md` cùng thư mục. Bài 3 là cốt lõi; không kịp thì phần iframe (Bài 4) và route giả
(Bài 5) để sang đầu Buổi 12.

Checklist Notion Buổi 10–11 (Buổi 11 làm phần frontend):

- Frontend Next.js: chat widget nhúng được, streaming UI mượt → Bài 1, 2, 4
- Generative UI: tool trả data → render component động (chart / card / table) → Bài 3
- (Đã xong Buổi 10) Backend FastAPI, chống spam

## Setup (tự làm)

Chạy từ thư mục gốc repo (`llm-foundations-notes/`).

- [x] **Tạo app Next.js** cạnh backend:
      `pnpm create next-app@latest projects/p1-smart-copilot/web` → TypeScript, App Router, Tailwind, không cần
      `src/` (giống Buổi 9). Kiểm `web/.gitignore` có bỏ `node_modules`, `.next`, `.env*`.
- [x] **`web/.env.local`** (không commit): `APP_API_KEY=<cùng giá trị backend/.env>`,
      `BACKEND_URL=http://127.0.0.1:8000`. **Không** dùng `NEXT_PUBLIC_` (lý do: Buổi 9 Bài 5B).
      Tạo `web/.env.example` (chỉ tên biến) để commit — Buổi 12 deploy Vercel cần biết biến nào.
- [x] **Chạy 2 terminal**: (1) trong `backend/`: `uv run fastapi dev app/main.py`,
      (2) trong `web/`: `pnpm dev` → mở http://localhost:3100 (đổi port trong `package.json`: `next dev -p 3100`).
- [ ] Đọc nhanh (docs Next.js 16 trong `web/node_modules/next/dist/docs/01-app/`): `01-getting-started/15-route-handlers.md`;
      `02-guides/streaming.md` mục "Streaming in Route Handlers" + "What can affect streaming";
      `02-guides/environment-variables.md` (biến server vs `NEXT_PUBLIC_`).

Kết quả setup _(Claude kiểm, 2026-10-19, theo yêu cầu: đọc file + `curl`, không in giá trị key)_:

- Next.js **16.4.2**, React 19.3, Tailwind 4; `web/` chạy port **3100** (`package.json`), backend `:8000/health` → ok.
- `APP_API_KEY` trong `web/.env.local` **trùng** `backend/.env`, không có `NEXT_PUBLIC_`.
- `web/.gitignore`: đổi `.env*` (mặc định) thành `.env` + `.env.local` → `.env.example` commit được (đã kiểm
  `git check-ignore`). Đánh đổi: `.env.development.local`, `.env.production`… giờ **không** bị bỏ qua nữa. Cách chặt
  hơn: giữ `.env*` và thêm dòng `!.env.example`.
- `.gitignore` gốc repo: thêm `.env.local` (thừa vì `web/.gitignore` đã bỏ, giữ làm lưới an toàn).
- `backend/app/main.py`: CORS `origins` đổi `localhost:3000` → `localhost:3100`. Sau Bài 1 trình duyệt chỉ gọi
  `/api/chat` cùng origin, Next server gọi FastAPI server-to-server (CORS chỉ trình duyệt kiểm) → dòng này **không còn
  cần**. Tự kiểm sau Bài 1: bỏ `3100` khỏi `origins`, chat vẫn chạy?

## Nợ từ Buổi 10 (làm lúc rảnh, không chặn Buổi 11)

- [ ] `session10/notes.md`: 11 dòng "Bản của mình" (Bài 1–5 + câu phỏng vấn 1); đọc lại câu 2, 3 (đang là bản Claude)
- [ ] `session10/notes.md:48`: đọc docs Function calling streaming, SDK "Retries", FastAPI Dependencies → tick
- [ ] (Tuỳ chọn) `test_tool_loop_two_steps` dùng `ORDERS_CSV` thay vì `data/orders.csv` thật
- [ ] (Tuỳ chọn) `Retry-After` tính theo mốc cũ nhất thay vì cố định 60s — Bài 2 buổi này sẽ hiện số này cho user
- [ ] Nợ Buổi 9 còn lại (`session10/notes.md:53-55`): notes Buổi 9, bấm Dừng trên trình duyệt thật, 3 câu PV Buổi 9
- [ ] Notion: tick Buổi 9, Buổi 10 + dòng Status; nhật ký Tuần 2

## Bài 1 — Route Handler

_(Claude ghi, 2026-10-19, theo yêu cầu. Nguồn: `curl` tới `localhost:3100/api/chat` (Next dev) + FastAPI `:8000` chạy
thật, `tail backend/logs/cost.jsonl`; thời gian đo bằng `curl -N` + perl timestamp, 1 lần mỗi câu.)_

Code: `web/app/api/chat/route.ts` (1 hàm `POST`). Luồng: kiểm env → `request.text()` → `fetch` FastAPI kèm
`X-API-Key` + `signal: request.signal` → lỗi thì chuyển status → OK thì trả thẳng `upstream.body`.

| Thử                                       | Kết quả                                                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Stream "Xin chào"                         | `200`, 12 `delta` rải từ 1905ms → 2128ms rồi `done` → chảy từng mảnh qua Route Handler, không bị dồn cục    |
| Header stream                             | `content-type: text/event-stream`, `cache-control: no-cache`, `x-accel-buffering: no` (đặt tay ở `route.ts`) |
| Tool "Đơn nào của An đang giao?"          | `tool_call` 2031ms → `tool_result` 2613ms → `delta` đầu 4304ms → `done` 4627ms. TTFT ~4.3s (giống Buổi 10) |
| `{"message":""}`                          | `422` (FastAPI validate, Route Handler không validate lại)                                                  |
| 7 request liên tiếp                       | `422 ×5` rồi `429 ×2` + `retry-after: 60`                                                                   |
| FastAPI tắt                               | `502 {"error":"Backend unavailable"}`, log lỗi ở terminal `pnpm dev`                                        |
| Ngắt sau ~5s (`curl -m 5`, như Ctrl+C)    | backend log `"status": "cancelled"`, `latency_ms: 4973` → huỷ đi tới tận FastAPI                            |
| Key sai (401)                             | **Chưa thử end-to-end**: Next 16 không cho chạy 2 `next dev` cùng thư mục ("Another next dev server is already running") nên không thử được với key giả mà không đụng `.env.local`. FastAPI trực tiếp với key sai → `401 {"detail":"Invalid API Key"}`; đọc code `route.ts:21-27` → Route Handler sẽ trả `401` body rỗng |

Quan sát:

- _(Claude ghi)_ **Không đọc stream vẫn tốn tiền**: bản tạm Bước 4 trả `{"status":200}` mà không đọc `upstream.body`, backend
  vẫn chạy hết và log `status: ok` (câu ngắn, vừa buffer mạng nên FastAPI không biết không ai đọc) → lý do phải
  chuyển stream thật + `signal`.
- _(Claude ghi)_ **422 vẫn bị trừ lượt rate limit**: 5 request body rỗng (422) xong request 6 bị 429 → `rate_limit`
  (dependency) chạy **trước** validate body. Lợi: request rác cũng bị đếm (chống spam). Hại: gõ sai vài lần cũng hết lượt.
- _(Claude ghi)_ **Mọi request tới FastAPI giờ đi từ Next server** → backend đếm rate limit theo IP của Next server, dùng
  chung cho mọi user (lần thử đầu: cả 7 request đều 429 vì lượt đã bị các lần thử trước dùng hết). Local thì curl /
  trình duyệt vốn cũng là `127.0.0.1` nên **chưa chứng minh** được ở local; lên deploy (Buổi 12) sẽ thành lỗi thật →
  Next phải gửi IP thật (vd `X-Forwarded-For`) và backend chỉ tin header đó từ Next. Cùng vấn đề câu PV 3 Buổi 10.
- _(Claude ghi)_ `fetch` với `body: request.body` (stream) ném `TypeError: RequestInit: duplex option is required when
  sending a body` (đã tái hiện bằng Node) → dùng `request.text()` (chuỗi) cho gọn.
- _(Claude ghi)_ `Response.json({ status: 500 })` chỉ đặt 500 **trong body**, HTTP vẫn `200` → status phải ở tham số
  thứ 2: `Response.json(body, { status: 502 })`. Lỗi `headers` chưa khai báo nằm trong `try` → `ReferenceError` sẽ bị
  `catch` biến thành 502 "Backend unavailable" (bug tự giấu) — `tsc` bắt được trước khi chạy.

Còn mở (tự quyết):

- [x] `route.ts:27`: body lỗi đang `null` → gửi JSON (`await upstream.text()` hoặc `{ error }`) để mọi lỗi cùng 1 dạng
      _(Claude sửa, 2026-10-19, theo yêu cầu)_: lấy `detail` của FastAPI nếu là chuỗi, không thì "Invalid request" →
      `{ error }`. Đã thử: 422 → `{"error":"Invalid request"}`, 429 → `{"error":"Rate limit exceeded"}` + `retry-after: 60`
- [ ] 401: chuyển nguyên (hiện tại) hay log + 500 "Server misconfigured" (key sai là lỗi cấu hình server, không phải lỗi user)
      → đang giữ **chuyển nguyên** (`route.ts` không có nhánh riêng cho 401); ghi lý do ở "Quyết định của mình"
- [x] Thử 401 thật: đổi `APP_API_KEY` trong `.env.local`, restart `pnpm dev`, curl, rồi trả key lại
      → `HTTP/1.1 401 Unauthorized` + `{"error":"Invalid API Key"}` (trình duyệt bị báo "không có quyền" dù nó không
      gửi key). Trả key đúng + restart → "Xin chào" stream lại bình thường (12 `delta` + `done`)
- [ ] Thử từ **trình duyệt** (Bài 2/4): DevTools Network + Sources không còn thấy key; xem có bị nén (gzip) làm dồn
      chữ không (curl không gửi `Accept-Encoding` nên chưa kiểm được)

Quyết định của mình (body A vs B, `throw` vs `return 500` ở bước kiểm env, 401):

- Bản của mình:

Key còn lộ không (Network + Sources), chữ còn chảy từng mảnh không, Dừng có tới backend không:

- Bản của mình:

Lỗi 401 / 429 từ FastAPI chuyển tiếp thế nào (status, `Retry-After`):

- Bản của mình:

## Bài 2 — Đọc stream có type

_(Claude ghi, 2026-10-19, theo yêu cầu. Nguồn: test Node chạy chính `lib/*.ts` (tsc 5.9.3 `--strict`, file test ở
scratchpad, không commit) + 1 lượt hỏi thật qua `localhost:3100/api/chat` → `readEvents` → `applyEvent` / `errors.ts`
(gọi từ Node, **chưa** bấm trên trình duyệt), `tail backend/logs/cost.jsonl`. `pnpm exec tsc --noEmit` + `pnpm lint`
trong `web/` → sạch.)_

Code (ai viết):

| File                   | Nội dung                                                                                         | Ai viết                                            |
| ---------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------- |
| `web/lib/types.ts`     | `ChatEventMap` → `ChatEvent` (union sinh bằng mapped type), `TextPart`, `ToolPart`, `AssistantMessage` | mình viết bản đầu, Claude sửa theo yêu cầu        |
| `web/lib/sse.ts`       | `parseEvent(raw)` (type guard `isEventName`) + `readEvents(body)` (async generator)              | mình (Claude review nhiều vòng)                    |
| `web/lib/applyEvent.ts`| hàm thuần `(message, event) → message mới`                                                      | mình viết 4 case; Claude sửa case `error` + `{ }` |
| `web/lib/errors.ts`    | `errorFromResponse(res)`, `errorFromException(err)` (`null` = bấm Dừng)                          | Claude viết theo yêu cầu                           |
| `web/app/page.tsx`     | trang thử: form + Gửi/Dừng + `<pre>` JSON (Bài 3 thay bằng component)                           | Claude viết theo yêu cầu                           |

Test đơn vị (Node, gọi thẳng hàm):

| Hàm                 | Thử                                                    | Kết quả                                                 |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------- |
| `parseEvent`        | event đúng / `tool_result ok:false`                    | `{ event, data }` đúng                                  |
| `parseEvent`        | JSON hỏng / tên lạ `ping` / thiếu `data:`              | `null` cả 3                                             |
| `readEvents`        | 2 event 1 chunk / 1 event cắt 2 chunk / chữ `ạ` cắt đôi | đủ event, `ạ` nguyên vẹn                                |
| `readEvents`        | event cuối không có `\n\n`                             | vẫn ra (nhờ flush sau vòng lặp)                         |
| `readEvents`        | `break` sớm / stream lỗi giữa chừng (AbortError)       | lock được nhả; lỗi lên tới caller, không lặp vô hạn    |
| `applyEvent`        | 2 tool **cùng tên** `get_weather`, kết quả về **ngược** | ghép đúng theo `call_id` (Hà Nội ↔ `a`, Đà Nẵng ↔ `b`) |
| `applyEvent`        | `error` giữa chừng / gọi lại trên cùng input            | giữ parts + thêm `error`; message cũ không đổi          |
| `errorFromResponse` | 429 + `Retry-After: 60` / không header / header là ngày | "…sau 60 giây" / "…sau ít phút" / "…sau ít phút"       |
| `errorFromResponse` | 401 / 502 / 500 body HTML / 422 JSON                    | lỗi cấu hình / không kết nối / không kết nối / `error` của body |
| `errorFromException`| AbortError (giả + `fetch` bị abort thật) / `fetch` lỗi mạng thật | `null` / "Không kết nối được…" (`TypeError`) |

Hỏi thật qua `/api/chat` (1 lần mỗi câu, ms tính từ lúc gửi):

| Câu hỏi                                              | Parts cuối                                   | Part đầu | Chữ đầu | Tổng | `steps` |
| ---------------------------------------------------- | -------------------------------------------- | -------- | ------- | ---- | ------- |
| "Xin chào"                                           | text                                         | 1445     | 1445    | 1819 | 1       |
| "Đơn nào của An đang giao?"                          | `query_orders` ok (0 đơn) → text             | 1376     | 2465    | 2777 | 2       |
| "Tuần này món nào bán chạy nhất?"                    | `sales_summary` ok (`data` là list) → text   | 2117     | 4584    | 5176 | 2       |
| "Mai Đà Nẵng mưa không, có nên giao đơn không?"      | `get_weather` ok (25.3°C, ít mây) → text     | 1917     | 5297    | 5950 | 2       |
| "So sánh doanh thu theo ngày với thời tiết Hà Nội…"  | `sales_summary` ok, `get_weather` ok → text  | 1368     | 5611    | 6403 | 3       |
| Câu 2, Dừng sau 2.5s                                 | `query_orders` ok, chưa có text → `stopped`  | 1836     | —       | 2508 | —       |
| 6 câu "Hi" liên tiếp                                 | câu 1–5 ok, câu 6 `429` sau 19ms → "Bạn hỏi nhanh quá, thử lại sau 60 giây" | | | | |

- Dừng: backend log `"status": "cancelled"`, `latency_ms: 2473`, `tools: ["query_orders"]` → huỷ đi tới tận FastAPI.
- Key: tìm trong HTML trang + 16 JS chunk của `localhost:3100` → **0** lần (so khớp chuỗi, không in key).

Quan sát:

- _(Claude ghi)_ **Câu có tool: part đầu ~1.4–2.1s nhưng chữ đầu ~2.5–5.6s** → chờ 3–4s mà chỉ có `<pre>` thì như treo.
  Bài 3 nên hiện component / "đang tra cứu…" ngay khi có ToolPart `running`, không đợi chữ.
- _(Claude ghi)_ Câu 5 gọi 2 tool ở **2 bước riêng** (`steps: 3`), không cùng 1 bước → lần này **chưa** gặp thật
  trường hợp "2 tool cùng bước", chỉ unit test (2 `get_weather`, kết quả về ngược) kiểm.
- _(Claude ghi)_ Câu 3 model tự nói "chưa lọc riêng tuần này" → `sales_summary` không có tham số ngày, giới hạn của
  tool backend chứ không phải lỗi frontend.
- _(Claude ghi)_ `Retry-After` luôn là 60 dù có thể còn ít giây hơn → nợ Buổi 10 (đã ghi ở "Nợ từ Buổi 10").
- _(Claude ghi)_ Bug gặp khi viết (để nhớ):
  - `JSON.parse` trả `any` → `return JSON.parse(data)` (mất tên event) vẫn qua `tsc`.
  - `as` chỉ làm `tsc` im, không chặn `ping` lúc chạy → cần type guard.
  - `getReader()` trong vòng lặp → `ReadableStream is locked`.
  - `try/catch` trong `while` nuốt lỗi → lặp vô hạn khi stream lỗi → đổi thành `try { while } finally { releaseLock }`.
  - `if (buffer.trim() === "") continue` trước `for` → mất hết event (vì `buffer` sau `pop()` thường rỗng).
  - `push` / gán `parts[i] =` → mutate message cũ (Strict Mode gọi updater 2 lần → chữ nhân đôi).

Còn mở (tự làm):

- [ ] Thử trên **trình duyệt**: chữ chảy mượt, Dừng hiện "Đã dừng", Network chỉ có `/api/chat`, Response thấy event
      đến từng cái (gộp với mục "Thử từ trình duyệt" của Bài 1)
- [ ] (Tuỳ chọn) 422 đang hiện tiếng Anh `"Invalid request"` (chuỗi trong `route.ts`) → đổi sang tiếng Việt?

Vì sao ghép `tool_result` theo `call_id` (không theo thứ tự / theo `name`):

- _Bản tham khảo do Claude viết:_ 1 bước model có thể gọi nhiều tool, kể cả **cùng 1 tool** với tham số khác (2
  `get_weather` cho 2 thành phố) → `name` trùng. Thứ tự kết quả cũng không chắc giống thứ tự gọi (backend hiện chạy
  tuần tự nên đang khớp, nhưng đổi sang chạy song song là lệch). `call_id` do model sinh, duy nhất cho mỗi lần gọi,
  và backend gửi kèm ở cả `tool_call` lẫn `tool_result` → là khoá duy nhất ghép đúng. Unit test: 2 `get_weather`,
  kết quả về ngược → vẫn đúng chỗ.
- Bản của mình:

Vì sao tách `applyEvent` thành hàm thuần:

- _Bản tham khảo do Claude viết:_ (1) **Test được không cần React**: input → output, như test ở trên.
  (2) **An toàn với Strict Mode**: React dev gọi updater 2 lần; hàm thuần (không mutate, không `setState` bên trong)
  gọi 2 lần vẫn ra cùng kết quả. (3) **Tách lớp**: `sse.ts` lo byte → event, `applyEvent` lo event → state, component
  chỉ render → Bài 4 (widget) và route giả (Bài 5) dùng lại được nguyên. Giống reducer của Redux / `useReducer`.
- Bản của mình:

## Bài 3 — Generative UI

_(Claude ghi, 2026-10-20, theo yêu cầu "kiểm Bài 3". Nguồn: đọc code commit `6b54d8c`; `pnpm exec tsc --noEmit` +
`eslint .` trong `web/` → sạch; 4 câu hỏi thật qua `curl -N localhost:3100/api/chat` + perl timestamp, 1 lần mỗi câu.
Thời gian = lúc **event** tới (`tool_call` → hiện trạng thái, `tool_result` → hiện component), **chưa** đo lúc trình
duyệt vẽ — chưa mở trình duyệt.)_

Code (ai viết, theo comment đầu file):

| File                         | Nội dung                                                                                                   | Ai viết             |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------- |
| `components/ToolView.tsx`    | registry `TOOL_UI` (name → câu `running` + `render`), 3 trạng thái `running` / `error` / ok, tool lạ → `<details>` JSON | Claude theo yêu cầu |
| `components/OrdersTable.tsx` | bảng đơn, nhãn trạng thái tiếng Việt, 0 đơn → "Không có đơn nào khớp", cuộn khi nhiều đơn, dòng tổng     | Claude theo yêu cầu |
| `components/SalesChart.tsx`  | tự vẽ bằng `div` + %: nhãn toàn ngày → cột dọc, còn lại → thanh ngang xếp hạng                             | Claude theo yêu cầu |
| `components/WeatherCard.tsx` | card nhiệt độ + mô tả + giờ cập nhật                                                                       | Claude theo yêu cầu |
| `lib/format.ts`              | `formatVnd` (`Intl.NumberFormat` VND), `formatDate` (tách chuỗi, không `new Date()`)                       | Claude theo yêu cầu |
| `app/page.tsx`               | thay `<pre>` bằng `parts.map` → text / `ToolView`                                                          | Claude theo yêu cầu |

| Câu hỏi                                                    | Tool + component hiện ra                                                   | Thời gian tới component | Thời gian tới chữ đầu | Ghi chú |
| ---------------------------------------------------------- | -------------------------------------------------------------------------- | ----------------------- | --------------------- | ------- |
| "Đơn nào của An đang giao?"                                | `query_orders(An, shipping)` → OrdersTable "Không có đơn nào khớp"         | 4046ms                  | 5104ms                | `tool_call` 3860ms (lần này model nghĩ lâu), tool ~0.2s |
| "Tuần này món nào bán chạy nhất?"                          | `sales_summary(product)` → SalesChart thanh ngang                          | 1285ms                  | 3296ms                | component trước chữ ~2s |
| "Mai Đà Nẵng mưa không, có nên giao đơn không?"            | `get_weather(Đà Nẵng)` → WeatherCard                                       | 2734ms                  | 4440ms                | tool gọi mạng ~1.2s → trạng thái "Đang xem thời tiết Đà Nẵng…" hiện lâu nhất |
| "So sánh doanh thu theo ngày với thời tiết Hà Nội hôm nay" | `sales_summary(day)` → SalesChart cột dọc, rồi `get_weather(Hà Nội)` → WeatherCard | 1880ms / 2938ms   | 4514ms                | **2 tool cùng 1 bước** (`steps: 2`) — lần này gặp thật (Bài 2 chỉ có unit test) |

Quan sát:

- _(Claude ghi)_ **Component hiện trước chữ 1–2s ở cả 4 câu** → người dùng thấy số liệu sớm, đây là lợi ích chính của
  Generative UI trong project này.
- _(Claude ghi)_ **Khoảng trống trước `tool_call` (1.2–3.9s) chỉ có "Đang trả lời…"**: backend gửi `tool_call` **sau** khi
  bước stream xong, ngay trước lúc chạy tool (`main.py:123-130`), nên trạng thái "Đang tra…" chỉ hiện trong lúc tool
  chạy (0.02–1.2s), không phủ được lúc model đang quyết định. Muốn sớm hơn thì backend phải gửi khi nhận
  `response.output_item.added` (giả thuyết, chưa thử).
- _(Claude ghi)_ 2 tool cùng bước: backend chạy **tuần tự** → `tool_call` của `get_weather` chỉ tới sau khi
  `sales_summary` xong (1880ms) → 2 trạng thái không hiện cùng lúc.
- _(Claude ghi)_ Rủi ro: `data as OrdersData` chỉ là cast. Nếu backend đổi hình dạng `data` (vd thiếu `orders`) thì
  `data.orders.length` ném lỗi lúc render → không có error boundary nên **cả trang trắng**. Cách chặn (chưa làm): bọc
  `ToolView` bằng error boundary, hoặc kiểm tối thiểu / Zod ở `render` trước khi đưa vào component.
- _(Claude ghi)_ `SalesChart` đoán "theo ngày / theo món" từ **nhãn** (regex ngày) vì `render` chỉ nhận `data`; chắc hơn
  là truyền `part.arguments.group_by` vào.

Còn mở (tự làm):

- [ ] Mở **trình duyệt** hỏi 4 câu trên: component vẽ đúng (bảng / chart / card), trạng thái "Đang…" có hiện, chart
      cột dọc với 14 ngày có cần cuộn ngang không (gộp với mục "Thử trên trình duyệt" Bài 1, 2)
- [ ] Thử 1 tool lỗi để thấy cảnh báo ⚠️ (dễ nhất ở Bài 5 bằng route giả)

Chart: thư viện hay tự vẽ, vì sao:

- Bản của mình:

`data` từ mạng: cast type hay validate (Zod), vì sao:

- Bản của mình:

Generative UI (backend trả data, frontend chọn component) vs để LLM sinh HTML/JSX:

- Bản của mình:

## Bài 4 — Widget + streaming UI

_(Claude ghi, 2026-10-20, theo yêu cầu. Nguồn: Chrome headless (playwright-core + Chrome 155, script ở scratchpad, không
commit) chạy trên `pnpm dev` + FastAPI thật; "giả" = chặn `/api/chat` bằng `page.route` của Playwright (**chưa** phải
route giả Bài 5); `tail backend/logs/cost.jsonl`; `curl`. `pnpm exec tsc --noEmit` + `pnpm lint` trong `web/` → sạch.)_

Code (ai viết):

| File                        | Nội dung                                                                                         | Ai viết                       |
| --------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------- |
| `lib/types.ts`              | `UserMessage`, `AssistantTurn` (`status: "streaming" \| "done" \| "stopped"`, `message` lồng bên trong), `ChatMessage` | mình viết (Claude review 2 vòng) |
| `components/ChatWidget.tsx` | bước 2–6: bong bóng + khung, `messages[]` + `updateTurn(id)`, Dừng, chỉ báo / lỗi / usage, tự cuộn | Claude theo yêu cầu           |
| `app/embed/page.tsx`        | chỉ có widget, bọc `<div data-embed>`                                                            | Claude theo yêu cầu           |
| `app/page.tsx`              | trang demo (câu mẫu + link `/embed`) + widget; **bỏ** trang thử Bài 2–3 (bản cũ ở `6b54d8c`)    | Claude theo yêu cầu           |
| `app/globals.css`           | `body:has([data-embed]) { background: transparent }`                                             | Claude theo yêu cầu           |
| `embed-test/index.html`     | trang "Quán Cà Phê Demo" ở :5500, `<iframe>` 420×640 góc phải dưới                               | Claude theo yêu cầu           |

| Thử                                                  | Kết quả                                                                                                     |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| 2 câu liên tiếp ("bán chạy nhất", "đơn đang giao")   | `200` 5.4s / 4.3s, 2 cặp hỏi–đáp đúng thứ tự, chart + bảng trong khung. Bảng rộng 502px tự cuộn ngang trong ô, list 382px không tràn |
| Đang stream                                          | Dừng hiện, Gửi ẩn; gõ câu khác + Enter → vẫn **1** request                                                 |
| Dừng sau chữ đầu ("Mai Đà Nẵng mưa không…")          | giữ 202 ký tự + "Đã dừng"; backend `"status": "cancelled"`, `latency_ms: 5792`, `tools: ["get_weather"]`; câu sau `200` |
| "Xin chào"                                           | "Đang trả lời…" hiện ngay sau Gửi → chữ → `461 in · 16 out · $0.00005`                                     |
| 429 giả (`retry-after: 42`)                          | "Bạn hỏi nhanh quá, thử lại sau 42 giây" dưới đúng tin đó                                                  |
| `event: error` giữa stream (giả)                     | giữ "Chữ trước lỗi." + lỗi đỏ bên dưới; Gửi hiện lại                                                       |
| Cuộn (list ~400px cao)                               | A. ở đáy → theo chữ (`gap 0`). B. cuộn lên giữa chừng: nội dung 811 → 1201px, `scrollTop` vẫn 0. C. đang cuộn lên mà gửi câu mới → về đáy. D. cuộn lên, đóng + mở lại → về đáy |
| `/embed`                                             | `200`, title "Smart Copilot", hỏi được                                                                     |
| iframe từ `localhost:5500`                           | iframe tải, hỏi "Mai Đà Nẵng mưa không?" → WeatherCard + chữ + usage. Request `/api/chat` đi từ frame `:3100/embed`, `Origin: http://localhost:3100`, `Sec-Fetch-Site: same-origin`; log dev **không** có cảnh báo `allowedDevOrigins` |
| `curl -D - localhost:3100/embed` (dev)               | **không** có `X-Frame-Options`, **không** có `Content-Security-Policy`                                      |
| `http.server --directory embed-test`                 | `/../backend/.env` → `404`                                                                                  |
| Nền trong suốt cho `/embed`                          | **Chưa đạt**: CSS trả về thiếu rule `data-embed` dù đã restart `pnpm dev` (12:23:10) → iframe vẫn là ô đen 420×640. Tailwind compile thẳng `globals.css` thì **có** rule; class mới trong `.tsx` (`.list-disc`) thì có → chỉ nội dung `globals.css` bị cũ |

Quan sát:

- _(Claude ghi)_ **Bug: bấm Dừng → form gửi luôn câu đang gõ** (test bắt được: 2 request). React dùng lại **cùng 1
  `<button>`**, đổi `type="button"` → `"submit"` ngay trong lúc xử lý click → hành động mặc định của click thành submit.
  Sửa: `key="stop"` / `key="send"` → React tạo nút mới. Sau sửa: 1 request. Trang thử cũ (`page.tsx`) có cùng bug, đã bỏ.
- _(Claude ghi)_ Ẩn nút Gửi **chưa đủ**: form chỉ có 1 ô nhập thì Enter vẫn submit dù không có nút submit → phải chặn
  `streaming` trong `handleSubmit`.
- _(Claude ghi)_ `streaming` **suy ra từ `messages`**, không thêm state, không dùng `abortRef` (đổi ref không render lại).
- _(Claude ghi)_ Tạo `id` **ngoài** updater: Strict Mode gọi updater 2 lần → `crypto.randomUUID()` bên trong ra 2 id
  khác nhau. `React.FormEvent` đã deprecated trong `@types/react` 19.3 → dùng `React.SubmitEvent`.
- _(Claude ghi)_ Tự cuộn: `nearBottomRef` chỉ đo **lúc cuộn**; nội dung dài thêm (card 300px) không bắn scroll nên giá
  trị giữ từ lần trước. Không dùng `behavior: "smooth"`: cuộn mượt chưa xong thì delta sau tới, scroll event giữa chừng
  đo ra "không ở đáy" → tự ngừng theo.
- _(Claude ghi)_ **iframe che click** trang chủ cả vùng 420×640 kể cả khi khung đóng (`elementFromPoint(980, 400)` →
  `IFRAME#copilot`). Widget thật đổi kích thước iframe bằng `postMessage` (đóng = cỡ bong bóng). Chưa làm.
- _(Claude ghi)_ Model trả **markdown** (`**900.000₫**`, `**ít mây**`) mà UI hiện chữ thô → thấy dấu `**`. Câu "đơn đang
  giao" còn liệt kê lại 9 đơn bằng chữ ngay dưới bảng → trùng, dài.
- _(Claude ghi)_ Đóng khung lúc đang stream **không** dừng stream (state nằm ở `ChatWidget`, khung chỉ ẩn). Mở lại thì về
  đáy, không về chỗ đang đọc.
- _(Claude ghi)_ Backend `ChatRequest` chỉ nhận 1 `message` → giao diện hiện nhiều tin nhưng **chưa** là hội thoại nhiều
  lượt, model không nhớ câu trước (như đề bài đã lưu ý).

Còn mở (tự làm):

- [ ] Nền trong suốt: Ctrl+C `pnpm dev` → `rm -rf .next/dev/cache/turbopack` (trong `web/`) → `pnpm dev` → mở :5500 xem
      ô đen còn không. Giả thuyết (chưa chứng minh): cache Turbopack + loader CSS tự cấu hình (`next.config.ts`) không
      nhận thay đổi của `globals.css`
- [ ] Tự thử trong widget: 6 câu liên tiếp → câu 6 hiện 429 thật (lần này mới thử 429 **giả**)
- [ ] Markdown thô: render markdown (vd `react-markdown`) hay sửa prompt backend ("UI đã hiện bảng, chỉ tóm tắt")
- [ ] Kiểm header bản build (`pnpm build && pnpm start`): có `X-Frame-Options` / CSP không (mới kiểm ở dev)
- [ ] (Tuỳ chọn) iframe đổi kích thước bằng `postMessage`
- [x] (Tuỳ chọn) `lib/types.ts`: thêm `;` dòng 62, 68, 69, 71, bỏ 1 dòng trống thừa, trả thụt lề dòng 15–16
      _(Claude sửa, 2026-10-20, theo yêu cầu)_

iframe có bị chặn không; iframe vs `<script>` nhúng thẳng:

- _Bản tham khảo do Claude viết:_
  - **Bị chặn không**: không. `curl` `/embed` ở dev không có `X-Frame-Options` lẫn CSP, nhúng từ :5500 chạy thật. Docs
    Next 16 chỉ có 2 header này ở dạng **ví dụ tự thêm** (`headers.md` mục X-Frame-Options; `content-security-policy.md`
    dùng `frame-ancestors 'none'`) → mặc định không gửi (đã kiểm ở dev, **chưa** kiểm bản build). Lên prod nên thêm
    `frame-ancestors` liệt kê đúng domain được nhúng (chống clickjacking), không mở cho mọi trang.
  - **CSS**: iframe là document riêng → CSS 2 bên không đụng nhau (Tailwind preflight của widget không reset trang chủ).
    Script chèn thẳng thì dùng chung CSS → cần Shadow DOM hoặc tiền tố class.
  - **Gọi API / key**: iframe gọi `/api/chat` cùng origin của nó (đã thấy `Sec-Fetch-Site: same-origin`) → không cần
    CORS, key vẫn ở server. Script chạy trong origin trang chủ → gọi API của mình là cross-origin → cần CORS.
  - **Cookie** (kiến thức chung, **chưa thử**: :5500 và :3100 cùng site `localhost` nên local không tái hiện được): khi
    2 domain khác nhau, cookie của iframe là cookie bên thứ ba → trình duyệt chặn / tách riêng → đăng nhập trong widget
    khó. Script thì dùng cookie của trang chủ.
  - **Bảo mật**: same-origin policy → trang chủ không đọc được DOM / dữ liệu trong iframe và ngược lại. Script chạy với
    toàn quyền trên trang chủ → trang chủ phải tin script hoàn toàn, và JS của trang chủ cũng đọc / sửa được widget.
  - **Bố cục**: iframe kích thước cố định → che click cả vùng (đã thấy) → cần `postMessage` đổi kích thước. Script đặt
    vị trí tự do.
- Bản của mình:

Những gì làm cho stream "mượt" (chỉ báo, cuộn, Dừng):

- _Bản tham khảo do Claude viết:_
  - **Không để khung trống**: "Đang trả lời…" khi tin chưa có part nào (1.2–3.9s đầu, đo ở Bài 3); có tool thì
    `ToolView` hiện "Đang tra…"; component hiện trước chữ 1–2s.
  - **Tự cuộn có điều kiện**: chỉ cuộn khi đang cách đáy < 50px (`nearBottomRef`, ref chứ không state), gán `scrollTop`
    thẳng; gửi câu mới / mở lại khung → về đáy. Cuộn lên đọc thì không bị kéo xuống.
  - **Khoá Gửi + Dừng**: `streaming` suy từ `messages`, chặn cả Enter; Dừng = `AbortController` → huỷ tới FastAPI
    (`cancelled`), giữ chữ đã có + "Đã dừng"; 2 nút có `key` riêng.
  - **Lỗi / usage dưới từng tin**: lỗi không xoá chữ đã có; usage nhỏ dưới mỗi câu trả lời.
- Bản của mình:

## Bài 5 — Kiểm tra

_(Claude ghi, 2026-10-20, theo yêu cầu. Nguồn: `curl` từng kịch bản `/api/chat-mock`; Chrome headless (playwright-core,
script ở scratchpad, không commit) bấm widget ở `/mock` (route giả) và `/` (route thật, FastAPI + OpenAI thật, 9 lượt
gọi); `tail backend/logs/cost.jsonl`; `.next/dev/logs/next-development.log`. ms tính từ lúc bấm Gửi, đo trên giao diện.)_

Code (Claude viết theo yêu cầu):

| File                         | Nội dung                                                                                                  |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| `app/api/chat-mock/route.ts` | `?scenario=` `ok` / `tool-error` / `mid-error` / `unknown-tool` / `rate-limit`; event có type `ChatEvent` + `wait` (chờ trước mỗi event); đúng dạng `backend/app/sse.py`; nghe `request.signal` để Dừng; prod → `404` |
| `app/mock/page.tsx`          | chọn kịch bản (radio) → `<ChatWidget endpoint="/api/chat-mock?scenario=…">`; client page + `useState` để khỏi bọc `<Suspense>` khi bật `cacheComponents` |
| `components/ChatWidget.tsx`  | thêm prop `endpoint` (mặc định `/api/chat`)                                                              |

| Thử                                 | Mong đợi                                         | Thực tế |
| ----------------------------------- | ------------------------------------------------ | ------- |
| Route giả: tool → delta → done      | trạng thái tool → component → chữ → usage        | ✅ "Đang trả lời…" 39ms → "Đang xem thời tiết Đà Nẵng…" 982ms → WeatherCard 2418ms → chữ chảy → `0 in · 0 out · $0.00000` |
| Route giả: `tool_result ok:false`   | cảnh báo nhỏ, chữ vẫn chảy, kết thúc bằng `done` | ✅ "Đang tra đơn hàng của An…" 883ms → "⚠️ Tool query_orders lỗi, thử lại sau" 2014ms → chữ chảy bên dưới → usage |
| Lỗi giữa stream (`event: error`)    | giữ chữ đã có + câu báo lỗi gọn                  | ✅ 15 delta "Doanh thu tuần này … tiếp theo là" giữ nguyên + "Có lỗi khi tạo câu trả lời, thử lại sau" (đỏ), không có usage |
| (thêm) Tool lạ `get_stock`          | fallback, không crash                            | ✅ "Đang chạy get_stock…" → `<details>` "Kết quả get_stock" → chữ → usage |
| (thêm) 429 giả                      | "thử lại sau N giây"                             | ✅ "Bạn hỏi nhanh quá, thử lại sau 42 giây" sau ~150ms |
| Bấm Dừng giữa chừng                 | giữ chữ đã có, "đã dừng", backend log `cancelled` | ✅ Route giả: Dừng ở 5358ms → giữ card + chữ tới "…không gọi" + "Đã dừng"; dev log `[api/chat-mock] ok: cancelled`. Route thật (Bài 4): `"status": "cancelled"`, `latency_ms: 5792` |
| 6 câu liên tiếp                     | câu 6 → "thử lại sau N giây" (429)               | ✅ Câu 1–5 "Hi" → `200` (1.4–3.7s, ~$0.00005/câu); câu 6 sau 97ms → "Bạn hỏi nhanh quá, thử lại sau 60 giây"; backend chỉ log 5 câu |
| 4 câu thật (sau khi chờ 65s)        | tool → component → chữ                           | ✅ An đang giao → OrdersTable "Không có đơn nào khớp" 9760ms, tổng 11430ms ⚠️ (xem quan sát). Bán chạy → SalesChart 1842ms, chữ 4174ms. Đà Nẵng → WeatherCard 2428ms, chữ 3846ms. Doanh thu + Hà Nội → 2 tool, component đầu 1304ms, chữ 5476ms, `steps: 3` |
| Nhúng iframe từ origin khác         | widget chạy                                      | ✅ (Bài 4) hỏi được từ :5500. ⚠️ Nền trong suốt chưa ăn (ô đen 420×640) — xem "Còn mở" Bài 4 |
| `pnpm lint`, `pnpm exec tsc --noEmit` | sạch                                           | ✅ cả 2 sạch |

Quan sát:

- _(Claude ghi)_ **Câu "An đang giao" sau 65s chờ: giao diện 11.4s nhưng backend `latency_ms: 3560`** → ~8s mất **trước**
  khi backend bắt đầu đo. 3 câu sau khớp (giao diện ≈ backend + ~0.2–0.4s). Chưa rõ ở lớp nào (Next dev / FastAPI /
  kết nối nguội sau khi nghỉ), **chưa điều tra**, mới gặp 1 lần.
- _(Claude ghi)_ Route giả dùng chung type `ChatEvent` với frontend → gõ sai tên event / thiếu field là `tsc` báo. Nhưng nó
  **không** kiểm backend: backend đổi hình dạng thì route giả vẫn xanh (giống OpenAI giả ở test Buổi 10).
- _(Claude ghi)_ `wait` trước mỗi event là bắt buộc: không chờ thì cả kịch bản tới trong 1 chunk, không thấy "Đang…",
  không kịp bấm Dừng.
- _(Claude ghi)_ 429 thật hiện **60 giây** (cố định, nợ Buổi 10), 429 giả hiện 42 → chứng minh số giây lấy đúng từ
  `Retry-After`.

Còn mở:

- [x] (Tuỳ chọn) Vitest cho `lib/sse.ts` + `applyEvent` _(Claude làm, 2026-10-20, theo yêu cầu)_: `pnpm add -D vitest`
      (5.0.5, chỉ vitest — không cần jsdom / Testing Library vì chỉ test hàm thuần), script `"test": "vitest run"`,
      `lib/sse.test.ts` (9 case) + `lib/applyEvent.test.ts` (6 case) → `pnpm test` **15/15 pass** (180ms).
      Kiểm test có bắt lỗi thật: cài 3 bug vào bản copy tạm (ghép theo `name`, `decode` không `stream`, `Object.assign`
      sửa part cũ) → lần đầu chỉ bắt 2/3 (case "không sửa message cũ" có part cuối là tool nên không đi vào nhánh nối
      chữ) → sửa case đó → bắt đủ 3/3. Cảnh báo khi cài: vitest muốn `@types/node` ≥ 22, repo đang `^20` (chạy vẫn
      được, `tsc` sạch vì `skipLibCheck`)
- [ ] Tự bấm lại `/mock` trên trình duyệt thật (Chrome có extension) cho 5 kịch bản

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

### 1. Generative UI là gì, bạn làm thế nào trong project? (Tool trả data → component)

### 2. Tối ưu streaming UX thế nào? TTFT vs tổng thời gian (Bộ 20 câu, D.2)

### 3. Tool call fail giữa stream thì backend và UI xử lý sao? (exit criteria Phase 01)

### 4. Vì sao không để API key ở frontend, Route Handler giải quyết thế nào?
