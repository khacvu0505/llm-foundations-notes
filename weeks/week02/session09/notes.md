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
| Chữ hiện dần trên trang                     |          |
| DevTools → Network → `/chat/stream`         |          |
| Preflight `OPTIONS` có xuất hiện không       |          |
| Lỗi Bài 1a (1 `\n`) với client này          |          |
| Nút Dừng (AbortController) → log server     |          |

Vì sao không dùng `EventSource`:

-

Vì sao phải tự tách event bằng buffer (so với `res.json()`):

-

## Bài 5 — Test + SSE vs WebSocket

Test (`uv run pytest weeks/week02/session09`):

-

| Tiêu chí                     | SSE | WebSocket | Long polling |
| ---------------------------- | --- | --------- | ------------ |
| Chiều dữ liệu                |     |           |              |
| Giao thức                    |     |           |              |
| Tự kết nối lại               |     |           |              |
| Gửi header (auth) khi mở     |     |           |              |
| Qua proxy / CDN / load balancer |  |           |              |
| Độ phức tạp server           |     |           |              |
| Hợp với                      |     |           |              |

Key ở frontend (`NEXT_PUBLIC_`) lộ thế nào, cách đúng cho Project #1:

-

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

### 1. Vì sao chat LLM dùng SSE thay vì WebSocket? (exit criteria Phase 01)

### 2. Tool call / OpenAI fail giữa stream thì xử lý sao? (exit criteria Phase 01)

### 3. Stream từ LLM tới trình duyệt đi qua những bước nào, chỗ nào có thể bị buffer làm mất hiệu ứng "chảy chữ"?
