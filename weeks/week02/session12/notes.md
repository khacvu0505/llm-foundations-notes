# Buổi 12 — Hoàn thiện Project #1 + REBUILD TEST (4h)

Đề bài: `exercises.md` cùng thư mục.

- [ ] A1 chuẩn bị deploy · [ ] A2 backend Render · [ ] A3 frontend Vercel · [ ] A4 IP thật · [ ] A5 README + GIF
- [ ] B Rebuild test

Link demo:

- Frontend (Vercel):
- Backend (Render):

## Trạng thái đầu buổi

_(Claude ghi, 2026-10-20. Nguồn: `git status`, `uv run ruff check . / pyright / pytest -q` trong `backend/`,
`pnpm lint / exec tsc --noEmit / test` trong `web/`; Notion Phase 01 qua API public của notion.site.)_

- Git sạch, commit cuối `f31bc8d` (Buổi 11 Bài 4 + 5).
- Backend: ruff sạch, pyright 0 lỗi, pytest **10/10**. Web: lint sạch, tsc sạch, vitest **15/15**.
- Notion: Buổi 9, 10, 11 **chưa tick** (MCP Notion không truy cập được workspace này → tự tick tay).

## Bài A1 — Local → prod khác gì

| Câu hỏi                                   | Trả lời / quyết định |
| ----------------------------------------- | -------------------- |
| `fastapi dev` vs `fastapi run`            | Prod dùng `fastapi run` (no reload, host `0.0.0.0`, port đọc `PORT`) — chi tiết Q1 dưới bảng |
| CORS `origins` còn cần không              | Không — đã bỏ `CORSMiddleware` khỏi `main.py` — chi tiết Q2 dưới bảng |
| `logs/cost.jsonl` trên Render             | Mất khi redeploy / restart — chấp nhận, xem cost qua Render logs + OpenAI Usage — chi tiết Q3 dưới bảng |
| File phải / không được có trong git       | OK — đủ 4 file cần có, `.env` / `.env.local` bị ignore, chưa từng vào lịch sử — chi tiết Q4 dưới bảng |
| `pnpm build && pnpm start`: stream, `/mock` | Build pass (sau `pnpm install`), stream chảy từng mảnh, `/mock` + `/api/chat-mock` → `404` — chi tiết Q5 dưới bảng |
| Key prod + giới hạn chi tiêu OpenAI       | Key mới trong project OpenAI riêng + **hard limit** theo tháng — chi tiết Q6 dưới bảng |

### Q1 — `fastapi dev` vs `fastapi run`

Nguồn: `uv run fastapi run --help` / `uv run fastapi dev --help` trong `backend/`.

|        | `fastapi dev`                          | `fastapi run`                                  |
| ------ | -------------------------------------- | ---------------------------------------------- |
| Reload | bật — sửa file là tự restart           | tắt — chỉ chạy lại khi server restart          |
| Host   | `127.0.0.1` — chỉ máy này gọi được     | `0.0.0.0` — máy khác gọi được (Render cần)     |
| Port   | biến `PORT` nếu có, không thì `8000`   | giống `dev`                                    |

- Render: request đi từ proxy của Render (máy khác) vào container → host `127.0.0.1` sẽ từ chối → deploy fail / 502.
- Render tự đặt `PORT` → start command chỉ cần `fastapi run`, **không** cần `--port $PORT`.
- Reload trong prod: tốn CPU theo dõi file, server có thể tự restart giữa lúc đang stream.

### Q2 — CORS còn cần không

CORS chỉ do **trình duyệt** kiểm. Server gọi server thì không bị CORS chặn.

| Ai gọi                      | Bằng chứng                                              | Có CORS check? |
| --------------------------- | ------------------------------------------------------- | -------------- |
| Trình duyệt → Next          | `ChatWidget.tsx:17` `endpoint = "/api/chat"` (cùng origin) | Không          |
| Next server → FastAPI       | `route.ts:12` `fetch(\`${backendUrl}/chat/stream\`)`      | Không          |
| iframe `/embed` → Next      | widget trong iframe vẫn gọi `/api/chat` của Next         | Không          |

- Quyết định: **bỏ hẳn** (option A), không đọc từ env (option B) — trình duyệt không bao giờ gọi thẳng FastAPI, giữ lại là code chết.
- Lợi thêm: không có header CORS → web lạ không gọi được FastAPI từ trình duyệt; đúng thiết kế "chỉ Next server gọi
  FastAPI" (Next giữ `APP_API_KEY`).
- Bớt 1 env var phải cấu hình trên Render.
- Khi nào thêm lại: nếu sau này trình duyệt gọi thẳng FastAPI (frontend khác không qua proxy) → lúc đó mới đọc
  `origins` từ env.

### Q3 — `logs/cost.jsonl` trên Render

Nguồn: [Render Disks](https://render.com/docs/disks), [Render Logging](https://render.com/docs/logging) (số 7 ngày lấy
từ kết quả search, chưa mở trực tiếp trang được).

- Render mặc định **ephemeral filesystem**: file ghi lúc chạy **mất khi deploy và restart**. Free plan ngủ sau 15ph →
  thức dậy = restart → cũng mất.
- Persistent disk chỉ có ở service **trả phí** → free plan không có cách giữ file.

Chỗ khác xem cost:

| Nơi             | Thấy gì                                         | Hạn chế                                  |
| --------------- | ----------------------------------------------- | ---------------------------------------- |
| Render Logs     | dòng `[cost] ...` từng request (`cost_log.py` `print`) | Hobby giữ **7 ngày**, khó cộng tổng   |
| OpenAI Usage    | tiền thật đã trừ theo key / project             | không chia theo từng câu hỏi             |
| `cost.jsonl`    | đủ field, dễ phân tích                          | chỉ còn dùng được ở local                |

- Quyết định: **chấp nhận mất** cho bản demo, không sửa code. OpenAI Usage là nguồn số liệu chính xác nhất (tiền thật).
- Ghi vào README mục **Hạn chế đã biết** (A5): cost log mất khi redeploy / restart.
- Nếu cần sau này: đẩy record vào DB hoặc dịch vụ log ngoài — ngoài phạm vi hôm nay.

### Q4 — File phải / không được có trong git

Render / Vercel build từ **repo GitHub**, không từ laptop. Nguồn: `git ls-files projects/p1-smart-copilot`,
`git check-ignore -v`, `git log --all -- backend/.env web/.env.local` (2026-10-25).

| Phải có                   | Trong git? | Vì sao                                                              |
| ------------------------- | ---------- | ------------------------------------------------------------------- |
| `backend/data/orders.csv` | ✅         | tool đơn hàng đọc file này trên server; thiếu → tool lỗi trên prod  |
| `backend/uv.lock`         | ✅         | Render cài đúng version đã test (`uv sync`)                         |
| `backend/.python-version` | ✅         | chốt Python `3.12` cho Render                                       |
| `web/pnpm-lock.yaml`      | ✅         | Vercel cài đúng version; pnpm lấy từ `packageManager: pnpm@10.31.0` |
| `backend/.env.example`, `web/.env.example` | ✅ | mẫu tên biến, giá trị rỗng / placeholder (đã kiểm, không có key thật) |

| Không được có     | Trong git? | Bị ignore bởi                     | Vì sao                                 |
| ----------------- | ---------- | --------------------------------- | -------------------------------------- |
| `backend/.env`    | ❌ (đúng)  | `.gitignore:218` (root)           | chứa `OPENAI_API_KEY`, `APP_API_KEY`   |
| `web/.env.local`  | ❌ (đúng)  | `web/.gitignore:35`               | chứa `APP_API_KEY`                     |

- 2 file secret có trên disk nhưng bị ignore, và `git log --all` không có commit nào chứa chúng → key chưa từng lộ.
- Trên prod: giá trị secret nhập vào **Environment** của dashboard Render / Vercel, không qua git.

### Q5 — Bản build Next (`pnpm build && pnpm start`)

Nguồn: chạy `pnpm build` trong `web/` (2026-10-25) + đọc code.

| Kiểm                          | Kết quả                                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------------------- |
| `pnpm build` (lần 1)          | ❌ fail ở bước type check: `lib/sse.test.ts`, `lib/applyEvent.test.ts` — `Cannot find module 'vitest'` |
| Vì sao fail                   | `vitest` có trong `package.json` + `pnpm-lock.yaml`, nhưng **không có** trong `node_modules` local (cài cũ) → sửa: `pnpm install`. Vercel cài từ lockfile nên khả năng cao không bị — kiểm lại ở A3 |
| `pnpm build` (sau `pnpm install`) | ✅ pass. Route: `/`, `/embed`, `/mock` = `○ Static`; `/api/chat`, `/api/chat-mock` = `ƒ Dynamic` |
| `/api/chat-mock`              | ✅ `404` (`curl -X POST` vào bản `pnpm start`) — guard `route.ts:90` `NODE_ENV === "production"` |
| `/mock` (trang)               | ✅ đã sửa (xem checklist dưới). Trước khi sửa: ❌ **không có guard** (`app/mock/page.tsx`) — build xác nhận: `/mock` được prerender `○ Static` → prod vẫn hiện trang; widget gọi route giả → nhận 404 → trang hỏng. Cần thêm guard. `curl localhost:3100/mock` (trước khi sửa) → `200` |
| Stream ở bản build            | ✅ chảy từng mảnh: `curl -N` qua `/api/chat` (câu thời tiết), mỗi `delta` cách nhau vài ms, không dồn cục (curl không xin nén → chưa kiểm trường hợp trình duyệt gửi `Accept-Encoding`) |
| Header `X-Frame-Options` / CSP | ✅ bản build **không có** cả 2 (`curl -I /embed`: chỉ `X-Powered-By`, `Cache-Control`) → nhúng iframe không bị chặn. Code không đặt (`next.config.ts` không có `headers()`) |
| TTFT lần đo này               | ⚠️ `ttft_ms` = 28822, `latency_ms` = 29213 (`cost.jsonl`, model `gpt-6-luna`, 2 bước, `get_weather`). ~25s mới có `tool_call` → chậm bất thường, đo lại ở A2 |
| `print` của backend           | ⚠️ chạy `fastapi run` ghi ra file: có dòng uvicorn, **không có** `[cost]` / `[step]` dù `cost.jsonl` đã ghi record. Giả thuyết: Python **buffer stdout** khi không phải terminal → trên Render log có thể đến trễ / mất khi crash. Hướng sửa: env `PYTHONUNBUFFERED=1` trên Render (hoặc `print(..., flush=True)`) — kiểm ở A2 |

Việc còn lại (thực hành):

- [x] `pnpm install` trong `web/` → `pnpm build` pass
- [x] Thêm guard cho trang `/mock` ở prod → `404`: tách `page.tsx` (Server Component, `notFound()` khi
  `NODE_ENV === "production"`) + `MockClient.tsx` (`"use client"`, UI cũ). Lý do tách: docs Next — `notFound()` chỉ
  gọi được trong Server Component / Server Function / Route Handler.
- [x] `pnpm start` + backend: hỏi 1 câu, chữ có chảy từng mảnh không
- [x] `curl -i localhost:3100/api/chat-mock` → `404`; `curl -I localhost:3100/embed` → có `X-Frame-Options` / CSP không
- [x] Sau khi thêm guard: `pnpm build` lại → `curl /mock` → `404` (HTML có "This page could not be found" + `noindex`).
  `/mock` vẫn `○ Static`: lúc build `NODE_ENV` = production → Next prerender sẵn **trang 404**, không còn UI mock.
  `/`, `/embed` vẫn `200`; tsc 0 lỗi, lint sạch, vitest 15/15.

### Q6 — Key prod + giới hạn chi tiêu OpenAI

Nguồn: [Managing projects](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform),
[Usage and spend limits](https://help.openai.com/en/articles/6614457-troubleshooting-api-usage-and-spend-limits),
[Changelog](https://platform.openai.com/docs/changelog) (qua kết quả search; UI có thể đã đổi tên).

- Link demo public = ai cũng bấm được → **không dùng lại key local**. Tạo **project OpenAI riêng** cho prod + key mới.
- Giới hạn đặt theo **org hoặc project**, **không** theo từng key → muốn giới hạn riêng cho demo thì cần project riêng.
- **Alert** chỉ gửi thông báo, **không** chặn. Phải bật **hard limit** mới chặn: vượt mức → request trả `429`
  (`project_spend_limit_exceeded`). Chặn không tức thì → có thể vượt nhẹ.
- Project bị chặn không ảnh hưởng project khác (key local vẫn chạy).
- Thêm: đặt **ngày hết hạn** cho key prod (tính năng mới của project key).
- Liên quan code: OpenAI trả `429` khi hết budget → backend báo lỗi gì cho user? (kiểm ở A2/A3).

Việc còn lại (dashboard):

- [ ] Tạo project prod + key mới (có hạn) → dán vào Environment trên Render
- [ ] Bật hard limit theo tháng cho project (mức tự chọn, vd vài $) + alert

## Bài A2 — Backend trên Render

Root Directory: · Build: · Start:

| Thử                          | Kết quả |
| ---------------------------- | ------- |
| `/health`                    |         |
| Stream có key (`curl -N`)    |         |
| Không key                    |         |
| 6 lần liên tiếp              |         |
| Tool đơn hàng (đọc CSV)      |         |
| Cold start (> 15ph không gọi) |        |

Quan sát:

## Bài A3 — Frontend trên Vercel

Root Directory: · Env:

| Thử                                 | Kết quả |
| ----------------------------------- | ------- |
| 4 câu thật                          |         |
| Dừng → Render log `cancelled`       |         |
| DevTools không thấy key             |         |
| `/mock` → 404                       |         |
| iframe từ origin khác               |         |
| Hỏi lúc Render đang ngủ             |         |
| Câu dài nhất (so với giới hạn 300s) |         |

Quan sát:

## Bài A4 — IP thật sau proxy

Đo trước khi sửa:

| Máy / mạng      | `req.client.host` | `x-forwarded-for` | Chung bộ đếm? |
| --------------- | ----------------- | ----------------- | ------------- |
| Laptop (wifi)   |                   |                   |               |
| Điện thoại (4G) |                   |                   |               |

Sau khi sửa:

| Thử                                     | Kết quả |
| --------------------------------------- | ------- |
| 2 máy → 2 bộ đếm riêng                  |         |
| `curl` thẳng Render, IP giả, không key  |         |
| pytest "2 IP không chung lượt"          |         |

- Vì sao tin được header IP từ Next mà không tin `X-Forwarded-For` từ trình duyệt:
- `--forwarded-allow-ips` để làm gì, vì sao `'*'` nguy hiểm:

## Bài A5 — README + GIF

- [ ] `projects/p1-smart-copilot/README.md` · [ ] GIF trong `docs/` · [ ] dọn `web/README.md`, `backend/README.md`

## Phần B — Rebuild test

Ngày làm: · Bắt đầu: · Kết thúc: · Thư mục: `~/rebuild-p1/`

| #   | Bước                                 | Mốc thời gian | Vướng gì / tra docs gì |
| --- | ------------------------------------ | ------------- | ---------------------- |
| 1   | FastAPI + OpenAI `stream=True`       |               |                        |
| 2   | 1 tool + vòng lặp tool               |               |                        |
| 3   | SSE `delta` / `tool_result` / `done` / `error` |     |                        |
| 4   | Next.js đọc stream, chữ chảy         |               |                        |
| 5   | `tool_result` → component            |               |                        |
| 6   | Key chỉ ở backend                    |               |                        |

Kết quả: **pass / chưa pass** (…/6) · Danh sách ôn:

## Exit criteria Phase 01 — tự trả lời (3–5 dòng, không nhìn notes)

### 1. Vì sao SSE thay vì WebSocket?

### 2. Tool call fail giữa stream thì xử lý sao?

### 3. Structured output fail thì retry thế nào?

### 4. Temperature ảnh hưởng gì?

### 5. Transformer / tokens / context window bằng lời của mình

### 6. (Mới) Deploy app LLM có streaming qua nhiều lớp proxy cần chú ý gì? Rate limit sau proxy lấy IP thế nào?

## Nợ còn lại (không chặn Buổi 12)

- Buổi 11: 4 câu phỏng vấn cuối `session11/notes.md`; tự bấm `/mock` trên Chrome thật; nền iframe trong suốt;
  Markdown thô trong câu trả lời
- Buổi 10: "Bản của mình" trong `session10/notes.md`; `Retry-After` cố định 60s
- Notion: tick Buổi 9–12 + dòng "Status dd/mm/yyyy"; nhật ký Tuần 2
