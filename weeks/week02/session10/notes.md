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
- [ ] **Tạo cấu trúc** (gợi ý, tự quyết):
      `    backend/
  app/          main.py, sse.py, tools.py, auth.py, llm.py
  tests/        test_*.py
  data/         orders.csv
  logs/         cost.jsonl (không commit)`
- [ ] **Chạy**: `uv run fastapi dev app/main.py` (trong `backend/`) → `curl http://127.0.0.1:8000/health`.
- [ ] Đọc nhanh: OpenAI docs "Function calling" mục streaming; `openai` SDK README mục "Retries";
      FastAPI "Dependencies" (lại) cho `rate_limit`.

## Nợ từ Buổi 9 (làm lúc rảnh, không chặn Buổi 10)

- [ ] `session09/notes.md`: Bài 1b, dòng so sánh `/chat` ở Bài 2, dòng "bắt → event: error" ở Bài 3, dán log
- [ ] Bấm Dừng trên trình duyệt thật: DevTools Network hiện gì, message lỗi của Chrome
- [ ] 3 câu phỏng vấn cuối `session09/notes.md`: viết lại bằng lời mình (đang là bản nháp Claude)
- [ ] Dọn `session09/web/app/page.tsx`: `console.log(JSON.stringify(chunk))`, dòng trống thừa
- [ ] Test lỗi giữa stream → đã đưa vào Bài 5 buổi này
- [ ] Notion: tick Buổi 9 + dòng Status; nhật ký Tuần 2; nợ Buổi 7, 8 (xem `session09/notes.md`)

## Bài 1 — Tách file

Import / chạy thế nào (`fastapi dev`, `pytest`, `pyright` cùng chạy được):

-

## Bài 2 — Tool loop bên trong stream

| Câu hỏi                                         | Tool được gọi | Số bước | TTFT (chữ đầu) | Tổng | Ghi chú |
| ----------------------------------------------- | ------------- | ------- | -------------- | ---- | ------- |
| "Đơn nào của An đang giao?"                     |               |         |                |      |         |
| "Tuần này món nào bán chạy nhất?"               |               |         |                |      |         |
| "Mai Đà Nẵng mưa không, có nên giao đơn không?" |               |         |                |      |         |
| Câu cần 2 tool                                  |               |         |                |      |         |
| Câu không cần tool ("Xin chào")                 |               |         |                |      |         |

Lấy function call từ stream bằng event nào, vì sao:

-

Tool sync trong async generator — đã xử lý thế nào (`get_weather`, `query_orders`):

-

Tool lỗi vs OpenAI lỗi giữa stream — gửi event gì, vì sao khác nhau:

-

UI nên hiện gì trong lúc chờ tool (ghi cho Buổi 11):

-

## Bài 3 — Cost log

| Câu hỏi | steps | tools | input | output | cost_usd | latency_ms | status |
| ------- | ----- | ----- | ----- | ------ | -------- | ---------- | ------ |
|         |       |       |       |        |          |            |        |

Câu đắt nhất, vì sao; tool schema chiếm bao nhiêu input:

-

Bị cancel giữa stream thì usage lấy ở đâu, log thế nào:

-

## Bài 4 — Chống spam

| Thử                              | Quan sát |
| -------------------------------- | -------- |
| 7 request liên tiếp (curl)       |          |
| Header `Retry-After` của 429     |          |
| SDK retry những lỗi nào, mấy lần |          |

Rate limit in-memory hỏng khi nào; sau proxy thì IP còn đúng không:

-

## Bài 5 — Test

Test (`uv run pytest` trong `backend/`):

-

## Câu phỏng vấn liên quan (tự trả lời sau buổi, 3–5 dòng)

### 1. Agent gọi tool trong lúc đang stream: luồng event giữa backend và frontend thiết kế thế nào?

### 2. Tính và giới hạn chi phí cho 1 endpoint chat LLM như thế nào (cost log, rate limit, max tokens)?

### 3. Rate limit in-memory có vấn đề gì khi scale, thay bằng gì?
