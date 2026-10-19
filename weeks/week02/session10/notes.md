# Buổi 10 — Project #1 (p1): Smart Copilot Widget — Backend (2h)

| Phần                                       | Thời lượng | Làm ở đâu                                |
| ------------------------------------------ | ---------- | ---------------------------------------- |
| Setup: tạo project, cài gói, chép code     | ~15ph      | mục Setup                                |
| Bài 1: tách file, chạy lại như cuối Buổi 9 | ~15ph      | `projects/p1-smart-copilot/backend/app/` |
| Bài 2: tool loop bên trong stream          | ~40ph      | `app/main.py`, `app/tools.py`            |
| Bài 3: cost log (terminal + JSONL)         | ~20ph      | `app/`                                   |
| Bài 4: rate limit 429 + retry OpenAI       | ~15ph      | `app/`                                   |
| Bài 5: test                                | ~15ph      | `backend/tests/`                         |

Đề bài chi tiết: `exercises.md` cùng thư mục. Bài 2 là cốt lõi; không kịp thì để Bài 5 sang đầu Buổi 11.

Checklist Notion Buổi 10–11 (Buổi 10 làm phần backend):

- Backend FastAPI: endpoint chat, tools (2–3 cái), SSE streaming, cost logging → Bài 1, 2, 3
- Chống spam tối thiểu: giới hạn input, `max_output_tokens`, rate limit IP → 429, retry OpenAI → Bài 4
- (Buổi 11) Frontend widget, streaming UI mượt, Generative UI

## Setup (tự làm)

Chạy từ thư mục gốc repo (`llm-foundations-notes/`).

- [x] **Tạo project backend độc lập** (có `pyproject.toml` riêng để Buổi 12 deploy):
      `    mkdir -p projects/p1-smart-copilot
uv init --app --no-workspace projects/p1-smart-copilot/backend`
      `--no-workspace`: không gắn vào `pyproject.toml` gốc của repo (kiểm: `uv init --help`).
      Xoá file mẫu `main.py` mà `uv init` tạo nếu không dùng.
- [x] **Cài gói** (chạy trong `backend/`):
      `    cd projects/p1-smart-copilot/backend
uv add "fastapi[standard]" openai httpx2 pandas pydantic python-dotenv
uv add --dev ruff pyright pytest`
- [x] **Chép config ruff + pyright** từ `pyproject.toml` gốc (mục `[tool.ruff]`, `[tool.ruff.lint]`,
      `[tool.pyright]`) sang `backend/pyproject.toml`. Kiểm: `uv run ruff check .` và `uv run pyright` chạy được.
- [x] **`.env` riêng cho backend**: tạo `backend/.env` với `OPENAI_API_KEY`, `APP_API_KEY` (chép từ `.env` gốc).
      Tạo thêm `backend/.env.example` (chỉ tên biến, không giá trị) để commit — Buổi 12 deploy cần biết biến nào.
      Kiểm `.gitignore` có bỏ `.env` (gốc repo đã có? mở ra xem) và thêm `logs/`.
- [x] **Dữ liệu**: chép `weeks/week02/session07/orders.csv` → `backend/data/orders.csv`.
      (Tuỳ chọn, cho chart đẹp hơn) mở rộng lên ~40–60 đơn trải 14 ngày, thêm cột `city`
      (Hà Nội / Đà Nẵng / TP.HCM) để nối với `get_weather`. Sinh dữ liệu giả có thể nhờ Claude, không phải phần học.
- [x] **Tạo cấu trúc** (gợi ý, tự quyết):
      `    backend/
app/          main.py, sse.py, tools.py, auth.py, llm.py
tests/        test_*.py
data/         orders.csv
logs/         cost.jsonl (không commit)`
- [x] **Chạy**: `uv run fastapi dev app/main.py` (trong `backend/`) → `curl http://127.0.0.1:8000/health`.
- [ ] Đọc nhanh: OpenAI docs "Function calling" mục streaming; `openai` SDK README mục "Retries";
      FastAPI "Dependencies" (lại) cho `rate_limit`.

## Nợ từ Buổi 9 (làm lúc rảnh, không chặn Buổi 10)

- [ ] `session09/notes.md`: Bài 1b, dòng so sánh `/chat` ở Bài 2, dòng "bắt → event: error" ở Bài 3, dán log
- [ ] Bấm Dừng trên trình duyệt thật: DevTools Network hiện gì, message lỗi của Chrome
- [ ] 3 câu phỏng vấn cuối `session09/notes.md`: viết lại bằng lời mình (đang là bản nháp Claude)
- [x] Dọn `session09/web/app/page.tsx`: `console.log(JSON.stringify(chunk))`, dòng trống thừa
- [x] Test lỗi giữa stream → đã đưa vào Bài 5 buổi này (`test_openai_error_mid_stream`)
- [ ] Notion: tick Buổi 9 + dòng Status; nhật ký Tuần 2; nợ Buổi 7, 8 (xem `session09/notes.md`)

## Bài 1 — Tách file

Import / chạy thế nào (`fastapi dev`, `pytest`, `pyright` cùng chạy được):

_(Claude viết, 2026-10-18, theo yêu cầu. Nguồn: lỗi gặp thật lúc làm Bài 1; đọc `fastapi_cli/discover.py` trong
`backend/.venv`; thử lại `pytest -o pythonpath=` và `get_module_data_from_path` trên thư mục tạm có / không có
`__init__.py`.)_

- _(Claude viết)_ Cấu trúc: `backend/app/{main,sse,auth,llm,tools,cost_log,rate_limit}.py` + `app/__init__.py` (rỗng),
  `backend/tests/`. Mọi import viết **tuyệt đối từ gốc `backend/`**: `from app.sse import format_sse`,
  `from app.main import app`. Muốn chạy được thì thư mục **chứa** `app/` (= `backend/`) phải nằm trong `sys.path`.
  Mỗi tool tự quyết `sys.path` khác nhau:

  | Tool                                       | Đưa gì vào `sys.path`                                                                                              | Tìm thấy `app`?                                |
  | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
  | `fastapi dev app/main.py`                  | đi ngược lên từ `main.py`, gặp thư mục có `__init__.py` thì coi là package → thêm **cha của package** (`backend/`) | ✓ (module `app.main`)                          |
  | `pyright`                                  | resolve import từ gốc project (chỗ có `pyproject.toml` = `backend/`)                                               | ✓                                              |
  | `pytest` (mặc định, import mode `prepend`) | thư mục của **file test** (`tests/`), không phải `backend/`                                                        | ✗ `ModuleNotFoundError: No module named 'app'` |

  Buổi 9 không gặp vì test và code nằm **cùng 1 thư mục**.

- _(Claude viết)_ Cách sửa: `backend/pyproject.toml` thêm `[tool.pytest.ini_options]` `pythonpath = ["."]` (`.` tính
  từ `rootdir` = `backend/`) → pytest tự thêm `backend/` vào `sys.path`. Thử bỏ cấu hình đó (`pytest -o pythonpath=`)
  là lỗi lại ngay. Tốt hơn `uv run python -m pytest` (cũng chạy được vì `-m` thêm cwd vào `sys.path`) vì không phụ
  thuộc lệnh gõ và thư mục đang đứng — CI / người khác chạy `pytest` trơn vẫn đúng.
- _(Claude viết)_ Có cần `__init__.py` không: **cần cho `app/`, vì `fastapi dev`**. Thử `get_module_data_from_path`:
  có `app/__init__.py` → module `app.main`, thêm `backend/` vào `sys.path`; **không có** → module `main`, thêm `app/`
  vào `sys.path` → `from app.sse import ...` trong `main.py` sẽ hỏng. Với `pytest` thì `__init__.py` **không** sửa
  được lỗi trên (thiếu `backend/` trong `sys.path`) — phải dùng `pythonpath`. `tests/` không cần `__init__.py`.
- _(Claude viết)_ `load_dotenv()` đặt ở **đầu `app/llm.py`**, trước `client = AsyncOpenAI(...)`: `AsyncOpenAI()` đọc
  `OPENAI_API_KEY` **lúc import** (tạo client ở cấp module), nên `.env` phải được nạp trước dòng đó. Còn
  `verify_api_key` đọc `APP_API_KEY` **lúc có request** → chỉ cần `.env` đã nạp trước request đầu (đã đúng vì
  `main.py` import `app.llm`). `load_dotenv()` không tham số tìm `.env` bắt đầu từ thư mục của file gọi nó
  (`app/`) rồi đi lên → thấy `backend/.env`; nhưng trong REPL / `python -c` / debugger thì tìm từ **cwd** (đọc
  `find_dotenv`) → muốn chắc thì truyền đường dẫn tuyệt đối dựng từ `__file__`.
- Bản của mình:

## Bài 2 — Tool loop bên trong stream

_(Claude viết, 2026-10-17, theo yêu cầu. Nguồn số liệu: chạy thật `fastapi run` local + script httpx stream
đo từng câu 1 lần, ~20:30; TTFT = từ lúc gửi request đến `delta` đầu tiên; model `gpt-6-luna`.)_

| Câu hỏi                                                            | Tool được gọi                                                | Số bước | TTFT (chữ đầu) | Tổng  | Ghi chú                                                                                                                                         |
| ------------------------------------------------------------------ | ------------------------------------------------------------ | ------- | -------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| "Đơn nào của An đang giao?"                                        | `query_orders(customer="An", status="shipping")`             | 2       | 2.76s          | 3.03s | Trả lời đúng "không có đơn nào của An đang giao" (4 đơn của An đều `delivered`). 993 in / 37 out token                                          |
| "Tuần này món nào bán chạy nhất?"                                  | `sales_summary(group_by="product", status=null)`             | 2       | 3.43s          | 4.21s | Trà đào cam sả 900.000đ / 9 đơn (đã trừ cancelled). Model tự nói "dữ liệu không ghi rõ phạm vi tuần" → tool chưa lọc theo khoảng ngày           |
| "Mai Đà Nẵng mưa không, có nên giao đơn không?"                    | `get_weather(city="Đà Nẵng")`                                | 2       | 5.92s          | 6.41s | Tool chỉ có thời tiết **hiện tại** (mưa phùn nhẹ, 27.4°C); model nói rõ "không có dự báo cho ngày mai", không bịa                               |
| "So sánh doanh thu theo ngày với thời tiết Hà Nội hôm nay" (lần 1) | `sales_summary(day)` → bước sau `get_weather(Hà Nội)`        | 3       | 6.88s          | 7.46s | Gọi **tuần tự** 2 bước. Open-Meteo trả **503** → `tool_result ok:false` → model báo "chưa lấy được thời tiết", stream không chết. 2335 in token |
| Cùng câu đó (lần 2)                                                | `sales_summary(day)` + `get_weather(Hà Nội)` **cùng 1 bước** | 2       | 5.36s          | 7.51s | Lần này gọi **song song**. Cùng câu hỏi, model chọn cách gọi khác nhau giữa 2 lần chạy. 1471 in token                                           |
| Câu không cần tool ("Xin chào")                                    | —                                                            | 1       | 0.80s          | 1.13s | 461 in / 16 out token. ~440 token input là 3 tool schema (so với 25 token lúc chưa có tools ở Bài 1)                                            |

Nhận xét chung: có tool thì TTFT tăng từ ~0.8s lên ~2.8–6.9s vì chữ đầu tiên chỉ ra ở **bước cuối**: phải chờ
1 lượt OpenAI (model quyết định gọi tool) + chạy tool (`get_weather` gọi mạng, chậm hơn đọc CSV) + lượt OpenAI thứ 2
bắt đầu sinh chữ. Mỗi bước thêm ~1 lần gửi lại toàn bộ input → input token cộng dồn (993 ≈ 466 + 527).

Bản của mình:

Lấy function call từ stream bằng event nào, vì sao:

- _(Claude viết)_ Chọn `response.output_item.done` với `event.item.type == "function_call"` (cách A). `event.item` đã là
  `ResponseFunctionToolCall` đầy đủ (`call_id`, `name`, `arguments` hoàn chỉnh) → đưa thẳng vào `execute_call`, không
  phải ghép từ các `function_call_arguments.delta`. Bắt được từng call ngay khi xong, sau này có thể gửi `tool_call`
  cho UI sớm hơn (không đợi hết bước). Vẫn phải giữ `event.response.output` ở `response.completed` để nối vào
  `input_list` cho bước sau. Cách B (đọc `response.output` ở `completed`) đơn giản hơn, giống Buổi 7, nhưng chỉ thấy
  call ở cuối bước.
- Bản của mình:

Tool sync trong async generator — đã xử lý thế nào (`get_weather`, `query_orders`):

- _(Claude viết)_ `get_weather` gọi mạng → đổi sang `httpx2.AsyncClient` + `await` (bản `get_weather_parallel` Buổi 7),
  không chặn event loop trong lúc chờ Open-Meteo. `query_orders` / `sales_summary` vẫn sync (pandas đọc CSV 50 dòng):
  đo ~0.6ms / ~1.8ms mỗi lần → chặn event loop không đáng kể, chấp nhận. `execute_call` gọi `func(**args)` rồi
  `isawaitable(result)` thì `await` → 1 hàm xử lý cả tool sync lẫn async. Nếu file lớn / truy vấn DB chậm thì chuyển
  sang `await asyncio.to_thread(...)` hoặc driver async.
- Bản của mình:

Tool lỗi vs OpenAI lỗi giữa stream — gửi event gì, vì sao khác nhau:

- _(Claude viết)_ **Tool lỗi** (tool lạ, JSON hỏng, tool ném exception — vd Open-Meteo 503 ở bảng trên) → `execute_call`
  trả `{"ok": false, "error": ...}` → gửi `tool_result ok:false` **và** đưa kết quả đó cho model; stream chạy tiếp,
  model tự xử lý (báo người dùng, thử tool khác). Đây là lỗi "trong cuộc hội thoại", model sửa được.
  **OpenAI lỗi** (`openai.APIError`: mất kết nối, 5xx, rate limit) → không còn model để xử lý tiếp → gửi
  `event: error` 1 lần rồi dừng (try bọc ngoài `for`, nên không chạy tiếp bước sau). Hết `MAX_STEPS` cũng gửi `error`.
  Chi tiết lỗi (exception, URL) chỉ ghi log server, không gửi cho client / model.
- Bản của mình:

UI nên hiện gì trong lúc chờ tool (ghi cho Buổi 11):

- _(Claude viết)_ Nhận `tool_call` → hiện trạng thái theo tên tool ("Đang tra đơn hàng…", "Đang xem thời tiết Đà Nẵng…",
  "Đang tổng hợp doanh thu…"), map bằng `call_id`. Nhận `tool_result` cùng `call_id` → đổi thành ✓ (hoặc ⚠ nếu
  `ok:false`). `sales_summary` trả list `{label, revenue_vnd, order_count}` → có thể vẽ chart ngay (Generative UI) trước
  khi model viết xong chữ. TTFT có tool là 3–7s nên **bắt buộc** phải có trạng thái, nếu không người dùng tưởng treo.
- Bản của mình:

## Bài 3 — Cost log

_(Claude viết, 2026-10-18, theo yêu cầu. Nguồn: `backend/logs/cost.jsonl` sau khi chạy thật `fastapi run` local,
5 câu + 1 lần cancel (script httpx tự đóng kết nối sau 3 delta); model `gpt-6-luna`.)_

| Câu hỏi                                                                           | steps | tools                      | input | output | cost_usd  | latency_ms | status    |
| --------------------------------------------------------------------------------- | ----- | -------------------------- | ----- | ------ | --------- | ---------- | --------- |
| "Xin chào"                                                                        | 1     | —                          | 461   | 17     | 0.0000546 | 1970       | ok        |
| "Đơn nào của An đang giao?"                                                       | 2     | query_orders               | 993   | 37     | 0.0001178 | 2834       | ok        |
| "Tuần này món nào bán chạy nhất?"                                                 | 2     | sales_summary              | 1146  | 298    | 0.0002636 | 4519       | ok        |
| "Mai Đà Nẵng mưa không?"                                                          | 2     | get_weather                | 1022  | 114    | 0.0001592 | 4945       | ok        |
| "So sánh doanh thu theo ngày với thời tiết Hà Nội hôm nay"                        | 3     | sales_summary, get_weather | 2368  | 201    | 0.0003373 | 6664       | ok        |
| "Tuần này món nào bán chạy nhất? Giải thích chi tiết từng món" (ngắt sau 3 delta) | 2     | sales_summary              | 474   | 23     | 0.0000589 | 2938       | cancelled |

Câu đắt nhất, vì sao; tool schema chiếm bao nhiêu input:

- _(Claude viết)_ Đắt nhất: câu cần 2 tool ($0.000337, ~6x "Xin chào"). Lý do: 3 bước = 3 lời gọi OpenAI, mỗi bước
  gửi lại **toàn bộ** input (câu hỏi + tool schema + các function_call + kết quả tool của bước trước) → input cộng dồn
  2368 token. Kết quả `sales_summary(day)` (14 dòng) cũng làm input bước sau to lên. Output ít ảnh hưởng hơn: câu
  "món bán chạy" có output 298 token nhưng vẫn rẻ hơn câu 2 tool.
- _(Claude viết)_ Tool schema: "Xin chào" có tools = 461 input token, Bài 1 (chưa có tools, instructions ngắn hơn) = 25
  → 3 tool schema + phần instructions thêm ≈ **~435 token mỗi lời gọi**, và bị tính lại ở **mọi bước**. Buổi 7 đo
  ~167 token cho 2 tool; giờ 3 tool với description tiếng Việt dài (mô tả city, cancelled, sắp xếp) nên gấp ~2.6 lần.
  Muốn giảm: description ngắn hơn, chỉ gửi tool cần thiết. Số ~435 là ước lượng từ hiệu 2 lần chạy, chưa đo riêng
  từng schema.
- Bản của mình:

Bị cancel giữa stream thì usage lấy ở đâu, log thế nào:

- _(Claude viết)_ `usage` chỉ có trong event `response.completed` / `response.incomplete` ở **cuối** mỗi bước. Bước bị
  ngắt giữa chừng không bao giờ tới event đó → code hiện tại chỉ cộng usage của các bước **đã xong**. Dòng cancel ở
  bảng trên: `in=474 out=23` = đúng usage bước 1 (gọi tool); bước 2 đã gửi ~500+ input token và sinh vài delta
  nhưng **không được tính**, dù OpenAI vẫn có thể tính tiền phần đó → log đang **thiếu**, không phải 0 nhưng sai.
- _(Claude viết)_ Cách log đúng hơn (chưa làm): (1) bước bị ngắt → ước lượng output bằng số delta đã gửi (`count`,
  cận dưới) hoặc `tiktoken` trên phần text đã stream, input ≈ token của `input_list` lúc gọi bước đó; (2) thêm cờ
  `"usage_estimated": true` để biết số nào là đo, số nào là ước lượng; (3) giả thuyết chưa kiểm chứng: dùng
  `response.id` (event `response.created`) gọi lại API lấy usage sau khi cancel — cần thử xem response bị ngắt có
  usage không.
- Bản của mình:

## Bài 4 — Chống spam

_(Claude viết, 2026-10-18, theo yêu cầu. Nguồn: chạy thật `fastapi run` local + curl; đọc code SDK `openai` trong
`backend/.venv` (`openai/_constants.py`, `openai/_base_client.py`).)_

Cấu hình: `rate_limit` 5 request / 60s / IP (sliding window, `app/rate_limit.py`), thứ tự
`dependencies=[Depends(verify_api_key), Depends(rate_limit)]`; `AsyncOpenAI(max_retries=2, timeout=30)`.

| Thử                              | Quan sát                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7 request liên tiếp (curl)       | `1-5 → 200`, `6-7 → 429` đúng như đề. Request sai key gửi lúc đang bị chặn → `401` (không phải 429): `verify_api_key` chạy trước nên request sai key không bị trừ lượt. `/health` vẫn `200` (không gắn rate limit). Request bị 429 không vào `chat_events` → không có dòng trong `cost.jsonl`                                                                                                                                                                                                               |
| Header `Retry-After` của 429     | `HTTP/1.1 429 Too Many Requests`, `retry-after: 60`, body `{"detail":"Rate limit exceeded"}`. Đang trả **cố định** `WINDOW_S` = 60; chính xác hơn là `ceil(60 - (now - mốc cũ nhất))` để client không chờ thừa                                                                                                                                                                                                                                                                                              |
| SDK retry những lỗi nào, mấy lần | `max_retries` mặc định **2** (`_constants.py`: `DEFAULT_MAX_RETRIES = 2`) → tối đa 3 lần gọi. Retry khi status **408, 409, 429, ≥500**, hoặc server gửi `x-should-retry: true` (`_should_retry`); cũng retry **timeout** và **lỗi kết nối** (`_base_client.py`, nhánh `timeout_exceptions` / `request_exceptions`). Chờ: tôn trọng header `retry-after` / `retry-after-ms` của OpenAI nếu ≤ 2 phút, không thì backoff `0.5s × 2^n` (tối đa 8s) có jitter 0–25%. 4xx khác (400, 401, 404...) **không** retry |

Rate limit in-memory hỏng khi nào; sau proxy thì IP còn đúng không:

- _(Claude viết)_ `_hits` là dict trong RAM của **1 process** → hỏng khi: (1) **restart / redeploy** (kể cả
  `fastapi dev` auto-reload khi lưu code) → bộ đếm về 0; (2) **nhiều worker** (`uvicorn --workers 4`) → mỗi worker 1
  dict riêng, thực tế cho tới 5 × 4 = 20 request/phút; (3) **nhiều server / instance** sau load balancer → tương tự,
  chia đều cho mỗi máy; (4) `_hits` không bao giờ xoá IP cũ → bộ nhớ tăng dần nếu nhiều IP lạ. Cách chuẩn: lưu ở
  **Redis** (`INCR` + `EXPIRE`, hoặc sorted set cho sliding window) để mọi worker/server dùng chung và tự hết hạn.
- _(Claude viết)_ Sau proxy (Railway, Vercel, Nginx, Cloudflare): kết nối TCP tới app là **từ proxy**, nên
  `request.client.host` là IP của proxy → **mọi user chung 1 IP** → 5 request/phút cho cả hệ thống. IP thật nằm ở
  header `X-Forwarded-For` (hoặc `X-Real-IP`, `CF-Connecting-IP`). Chỉ tin header đó khi request đúng là đi qua
  proxy của mình (header này client tự gửi giả được) → uvicorn có `--proxy-headers` + `--forwarded-allow-ips` để làm
  việc này. Sẽ kiểm lại khi deploy Buổi 12 (chưa thử trên Railway/Vercel thật).
- _(Claude viết)_ Ghi thêm: retry của SDK áp dụng cho **lời gọi tạo stream**; nếu stream đã chạy rồi mới đứt giữa
  chừng thì không có retry (suy luận từ cách SDK retry theo HTTP request, chưa thử) → `chat_events` bắt
  `APIError` và gửi `event: error`.
- Bản của mình:

## Bài 5 — Test

Test (`uv run pytest` trong `backend/`):

_(Claude viết, 2026-10-18, theo yêu cầu. Nguồn: `uv run pytest -v` → **10 passed in 0.08s**; `ruff` + `pyright` sạch;
`logs/cost.jsonl` 13 dòng trước và sau khi chạy test → test không ghi vào log thật.)_

| Test                                               | Kiểm cái gì                                                                                                                                                                                                                                       |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_health`                                      | `/health` → 200 `{"status": "ok"}`                                                                                                                                                                                                                |
| `test_chat_stream_missing_api_key`                 | thiếu key → 401 JSON (dependency chạy trước stream)                                                                                                                                                                                               |
| `test_chat_stream_with_fake_openai`                | 1 bước không tool: `delta, delta, done`, usage + cost đúng, gửi đúng `input`/`model`/`stream`                                                                                                                                                     |
| `test_tool_loop_two_steps`                         | `tool_call → tool_result → delta → delta → done`; `arguments` là dict; cùng `call_id`; `steps == 2`; usage cộng 2 bước (100+150 / 10+5); bước 2 có `function_call_output` đúng `call_id`; cost log 1 dòng `status: ok`, `tools: ["query_orders"]` |
| `test_tool_error_still_done`                       | tool không tồn tại → `tool_result ok:false` (`"Unknown tool: nope"`), **không** có `event: error`, vẫn kết thúc bằng `done`                                                                                                                       |
| `test_openai_error_mid_stream`                     | OpenAI đứt sau 1 delta (`APIConnectionError`) → `delta, error`; status vẫn 200 (stream đã bắt đầu); cost log `status: error` (finally vẫn ghi)                                                                                                    |
| `test_rate_limit_6th_is_429`                       | 6 request → `[200×5, 429]`, có header `retry-after`; OpenAI giả chỉ bị gọi 5 lần (429 chặn trước khi tới OpenAI)                                                                                                                                  |
| `test_sales_summary_by_product_excludes_cancelled` | CSV 4 dòng tự tạo: gom theo món, bỏ đơn cancelled, doanh thu giảm dần                                                                                                                                                                             |
| `test_sales_summary_by_day_sorted_ascending`       | gom theo ngày, ngày tăng dần                                                                                                                                                                                                                      |
| `test_sales_summary_only_cancelled`                | `status="cancelled"` → chỉ đơn huỷ                                                                                                                                                                                                                |

- _(Claude viết)_ Cách làm:
  - **`tests/conftest.py`**: fixture `autouse` `isolate` (~ `beforeEach` + `afterEach`): xoá `rate_limit._hits`,
    `monkeypatch` `cost_log.LOG_FILE` sang `tmp_path`, sau test `app.dependency_overrides.clear()`. Không có nó: bộ đếm
    rate limit cộng dồn qua các test (test thứ 6 bị 429 vô cớ) và mỗi lần `pytest` thêm dòng rác vào log thật.
  - **Fake OpenAI nhận danh sách "script"** (mỗi script = event của 1 bước) → giả được tool loop nhiều bước mà không
    gọi API thật; `error=` để giả OpenAI đứt giữa stream. Function call giả dùng type thật `ResponseFunctionToolCall`
    vì `execute_call` và `main` đọc `.name` / `.arguments` / `.call_id`.
  - **Refactor nhỏ `app/tools.py`**: đường dẫn CSV thành hằng `ORDERS_CSV` ở cấp module → test `monkeypatch` sang CSV
    nhỏ. `monkeypatch` có tác dụng vì hàm đọc hằng **lúc chạy**, không phải lúc import.
- _(Claude viết)_ Chưa phủ / hạn chế:
  - `test_tool_loop_two_steps` vẫn đọc `data/orders.csv` thật qua `query_orders` (chưa dùng `ORDERS_CSV`) → sửa data có
    thể làm test fail.
  - Chưa test **cancel** (người dùng bấm Dừng): `TestClient` khó giả client ngắt kết nối giữa stream → đang dựa vào lần
    thử tay ở Bài 3 (`status: cancelled`).
  - Chưa test `get_weather` (gọi mạng thật) — nếu test thì phải mock HTTP (vd `respx`) để không phụ thuộc Open-Meteo
    (đã gặp 503 ở Bài 2).
- Bản của mình:

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

### 1. Agent gọi tool trong lúc đang stream: luồng event giữa backend và frontend thiết kế thế nào?

_(Bản tham khảo Claude viết, 2026-10-18, theo yêu cầu — dựa trên code p1 backend Bài 2.)_

- Backend dịch event của OpenAI thành **5 event SSE riêng** cho frontend, frontend không thấy event gốc như
  `response.completed`:
  - `delta {content}`
  - `tool_call {call_id, name, arguments}`
  - `tool_result {call_id, name, ok, data | error}`
  - `done {input_tokens, output_tokens, cost_usd, steps, incomplete}`
  - `error {message}`

- Thứ tự: có tool thì `tool_call → tool_result` (lặp nếu nhiều bước) `→ delta… → done`; không tool thì
  `delta… → done`.

- Frontend ghép `tool_call` với `tool_result` bằng **`call_id`**, vì model có thể gọi nhiều tool song song trong 1 bước.

- Tool lỗi → `tool_result ok:false`, stream chạy tiếp để model tự xử lý. OpenAI lỗi → `event: error` rồi dừng.

- TTFT có tool là 3–7s → UI phải hiện trạng thái theo tên tool ("Đang tra đơn hàng…"), đổi ✓ / ⚠ khi có
  `tool_result`.

Bản nháp của mình (2026-10-18): có event incomplete/completed...; ghép `tool_call`–`tool_result` bằng tool id; UI hiện
"đang xử lý…" lúc chờ tool.

Bản của mình:

### 2. Tính và giới hạn chi phí cho 1 endpoint chat LLM như thế nào (cost log, rate limit, max tokens)?

_(Claude viết lại từ nháp 3 ý của mình + bổ sung cost log / giới hạn khác, 2026-10-19, theo yêu cầu. Ý "OpenAI vẫn
tính output đã sinh khi cancel" dựa trên forum cộng đồng OpenAI, chưa thấy docs chính thức.)_

- Chi phí tính theo token input và token output, mỗi loại một giá. Thường input rẻ hơn output (model đang dùng:
  $0.10 / 1M input, $0.50 / 1M output, tức output đắt gấp 5).

- Với tool loop, input mới là phần tốn tiền chính: mỗi bước gửi lại toàn bộ lịch sử nên input cộng dồn (câu 2 tool:
  2368 input, chỉ 201 output).

- Cost log: cộng usage qua mọi bước, ghi 1 dòng mỗi request trong `finally`, nên request lỗi hay bị cancel vẫn có log.

- Bị cancel giữa stream: OpenAI vẫn tính input cùng phần output đã sinh tới lúc ngắt. Nhưng bước bị ngắt không tới
  `response.completed` nên log không có usage của bước đó và ghi thiếu (cần ước lượng hoặc đánh dấu).

- Giới hạn mỗi request: `max_output_tokens` (không đặt thì model sinh tới giới hạn tối đa của nó, nên luôn phải đặt),
  `max_length` cho input, `MAX_STEPS` cho số vòng tool.

- Giới hạn tổng: rate limit theo IP trả 429 trước khi gọi OpenAI, nên request bị chặn tốn $0.

### 3. Rate limit in-memory có vấn đề gì khi scale, thay bằng gì?

_(Claude viết, 2026-10-19, theo yêu cầu. Nguồn: `app/rate_limit.py`; ý 2–4 suy ra từ code, chưa chạy thử
`--workers 4`; ý proxy chưa kiểm trên Railway/Vercel thật — kiểm lại Buổi 12.)_

- Hiện tại: bộ đếm `_hits` là dict lưu trong RAM của 1 process (sliding window, 5 request / 60s / IP).

- Restart / redeploy / `fastapi dev` reload → bộ đếm về 0 → user vừa bị chặn lại được gọi tiếp ngay.

- Nhiều worker (`--workers 4`) → mỗi worker có dict riêng, không biết nhau → thực tế 1 IP được tới 5 × 4 = 20
  request/phút.

- Nhiều server sau load balancer → mỗi máy đếm riêng, giới hạn thật nhân lên theo số máy.

- Rò bộ nhớ: `_hits` chỉ xoá mốc thời gian cũ, không bao giờ xoá key IP → nhiều IP lạ thì dict phình dần.

- Sau proxy (Railway, Vercel): `request.client.host` là IP của proxy → mọi user chung 1 bộ đếm, cả hệ thống chỉ được
  5 request/phút. Sửa: đọc IP thật từ header `X-Forwarded-For`, nhưng chỉ tin header đó khi request đi qua proxy của
  mình (vì client tự gửi giả được) — uvicorn có `--proxy-headers` + `--forwarded-allow-ips`.

- Thay bằng: Redis dùng chung cho mọi worker/server, có TTL tự xoá. Cách đếm: `INCR` + `EXPIRE` (fixed window, đơn
  giản) hoặc sorted set (sliding window, chính xác hơn, giống bản hiện tại).
