# Buổi 9 — SSE Streaming end-to-end (2h)

| Phần                                              | Thời lượng | Làm ở đâu                |
| ------------------------------------------------- | ---------- | ------------------------ |
| Setup: chép code session08 + tạo app Next.js       | ~15ph      | mục Setup                |
| Bài 1: SSE bằng tay, token giả                    | ~20ph      | `exercises.py`           |
| Bài 2: POST /chat/stream với OpenAI               | ~25ph      | `exercises.py`           |
| Bài 3: lỗi giữa stream + client ngắt              | ~20ph      | `exercises.py`           |
| Bài 4: Next.js đọc stream (fetch + ReadableStream) | ~30ph      | `web/app/page.tsx`       |
| Bài 5: test + SSE vs WebSocket                    | ~10ph      | `test_exercises.py`, notes |

Bài 2 + Bài 4 là cốt lõi (stream đi hết đường từ OpenAI → FastAPI → trình duyệt). Không kịp thì cắt phần
tuỳ chọn của Bài 5.

Checklist Notion Buổi 9:

- FastAPI `StreamingResponse` + format SSE (`data: ...`) → Bài 1, 2, 3
- Next.js client đọc stream (fetch + ReadableStream), render từng token → Bài 4
- Hiểu vì sao SSE thay vì WebSocket (câu phỏng vấn kinh điển) → Bài 5B + câu phỏng vấn cuối file

## Setup (tự làm)

- [ ] **Không cần cài thêm gói Python.** `StreamingResponse` có sẵn trong `fastapi`, `AsyncOpenAI` đã có.
- [ ] **Chép code từ `session08/exercises.py`** sang `session09/exercises.py` (mỗi buổi 1 file độc lập):
      app + `load_dotenv()`, `CORSMiddleware`, `/health`, `ChatRequest`, `verify_api_key`,
      `get_openai_client`, `client = AsyncOpenAI()`, `MODEL`, `PRICES`, `cost_usd`.
      Không cần: `/orders*`, `/slow/*`, `/boom`, `ChatResponse` (stream không trả 1 object).
- [ ] **Tạo app Next.js** ở `weeks/week02/session09/web/` (~ thư mục frontend riêng):
      `pnpm create next-app@latest weeks/week02/session09/web` → chọn TypeScript, App Router, không cần
      `src/`. Kiểm: `cd weeks/week02/session09/web && pnpm dev` → mở http://localhost:3000 thấy trang mặc định.
      `create-next-app` tự tạo `web/.gitignore` (bỏ `node_modules`, `.next`, `.env*`): mở ra kiểm trước khi commit.
- [ ] **Key cho frontend (chỉ học local):** tạo `web/.env.local` với 1 dòng
      `NEXT_PUBLIC_APP_API_KEY=<cùng giá trị APP_API_KEY trong .env gốc>`. Không commit file này.
      Đọc Bài 5B để biết vì sao cách này **không** dùng được cho production.
- [ ] **Chạy 2 terminal:** (1) `uv run fastapi dev weeks/week02/session09/exercises.py`,
      (2) `cd weeks/week02/session09/web && pnpm dev`.
- [ ] Đọc nhanh: MDN "Using server-sent events" mục "Event stream format"; FastAPI "Custom Response" mục
      `StreamingResponse`; MDN "Using readable streams" (`getReader()`).

## Nợ từ Buổi 8 (làm lúc rảnh, không chặn Buổi 9)

- [ ] `session08/notes.md`: 4 dòng "Bản của mình" (bảng so sánh + 3 câu phỏng vấn)
- [ ] (Tuỳ chọn) test `/chat` thành công bằng `app.dependency_overrides` (Bài 5 Buổi 9 cũng có, làm 1 lần)
- [ ] (Tuỳ chọn) dọn `session08`: bỏ `allow_credentials=True`, `| None` ở `get_order`, route `/boom`
- [ ] Nợ Buổi 7 vẫn còn (xem `session08/notes.md` mục "Nợ từ Buổi 7")
- [ ] Nhật ký Tuần 2 trên Notion (2–3 dòng "học được gì / vướng gì")

## Bài 1 — SSE bằng tay, token giả

| Thử                                        | Quan sát (curl -N) |
| ------------------------------------------ | ------------------ |
| `/stream/fake` đúng format                 | 200, `text/event-stream`, `cache-control: no-cache`, `transfer-encoding: chunked` (không có `content-length`). 7 event `data: <chữ>\n\n` + `data: [DONE]\n\n`. Byte đầu 0.001s, tổng 1.41s (7 × 0.2s) |
| cùng request, curl **không** `-N`          | In thẳng ra terminal: vẫn thấy chảy chữ (stdout tty xả theo dòng). Qua pipe (`curl … \| …`): 8 dòng tới cùng lúc khi stream xong; có `-N` thì cách nhau ~0.2s |
| a) chỉ 1 `\n` sau mỗi event                | curl: trông như cũ, chỉ mất dòng trống giữa các chữ. Theo chuẩn SSE, client gộp mọi dòng `data:` tới dòng trống đầu tiên (sau `[DONE]`) thành **1 event** `"Xin\nchào,\n…\n[DONE]"` → nhận 1 lần lúc cuối, hết chảy chữ, không nhận ra `[DONE]`. Kiểm lại ở Bài 4 |
| b) token có xuống dòng                     |                    |
| b') sửa bằng `json.dumps`                  | `data: "chào\nbạn"` nằm trên **1 dòng** (`\n` thành 2 ký tự `\` `n`), mọi chữ có `"…"`. `ensure_ascii=False` giữ tiếng Việt. `[DONE]` giữ nguyên (không dumps) → client so `[DONE]` trước rồi mới `JSON.parse` |
| c) `def` + `time.sleep`, 3 request song song | 3 token → mỗi req 0.63s, 3 req song song wall 0.67s → **không** dồn hàng (khác `/slow/async-block` 5s). Lý do: StreamingResponse nhận iterator thường thì bọc `iterate_in_threadpool` (starlette/responses.py:238) → mỗi `next()` chạy trong threadpool. Nhưng tốn 1 thread/lần chờ, pool 40 thread → nhiều stream đồng thời sẽ nghẽn; ưu tiên async generator |

1 event SSE gồm những gì, kết thúc bằng gì: _(Claude ghi)_

- 1 hoặc nhiều dòng `field: value` (`data:` bắt buộc; tuỳ chọn `event:`, `id:`, `retry:`), mỗi dòng hết bằng `\n`.
- Kết thúc event = **dòng trống** → cuối event luôn là `\n\n` (xem bằng `curl -sN … | od -c`).
- `data: [DONE]` chỉ là quy ước (OpenAI cũng dùng) để client biết stream xong, không phải chuẩn SSE.

Vì sao curl cần `-N`: _(Claude ghi)_

- curl ghi output qua buffer stdio. Ra terminal thì xả theo dòng (event kết thúc bằng `\n` → thấy ngay).
  Ra pipe/file thì xả theo khối vài KB → cả stream (144 byte) nằm trong buffer tới khi curl xong.
- `-N` (`--no-buffer`) tắt buffer đó → luôn thấy đúng nhịp server gửi.
- Bài học: server stream đúng nhịp nhưng bất kỳ lớp nào **gom dữ liệu** phía sau (buffer client, proxy
  nginx, CDN, gzip) đều làm mất hiệu ứng chảy chữ.

`StreamingResponse` khác `return dict` ở chỗ nào (status code, header gửi lúc nào): _(Claude ghi)_

- `return dict`: FastAPI serialize xong cả body → biết `content-length` → gửi status + header + body 1 lần.
- `StreamingResponse`: gửi status 200 + header **ngay** (byte đầu 0.001s), body gửi dần từng chunk
  (`transfer-encoding: chunked`, không có `content-length` vì chưa biết dài bao nhiêu).
- Hệ quả: lỗi giữa stream không đổi được status nữa (đã gửi 200) → phải báo lỗi bằng event (Bài 3).
- Route `def stream_fake` chỉ tạo response rồi return; phần chờ nằm trong async generator `fake_tokens()`
  (truyền `fake_tokens()` đã gọi, không await — StreamingResponse tự `async for` qua nó).

## Bài 2 — POST /chat/stream với OpenAI

| Câu hỏi                                | TTFT (event delta đầu) | Tổng thời gian | Số event delta | Token in / out | Cost |
| -------------------------------------- | ---------------------- | -------------- | -------------- | -------------- | ---- |
| "Xin chào"                             | 1.25s                  | 1.47s          | 12             | 25 / 16        | $0.0000105 |
| "Giải thích transformer trong 5 câu"   | 1.43s                  | 2.52s          | ~121 (lần chạy trước) | 30 / 152 (lần chạy trước) | $0.000079 |
| (so sánh) cùng câu, `/chat` không stream | —                    |                | —              |                |      |

TTFT vs tổng thời gian, user cảm thấy khác gì: _(Claude ghi)_

- TTFT ~1.2–1.4s cho cả 2 câu (chờ mạng + model đọc prompt + sinh token đầu) → gần như cố định.
  Phần sau TTFT tỉ lệ với độ dài: "Xin chào" thêm 0.22s, transformer thêm 1.09s.
- Không stream: user nhìn màn hình trống tới lúc xong (2.52s). Stream: thấy chữ sau 1.43s.
  Tổng thời gian không đổi, **cảm giác chờ** giảm; câu càng dài lợi càng rõ.
- 1 delta ≠ 1 token (121 delta / 152 token; 12 / 16) → tính tiền theo `usage`, không đếm delta.
  Delta có thể cắt giữa chữ tiếng Việt ("tr" + "úc") và chứa `"  \n"` → Bài 1b' (`json.dumps`) gặp thật.

Usage / cost có từ lúc nào trong stream, vì sao: _(Claude ghi)_

- Chỉ có ở event cuối `response.completed` (`event.response.usage`) → event `done` luôn đi sau mọi delta.
- Vì `output_tokens` chỉ biết khi model sinh xong. `usage` có thể `None` → nhánh `done` với 3 trường `None`.
- Kiểm cost: 25 × 0.10/1M + 16 × 0.50/1M = 0.0000105 ✓; 30 × 0.10/1M + 152 × 0.50/1M = 0.000079 ✓.

## Bài 3 — Lỗi giữa stream + client ngắt

| Tình huống                                   | Mã HTTP | Client thấy gì (curl -N) | Terminal in gì |
| -------------------------------------------- | ------- | ------------------------ | -------------- |
| MODEL sai (lỗi **trước** delta đầu)          | **200** | header SSE rồi `curl: (18) transfer closed with outstanding read data remaining`, 0 event | traceback `NotFoundError` (chưa dán log) |
| raise sau delta thứ 3, chưa bắt              | **200** | 3 delta (`Xin`, ` ch`, `ào`) rồi `curl: (18) transfer closed…`, không có `done` → client thấy câu cụt, không biết lỗi | traceback `RuntimeError` (chưa dán log) |
| raise sau delta thứ 3, bắt → `event: error`  |         |                          |                |
| MODEL sai, **có** try/except                 | **200** | 0 delta, `event: error` + `data: {"message": "Có lỗi…"}`, curl kết thúc bình thường (exit 0, không `(18)`) | `[stream error] NotFoundError …` (chưa dán log) |
| Ctrl+C giữa chừng                            | —       | —                        | `[stream cancelled] sau 80 delta` rồi `[stream closed] đã gửi 80 delta` → generator nhận `CancelledError`, dừng ngay |

Lỗi trước khi stream bắt đầu vs lỗi giữa stream, xử lý khác nhau thế nào: _(Claude ghi)_

- `StreamingResponse` gửi 200 + header **trước** khi chạy generator → mọi lỗi trong generator (kể cả
  `create()` lỗi ngay, MODEL sai) đều đã là 200. Không bắt → server cắt kết nối, curl `(18)`, client chỉ
  thấy câu cụt / rỗng, không biết lỗi.
- Giữa stream: chỉ còn cách bắt lỗi trong generator → log chi tiết (`type(e).__name__`) → gửi
  `event: error` với câu cố định (không `str(e)`) → kết thúc stream sạch (curl exit 0).
- Muốn lỗi **trước** delta đầu vẫn trả 502 đúng nghĩa: `await responses.create(...)` trong route, bọc
  try/except → `HTTPException(502)`, rồi mới `return StreamingResponse(...)` (tuỳ chọn, chưa làm).

Client ngắt thì server có dừng gọi OpenAI không, vì sao quan trọng: _(Claude ghi)_

- Có: Starlette 1.7.0 nghe `http.disconnect` rồi cancel task stream (`starlette/responses.py:267-282`)
  → generator nhận `CancelledError` ngay ở `await` đang chờ → log `cancelled` + `closed` (80 delta).
  Vòng `async for` qua stream OpenAI dừng.
- Nhưng `AsyncStream.close()` chỉ **tự gọi khi đọc hết** (docstring `openai/_streaming.py:245-249`) → bị
  cancel giữa chừng thì kết nối tới OpenAI không được đóng chủ động. Sửa: `async with stream:` quanh vòng
  `async for` (SDK có `__aenter__/__aexit__`, `_streaming.py:234-237`).
- Chưa kiểm: OpenAI có ngừng tính token ngay khi kết nối đóng không (xem usage dashboard nếu cần).
- Quan trọng: không dừng = vẫn trả tiền token không ai đọc + giữ kết nối/tài nguyên server.
- `except CancelledError` phải `raise` lại (không nuốt tín hiệu dừng); `finally` luôn chạy → chỗ dọn dẹp.
  Biến dùng trong `finally` (`count`) phải gán **trước** `try` (pyright: possibly unbound).

Lỗi gặp: câu dài không có `done` (stream im lặng kết thúc) _(Claude ghi, 2026-10-11)_

- "Viết bài 500 chữ về lịch sử Hà Nội" + `max_output_tokens=300`: qua server có lần **0 event**, có lần
  nhiều delta rồi dừng, không bao giờ có `done`.
- Gọi thẳng SDK đếm event: kết thúc bằng `response.incomplete`
  (`incomplete_details.reason='max_output_tokens'`), **không** có `response.completed`.
  `usage`: output 300, trong đó `reasoning_tokens=179`.
- `gpt-6-luna` là model reasoning: token "nghĩ" tính vào `max_output_tokens` → số token còn cho chữ
  thay đổi mỗi lần (116 delta / 0 delta).
- Sửa: xử lý cả `response.completed` và `response.incomplete` (đều có `.response.usage`), thêm
  `"incomplete": true/false` vào `done`; tăng `max_output_tokens` nếu cần câu dài. Bài học Buổi 4 lặp lại:
  liệt kê **mọi** event kết thúc của SDK, không chỉ đường đi đẹp.

## Bài 4 — Next.js đọc stream

| Thử                                         | Quan sát |
| ------------------------------------------- | -------- |
| Chữ hiện dần trên trang                     | Có (tự thử trên UI): chữ chảy dần, cuối hiện Tokens/Cost. Đo lại bằng Node `fetch` cùng logic, câu "Giải thích transformer trong 5 câu": chunk đầu 1.8s, xong 3.5s, 120 event |
| DevTools → Network → `/chat/stream`         | Chrome tự nhận `text/event-stream` → có tab **EventStream** dù dùng `fetch` (không phải `EventSource`). Cột **Type** = giá trị dòng `event:` (`delta`), **Data** = JSON `{"content": …}`, cột **Id** trống vì server không gửi `id:`. Delta cắt giữa chữ: `" ng"` + `"ôn"` + `" ng"` + `"ữ"` (giống Bài 2). Cả stream 2.3 kB. Danh sách chỉ có 1 request `stream`, không thấy `OPTIONS` (giả thuyết: preflight đã được cache nhờ `max-age: 600`, chưa kiểm) |
| Preflight `OPTIONS` có xuất hiện không       | Có: header `x-api-key` + `Content-Type: application/json` không "simple" → trình duyệt gửi `OPTIONS` trước. Giả lập bằng curl: `200`, `access-control-allow-origin: http://localhost:3000`, `allow-headers` có `x-api-key`, `max-age: 600` (cache preflight 10 phút → các lần Gửi sau có thể không thấy `OPTIONS`) |
| Lỗi Bài 1a (1 `\n`) với client này          | Mô phỏng logic `page.tsx` (chưa sửa backend thật): `split("\n\n")` không tách được → `handleEvent` gọi **0 lần**, buffer phình dần tới hết stream rồi bị bỏ → trang trắng, không có Tokens/Cost, không báo lỗi |
| Nút Dừng (AbortController) → log server     | Có, giống Bài 3B: `[stream cancelled] sau 17 delta` rồi `[stream closed] đã gửi 17 delta`. Mô phỏng bằng Node `fetch` cùng logic `page.tsx`, gọi server riêng `:8001`, abort sau delta thứ 10 (xem ghi chú dưới) |

Nút Dừng — đo bằng Node `fetch` (v24) + `AbortController`, câu "Giải thích transformer trong 5 câu": _(Claude ghi, 2026-10-16)_

- Server **dừng thật**: abort → kết nối đóng → Starlette cancel generator → `CancelledError` → log `cancelled` + `closed`
  (cùng đường đi với Ctrl+C curl ở Bài 3B). Vòng `async for` qua stream OpenAI dừng theo.
- Client nhận 10 delta, server log đã gửi **17**: 7 delta đã ghi ra socket trước khi server biết client đi
  (còn nằm trên đường mạng / buffer) → client không bao giờ đọc. Server phát hiện ngắt **trễ** hơn lúc bấm Dừng một chút.
- Lỗi ném ra ở `reader.read()`, **không** ở `fetch`: `name=AbortError`, `message="This operation was aborted"` (thông
  điệp của Node; Chrome viết khác, chưa kiểm) → so `name`, không so `message`.
- Abort 50ms sau khi gửi: header 200 đã về sau 27ms (`StreamingResponse` gửi header trước khi gọi OpenAI) → vẫn lỗi ở
  `reader.read()`, server log `cancelled sau 0 delta`. Với backend này gần như không có lúc nào abort rơi vào `fetch`.
- Chữ đã nhận được giữ lại (`"Transformer là kiến trúc mạng nơ-ron"`) vì `catch` không `setAnswer("")`.
- Dùng lại controller đã abort cho fetch sau → bị huỷ **ngay**, request không tới server (log không có dòng nào)
  → mỗi lần Gửi phải `new AbortController()`.
- Chưa kiểm trên trình duyệt thật: DevTools Network hiện trạng thái gì (`(canceled)`?), message lỗi của Chrome.

Vì sao không dùng `EventSource`: _(Claude ghi)_

- Constructor `new EventSource(url, options)` chỉ có 1 option là `withCredentials` (MDN "EventSource() constructor")
  → luôn là **GET**, không gửi body, không đặt header tuỳ ý.
- Bài này cần `POST` + body JSON (`message`) + header `X-API-Key` → `EventSource` không làm được, phải dùng
  `fetch` + `res.body.getReader()` và tự parse SSE.
- Đổi lại mất các thứ `EventSource` làm sẵn: tự tách event, tự kết nối lại (`retry:`), `Last-Event-ID`.

Vì sao phải tự tách event bằng buffer (so với `res.json()`): _(Claude ghi)_

- `res.json()` đợi **hết** body rồi parse 1 lần → mất hiệu ứng chảy chữ. Stream thì đọc từng `read()`.
- 1 lần `read()` là 1 mảnh byte mạng, **không** khớp ranh giới event. Đo thật (Node `fetch`): 113 chunk / 120 event,
  có 1 chunk chứa **8 event dính nhau**. Lần đo này không gặp chunk cắt giữa event, nhưng TCP/proxy không
  đảm bảo → vẫn phải xử lý.
- Cách làm: `buffer += chunk` → `split("\n\n")` → `parts.pop()` giữ lại phần cuối (có thể là nửa event)
  → `handleEvent` từng phần đủ. Đã kiểm 3 kiểu chunk (1 event / nhiều event dính / cắt giữa JSON) đều ra đúng.
- `decoder.decode(value, { stream: true })`: chữ tiếng Việt UTF-8 nhiều byte có thể bị cắt giữa 2 chunk,
  `stream: true` giữ byte dở chờ chunk sau (giống lý do cần buffer, nhưng ở tầng byte).

## Bài 5 — Test + SSE vs WebSocket

Test (`uv run pytest weeks/week02/session09`): **4 passed** _(Claude viết + ghi, 2026-10-16)_

- `test_health`: khung test chạy được, `from exercises import app` import đúng file session09.
- `test_stream_fake`: `content-type` là `text/event-stream; charset=utf-8` (Starlette tự thêm charset → so
  `startswith`, không `==`). Body split `"\n\n"` ra 5 phần, cuối là `""`. Token `"chào\nbạn"` nằm trong body dạng
  `\\n` (2 ký tự) nhờ `json.dumps` → event không vỡ.
- `test_chat_stream_missing_api_key`: **401 JSON thường**, không phải stream → `Depends(verify_api_key)` chạy
  **trước** khi tạo `StreamingResponse`. Muốn trả đúng mã lỗi (auth, validate) thì kiểm tra trước stream.
- `test_chat_stream_with_fake_openai`: `app.dependency_overrides[get_openai_client]` thay client thật bằng client giả
  (`create` async + `async with` + `async for`) → không tốn token, kết quả cố định. Kiểm: endpoint gọi đúng
  `input` / `model` / `stream=True`, event lạ bị bỏ qua, thứ tự `delta, delta, done`, cost dùng `pytest.approx`.
  Nhớ `dependency_overrides.clear()` trong `finally`.
- Chưa test: lỗi giữa stream (client giả ném `openai.APIError` → phải có `event: error`).

So sánh 3 cách server đẩy dữ liệu xuống trình duyệt: _(Claude ghi, 2026-10-16 — nguồn ở dưới bảng)_

| Tiêu chí                     | SSE | WebSocket | Long polling |
| ---------------------------- | --- | --------- | ------------ |
| Chiều dữ liệu                | Một chiều server → client. Client muốn gửi thì mở request mới | Hai chiều trên cùng 1 kết nối, gửi lúc nào cũng được | Server → client, trả 1 lần rồi đóng; client gửi lên bằng request mới |
| Giao thức                    | HTTP thường (200 + `text/event-stream`, response không đóng) | Bắt đầu bằng HTTP (`Upgrade: websocket`) → server trả `101 Switching Protocols` → từ đó là giao thức WebSocket, không còn HTTP. URL `ws://` / `wss://` | HTTP thường, mỗi lượt 1 request/response |
| Tự kết nối lại               | Có nếu dùng `EventSource` (field `retry:`, gửi lại `Last-Event-ID`). Dùng `fetch` như bài này → **mất**, phải tự viết | Không có sẵn → tự viết | Vốn là vòng lặp client tự gửi lại → lỗi thì tự retry |
| Gửi header (auth) khi mở     | `EventSource`: **không** (chỉ có `withCredentials`). `fetch`: được → lý do bài này dùng `fetch` | **Không**: `new WebSocket(url, protocols)` không có chỗ cho header → thường gửi token qua query / cookie / message đầu | Được (là `fetch` thường) |
| Qua proxy / CDN / load balancer | Là HTTP nên đi qua được, **nhưng** proxy có thể buffer làm mất chảy chữ (nginx `proxy_buffering` mặc định `on` → tắt bằng header `X-Accel-Buffering: no`) | Proxy phải hỗ trợ Upgrade: nginx cần tự chuyển header `Upgrade` / `Connection` (hop-by-hop, không tự đi qua) | Đi qua dễ nhất, chỉ lo request bị giữ lâu chạm timeout |
| Độ phức tạp server           | Thấp: 1 generator + `StreamingResponse` (Bài 1 ~15 dòng) | Cao hơn: giữ trạng thái từng kết nối, nhận + gửi 2 chiều, ping để giữ kết nối, scale nhiều server khó hơn _(suy luận)_ | Trung bình: giữ request chờ dữ liệu, không mất tin giữa 2 lần client hỏi lại _(suy luận)_ |
| Hợp với                      | Server đẩy liên tục, client ít gửi: stream token LLM, thông báo, feed | Hai bên gửi liên tục, độ trễ thấp: chat nhiều người, game, sửa tài liệu chung | Cập nhật thưa / môi trường không dùng được 2 cách kia (phương án dự phòng) |

Ghi thêm:

- SSE qua HTTP/1.1 bị giới hạn **6 kết nối / trình duyệt + domain**, tính chung mọi tab (MDN) → mở nhiều tab chat
  dễ chạm trần. HTTP/2 không bị giới hạn kiểu này.
- Timeout proxy: nginx mặc định đóng kết nối proxy im lặng quá **60s** (`proxy_read_timeout`, docs WebSocket
  proxying). Áp dụng cho cả SSE: model nghĩ lâu không gửi gì có thể bị cắt _(suy luận, chưa thử)_.
- Nguồn: MDN "Using server-sent events" (retry, Last-Event-ID, giới hạn 6, "one-way connection"); MDN
  "WebSocket() constructor" (chỉ có `url`, `protocols`); MDN "Protocol upgrade mechanism" (`Upgrade`, `101`);
  nginx `ngx_http_proxy_module` (`proxy_buffering`, `X-Accel-Buffering`); nginx "WebSocket proxying".

Key ở frontend (`NEXT_PUBLIC_`) lộ thế nào, cách đúng cho Project #1: _(Claude ghi, 2026-10-16)_

- Docs Next.js 16.4 (`node_modules/next/dist/docs/01-app/02-guides/environment-variables.md`): biến
  `NEXT_PUBLIC_` được **inline lúc build** vào JS gửi xuống trình duyệt (thay `process.env.X` bằng giá trị cứng).
  → Ai mở trang cũng đọc được key: tab Sources (trong file JS) hoặc Network → request `/chat/stream` → header
  `X-API-Key`. Chưa tự kiểm trên bundle (lúc ghi, server `:3000` đã tắt).
- Biến **không** có `NEXT_PUBLIC_` chỉ có ở server ("By default, environment variables are only available on the server").
- Cách đúng: Route Handler `app/api/chat/route.ts` (chạy ở server Next.js, docs `15-route-handlers.md`)
  gọi FastAPI kèm key, rồi trả `new Response(stream)` chuyển tiếp stream về trình duyệt (docs `route.md` mục
  Streaming). Đường đi:
  `Trình duyệt → /api/chat (Next server, giữ APP_API_KEY) → FastAPI (giữ OPENAI_API_KEY) → OpenAI`.
  Trình duyệt chỉ gọi cùng domain, **không** thấy key nào; hết luôn preflight CORS (cùng origin).
  Buổi 10–11 làm thật.

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

_(Claude viết nháp, 2026-10-16, gom từ Bài 1–5 — đọc lại và viết bằng lời mình trước khi đi phỏng vấn)_

### 1. Vì sao chat LLM dùng SSE thay vì WebSocket? (exit criteria Phase 01)

- Chat LLM chủ yếu là **server đẩy một chiều**: client gửi 1 câu hỏi, server trả nhiều token. SSE đúng hình dạng đó;
  câu hỏi tiếp theo chỉ cần 1 request mới, không cần kênh 2 chiều.
- SSE là **HTTP thường**: dùng lại auth bằng header, CORS, log, load balancer, `fetch` sẵn có. Server chỉ là 1
  generator + `StreamingResponse`. WebSocket phải nâng cấp giao thức (`101`), giữ trạng thái kết nối, proxy phải
  hỗ trợ Upgrade, và trình duyệt không gắn header auth được.
- Đánh đổi: proxy có thể buffer SSE (tắt bằng `X-Accel-Buffering: no`), giới hạn 6 kết nối trên HTTP/1.1.
  Chỉ cần WebSocket khi hai bên gửi liên tục (voice realtime, nhiều người cùng chat).

### 2. Tool call / OpenAI fail giữa stream thì xử lý sao? (exit criteria Phase 01)

- `StreamingResponse` gửi **200 + header trước** khi chạy generator → lỗi giữa stream không đổi sang 502 được nữa.
  Không bắt thì kết nối bị cắt, client chỉ thấy câu cụt (curl `(18)`).
- Cách xử lý: `try/except` **trong generator** → log chi tiết ra server (`type(e).__name__`, model) → gửi
  `event: error` với câu gọn (không lộ `str(e)`) → kết thúc stream sạch. Client bắt event `error` để hiện lỗi,
  giữ phần chữ đã nhận.
- Lỗi kiểm được **trước** stream (auth, validate body, có thể cả `responses.create`) thì đặt trước
  `StreamingResponse` → vẫn trả 401 / 422 / 502 đúng nghĩa (test 401 ở Bài 5).
- Client ngắt (nút Dừng / Ctrl+C) → generator nhận `CancelledError` → log rồi `raise` lại, `finally` dọn dẹp,
  `async with stream` đóng kết nối tới OpenAI → không tốn token cho câu trả lời không ai đọc.
- Tool call lỗi: chưa làm thật (Buổi 10–11). Hướng dự kiến: cùng khung trên, lỗi tool cũng thành `event: error`
  hoặc trả lỗi về cho model như kết quả tool _(chưa kiểm)_.

### 3. Stream từ LLM tới trình duyệt đi qua những bước nào, chỗ nào có thể bị buffer làm mất hiệu ứng "chảy chữ"?

Đường đi: OpenAI → SDK `AsyncOpenAI` (`async for event`) → generator `chat_events` (`yield` SSE) →
Starlette `StreamingResponse` → (proxy / CDN nếu có) → TCP → `fetch` `reader.read()` → `TextDecoder` →
buffer `split("\n\n")` → `handleEvent` → React state.

| Chỗ có thể buffer                 | Đã gặp thật?                                        |
| --------------------------------- | --------------------------------------------------- |
| `print` thiếu `flush=True`        | Có — Buổi 4 (in ra terminal, không qua web): chữ đợi `"\n"` mới hiện |
| Client đợi hết body               | Có — curl không `-N` thấy cả cục ở cuối; `res.json()` cũng vậy |
| Proxy (nginx `proxy_buffering on`)| Chưa — giả thuyết, sửa bằng `X-Accel-Buffering: no` |
| Code sync chặn event loop         | Generator `def` + `time.sleep` (Bài 1c) **không** chặn: Starlette chạy nó trong threadpool. Nhưng code sync **trong** `async def` thì chặn (Buổi 8) → mọi stream khác cùng đứng |
| TCP gộp nhiều event 1 chunk       | Có — Bài 4: 1 chunk chứa 8 event. **Không** mất chảy chữ, chỉ cần buffer đúng ở client |
