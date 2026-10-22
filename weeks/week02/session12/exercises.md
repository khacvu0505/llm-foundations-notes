# Buổi 12 — Hoàn thiện Project #1 + REBUILD TEST (4h, T7)

Code **không** nằm ở thư mục này: Project #1 ở `projects/p1-smart-copilot/` (`backend/` + `web/`). Rebuild test làm
ở **thư mục mới ngoài repo**. Thư mục `weeks/week02/session12/` chỉ có đề bài (file này) + `notes.md`.

Checklist Notion Buổi 12:

- Polish Project #1: README tử tế (kiến trúc, screenshot/GIF demo), deploy (Railway/Render + Vercel) → Phần A
- Rebuild test: repo trắng, dựng lại "hỏi → tool call → stream → render UI" trong 1 buổi, KHÔNG nhìn code cũ.
  Chưa làm được = chưa qua phase → Phần B

Exit criteria Phase 01 (cổng qua Phase 02): rebuild test pass · trả lời trôi chảy 4 câu (SSE vs WebSocket, tool fail
giữa stream, structured output retry, temperature) · Project #1 có **link demo sống** + README · giải thích được
transformer / tokens / context window bằng lời của mình.

| Phần                                          | Thời lượng | Làm ở đâu                                  |
| --------------------------------------------- | ---------- | ------------------------------------------ |
| A1: chuẩn bị deploy (local → prod khác gì)    | ~25ph      | `backend/`, `web/`                         |
| A2: deploy backend (Render)                   | ~30ph      | dashboard Render                           |
| A3: deploy frontend (Vercel) + kiểm trên prod | ~25ph      | dashboard Vercel                           |
| A4: IP thật sau proxy (rate limit)            | ~30ph      | `web/app/api/chat/route.ts`, `backend/app/` |
| A5: README + GIF demo                         | ~30ph      | `projects/p1-smart-copilot/README.md`      |
| B: Rebuild test                               | ≤ 3h       | `~/rebuild-p1/` (ngoài repo)               |

Gợi ý chia: Phần A hôm nay. Phần B làm **ngày khác**, đầu óc tỉnh — làm ngay sau 2h sửa code cũ thì trí nhớ ngắn hạn
giúp mình, kết quả test không thật.

---

## Phần A — Hoàn thiện + deploy

Đường đi sau deploy:

```
Trình duyệt ──► Vercel (Next: /api/chat) ──► Render (FastAPI: /chat/stream) ──► OpenAI
                                                   └──► tools (CSV, Open-Meteo)
```

### Bài A1 — Local → prod khác gì? (~25ph)

Trước khi bấm deploy, tự trả lời từng dòng (ghi vào `notes.md`), sửa code nếu cần:

- **Lệnh chạy**: `fastapi dev` → `fastapi run`. Khác gì (reload, host mặc định, port lấy từ đâu)? Tự xem
  `uv run fastapi run --help` trong `backend/`.
- **CORS** `origins = ["http://localhost:3100"]` (`backend/app/main.py`): trình duyệt còn gọi FastAPI trực tiếp không?
  Bỏ hẳn hay đọc từ env? (Câu hỏi đã mở từ Setup Buổi 11.)
- **`logs/cost.jsonl`**: ổ đĩa của web service trên Render có giữ file qua lần deploy / restart không? (Tra docs
  Render "ephemeral filesystem".) Mất thì sao — còn chỗ nào thấy cost không?
- **File cần có trong git**: `data/orders.csv`, `uv.lock`, `.python-version`, `pnpm-lock.yaml` → kiểm `git ls-files`.
  File **không** được có: `.env`, `.env.local`.
- **Bản build Next**: `pnpm build && pnpm start` chạy được không? Stream có còn chảy từng mảnh ở bản build (khác dev:
  có nén)? `/mock` và `/api/chat-mock` có trả `404` không? (Nợ Buổi 11: header `X-Frame-Options` / CSP ở bản build.)
- **Key cho prod**: dùng lại key local hay tạo key mới? Link demo public = ai cũng bấm được → đặt **giới hạn chi tiêu**
  cho project OpenAI dùng key này (tra dashboard OpenAI, mục Limits / Budget).

### Bài A2 — Deploy backend lên Render (~30ph)

- New → Web Service → nối GitHub repo. Repo có nhiều project → **Root Directory** trỏ vào đâu?
- Build command / Start command: tự tìm trong docs Render (Python + uv; Render cần `uv.lock` ở root directory).
  Start command dùng `fastapi run` từ Bài A1. Port: Render đặt biến `PORT` — `fastapi run` có tự đọc không?
- Environment: `OPENAI_API_KEY`, `APP_API_KEY` (giá trị prod). Health check path: `/health`.
- Kiểm bằng `curl` (ghi bảng trong `notes.md`):
  - `/health` → `200`
  - `/chat/stream` có key → chữ chảy từng mảnh hay dồn cục qua proxy Render? (`curl -N`)
  - không key → `401`; 6 lần liên tiếp → `429`
  - Tool "Đơn nào của An đang giao?" → có `tool_call` / `tool_result` (đọc được `orders.csv` trên server)
  - **Cold start**: gói free ngủ sau 15ph không có request, ~1ph để dậy (theo docs Render, kiểm lại). Để yên > 15ph rồi
    gọi `/health`, đo mất bao lâu.

Thay thế: **Railway** không ngủ, nhưng chỉ có $5 dùng thử 1 lần, sau đó Hobby $5/tháng (kiểm trang pricing trước khi
chọn). Chọn cái nào thì ghi lý do vào README.

### Bài A3 — Deploy frontend lên Vercel + kiểm trên prod (~25ph)

- Import repo → Root Directory là gì? Vercel nhận pnpm từ đâu (`packageManager` trong `package.json`)?
- Env: `APP_API_KEY` (khớp backend prod), `BACKEND_URL` = URL Render (`https://…`, không có `/` cuối).
  Vì sao **không** dùng `NEXT_PUBLIC_`? (Buổi 9 Bài 5B.)
- Kiểm trên link Vercel thật, ghi bảng:
  - 4 câu thật (đơn hàng / bán chạy / thời tiết / 2 tool) → component + chữ chảy mượt
  - Dừng giữa chừng → log Render có `cancelled`?
  - DevTools: Network chỉ thấy `/api/chat`, Sources không thấy key
  - `/mock` → `404`
  - Nhúng iframe: sửa `embed-test/index.html` trỏ `src` sang URL Vercel, mở bằng `python3 -m http.server 5500`
  - Hỏi lúc Render đang ngủ → widget hiện gì trong ~1ph chờ? Có cần báo "đang khởi động" không?
- Giới hạn Vercel gói Hobby: 1 lần chạy function tối đa **300s, tính cả thời gian stream** (docs Vercel "Functions
  limitations"). Câu trả lời của mình dài nhất bao lâu? Có chạm không?

### Bài A4 — IP thật sau proxy (~30ph)

Buổi 11 đã đoán: FastAPI giờ nhận request **từ Next server**, không phải từ user → mọi user dùng chung 1 bộ đếm rate
limit. Local không chứng minh được (đều là `127.0.0.1`). Giờ có prod để đo.

1. **Đo trước, sửa sau**: tạm in ra trong `rate_limit` 2 thứ: `req.client.host` và header `x-forwarded-for`. Gọi từ
   2 mạng khác nhau (laptop wifi + điện thoại 4G). Backend thấy IP gì? 2 máy có chung bộ đếm không? Ghi bảng.
2. **Sửa**: Route Handler lấy IP thật của user rồi gửi sang FastAPI bằng 1 header riêng; `rate_limit` đếm theo header
   đó. Vercel đặt sẵn `x-forwarded-for` và **ghi đè** giá trị client gửi lên để chống giả (docs Vercel "Request
   headers" — đọc và kiểm).
3. **An toàn**: vì sao FastAPI được tin header này, còn header `X-Forwarded-For` do trình duyệt tự gửi thì không?
   Gợi ý: ai gọi được `/chat/stream`? `verify_api_key` có chạy **trước** `rate_limit` không (thứ tự trong
   `dependencies=[...]`)? Thiếu header thì đếm theo gì?
4. **Kiểm**: 2 máy → 2 bộ đếm riêng. `curl` thẳng Render với header IP giả nhưng không có key → `401`.
   Thêm 1 test pytest cho case "2 IP khác nhau không chung lượt".

Câu hỏi ghi notes: `--forwarded-allow-ips` của `fastapi run` dùng để làm gì? Vì sao bật `'*'` là nguy hiểm?

### Bài A5 — README + GIF demo (~30ph)

1 file `projects/p1-smart-copilot/README.md` — người đọc là **nhà tuyển dụng có 2 phút**. Gợi ý mục:

- 1 câu mô tả + **link demo** + GIF (dưới 5MB, để trong `projects/p1-smart-copilot/docs/`)
- Kiến trúc: sơ đồ (Mermaid, GitHub tự vẽ) + bảng event SSE; vì sao key nằm ở server
- Tính năng: tool calling (3 tool), SSE streaming, Generative UI, widget nhúng iframe, Dừng, rate limit, cost log
- Quyết định + đánh đổi: SSE vs WebSocket; Route Handler làm proxy; rate limit in-memory (chỉ đúng với 1 instance)
- Hạn chế đã biết: chưa nhớ hội thoại (backend nhận 1 `message`), cost log mất khi redeploy, cold start, …
- Số đo thật: TTFT, cost / câu (lấy từ notes Buổi 10–11 và prod)
- Chạy local (2 terminal, biến môi trường) + deploy (Render + Vercel)

Quay GIF trên macOS: `Cmd+Shift+5` quay màn hình → đổi sang GIF (vd `ffmpeg`, `gifski` hoặc app Kap). Dọn
`web/README.md` (đang là mẫu của create-next-app) và `backend/README.md` (đang trống, `pyproject.toml` có trỏ tới).

---

## Phần B — REBUILD TEST (≤ 3h, ngày khác)

**Luật** (nghiêm, vì đây là cổng qua phase):

- Thư mục mới **ngoài repo**: `~/rebuild-p1/`, `git init` mới. Không mở repo cũ, notes cũ, lịch sử chat.
- **Tắt AI trong editor** (Copilot / Kilo / Cursor Tab…). Không hỏi AI chat.
- Được dùng: docs chính thức (OpenAI API reference, FastAPI, Next.js docs trong `node_modules/next/dist/docs/`, MDN),
  Google / Stack Overflow để tra lỗi.
- Bấm đồng hồ, ghi mốc thời gian từng bước + chỗ vướng (bảng trong `notes.md`).

**Phải chạy được** (pass = đủ 6/6 trước khi hết giờ):

1. FastAPI `POST` endpoint gọi OpenAI có `stream=True`
2. 1 tool thật + vòng lặp tool: model gọi → mình chạy → gửi kết quả lại → model trả lời; có giới hạn số bước
3. SSE có ít nhất `delta`, `tool_result`, `done`; lỗi giữa stream → event `error` (không chết im lặng)
4. Trang Next.js: `fetch` + `getReader()`, tách event, chữ chảy từng mảnh
5. `tool_result` → render 1 component (card hoặc bảng), không in JSON thô
6. OpenAI key chỉ nằm ở backend

**Không bắt buộc** (làm nếu dư giờ): Route Handler proxy, nút Dừng, rate limit, cost log, iframe, test, type đầy đủ.

Sau khi xong: (tuỳ chọn) mới mở code cũ ra so — bản nào gọn hơn, chỗ nào bản mới tốt hơn. Chỗ vướng = danh sách ôn
trước khi sang Phase 02.
