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

| Câu hỏi                                                    | Tool + component hiện ra | Thời gian tới component | Thời gian tới chữ đầu | Ghi chú |
| ---------------------------------------------------------- | ------------------------ | ----------------------- | --------------------- | ------- |
| "Đơn nào của An đang giao?"                                |                          |                         |                       |         |
| "Tuần này món nào bán chạy nhất?"                          |                          |                         |                       |         |
| "Mai Đà Nẵng mưa không, có nên giao đơn không?"            |                          |                         |                       |         |
| "So sánh doanh thu theo ngày với thời tiết Hà Nội hôm nay" |                          |                         |                       |         |

Chart: thư viện hay tự vẽ, vì sao:

- Bản của mình:

`data` từ mạng: cast type hay validate (Zod), vì sao:

- Bản của mình:

Generative UI (backend trả data, frontend chọn component) vs để LLM sinh HTML/JSX:

- Bản của mình:

## Bài 4 — Widget + streaming UI

iframe có bị chặn không; iframe vs `<script>` nhúng thẳng:

- Bản của mình:

Những gì làm cho stream "mượt" (chỉ báo, cuộn, Dừng):

- Bản của mình:

## Bài 5 — Kiểm tra

| Thử                                 | Mong đợi                                         | Thực tế |
| ----------------------------------- | ------------------------------------------------ | ------- |
| Route giả: tool → delta → done      | trạng thái tool → component → chữ → usage        |         |
| Route giả: `tool_result ok:false`   | cảnh báo nhỏ, chữ vẫn chảy, kết thúc bằng `done` |         |
| Lỗi giữa stream (`event: error`)    | giữ chữ đã có + câu báo lỗi gọn                  |         |
| Bấm Dừng giữa chừng                 | giữ chữ đã có, "đã dừng", backend log `cancelled` |         |
| 6 câu liên tiếp                     | câu 6 → "thử lại sau N giây" (429)               |         |
| Nhúng iframe từ origin khác         | widget chạy                                      |         |
| `pnpm lint`, `pnpm exec tsc --noEmit` | sạch                                           |         |

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

### 1. Generative UI là gì, bạn làm thế nào trong project? (Tool trả data → component)

### 2. Tối ưu streaming UX thế nào? TTFT vs tổng thời gian (Bộ 20 câu, D.2)

### 3. Tool call fail giữa stream thì backend và UI xử lý sao? (exit criteria Phase 01)

### 4. Vì sao không để API key ở frontend, Route Handler giải quyết thế nào?
