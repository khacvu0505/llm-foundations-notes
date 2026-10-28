# Buổi 12 — Hoàn thiện Project #1 + REBUILD TEST (4h)

Đề bài: `exercises.md` cùng thư mục.

- [x] A1 chuẩn bị deploy (còn Q6 hard limit OpenAI) · [x] A2 backend Render · [x] A3 frontend Vercel (7/7) ·
  [x] A4 IP thật (bỏ qua test 2 máy) · [x] A5 README (bỏ GIF + dọn 2 README cũ — user: "quan trọng là kiến thức,
  không phải show kết quả")
- [ ] B Rebuild test

Link demo:

- Frontend (Vercel): https://llm-foundations-notes.vercel.app
- Backend (Render): https://llm-foundations-notes.onrender.com

## Handoff — dừng ở đây (cập nhật 2026-10-27)

_(Claude ghi để mở session mới. Đọc mục này trước, chi tiết từng bài ở dưới.)_

**Đang dừng ở**: Phần B bước 2 (1 tool + vòng lặp tool) — tool + `get_weather` xong (đã sửa + test), **chưa có
vòng lặp**. Thư mục rebuild thật là `projects/p1-smart-copilot-v2/backend/` (không phải `~/rebuild-p1/` như bảng Phần B).

**Đã xong hôm 27/10** (`app/main.py`, chưa commit):

- Bước 1 + 3 (một phần) đã commit trước đó: `/health`, `/chat` stream, SSE `delta` / `done` / `error` (`19f4d1c`).
- Tool `get_weather_tool` đúng format **Responses API** (phẳng: `type`/`name`/`description`/`strict`/`parameters`,
  không bọc `"function"` như Chat Completions); `strict: True` + `additionalProperties: False`; `"enum": list(CITIES.keys())`
  (danh sách thành phố chỉ ở `CITIES`); `tools=TOOLS` đã truyền vào `responses.create`.
- `async def get_weather(city: str) -> WeatherResponse | WeatherError`: city lạ → trả `WeatherError` (không raise);
  gọi Open-Meteo bằng `httpx2` (đã `uv add httpx2`); `httpx2.HTTPError` → log + trả `WeatherError`; map `weather_code`
  → chữ qua `WMO_CODES`. Claude chạy thử 27/10 bằng `.venv` của v2: Hà Nội → dict thời tiết; "Huế" →
  `{'error': 'City Huế not found'}`; URL sai (404) → dict `error`, không crash.

**Việc tiếp theo (theo thứ tự)**:

1. Vòng lặp tool trong `stream_answer`: bắt item `function_call` trong stream (lấy `name`, `arguments` = JSON string,
   `call_id`) → chạy `get_weather` → gọi `responses.create` lần 2 với `previous_response_id` + input
   `function_call_output` (cùng `call_id`, `output` = `json.dumps(result)`) → stream text → `done`. Dùng `while` có giới
   hạn số vòng (vd 3). Mẹo: in mọi `event.type` một lần để xem event nào tới.
2. Bước 3 còn lại: SSE `tool_result` ngay sau khi chạy tool. Test: `curl -N` `/chat` với "Thời tiết Đà Nẵng?".
3. Bước 4–6 (Next.js, `tool_result` → component, key chỉ ở backend) + điền cột "Mốc thời gian / Vướng gì" bảng Phần B.
4. 6 câu Exit criteria cuối file (tự viết, không nhìn notes).

**Tuỳ chọn (không chặn)** cho `get_weather`:

- Lỗi HTTP đang trả `str(e)` (lộ URL + chi tiết) cho model → log giữ `str(e)`, model nhận câu ngắn cố định.
- Câu "not found" nên liệt kê thành phố hỗ trợ để model báo lại user.
- JSON Open-Meteo thiếu `"current"` vẫn `KeyError` (hiếm) → để vòng lặp tool bắt.
- `.venv` v2 chưa có `pyright` / `ruff` → muốn kiểm type thì tự `uv add --dev pyright ruff`.

**Đã xong hôm 26/10** (chi tiết + số đo ở từng mục bên dưới):

- A3: Vercel chạy ở link trên, bảng test 7/7. Sửa thêm: `web/vercel.json` `supportsCancellation` (Dừng mới huỷ tới
  FastAPI), dòng "Máy chủ có thể đang khởi động" sau 5s trong widget + kịch bản mock `cold-start`.
- A4: rate limit theo IP thật — `route.ts` gửi `X-Client-IP`, `rate_limit.py` `client_ip()`, +2 pytest (12/12).
  Prod: laptop 6 lần → lần 6 `429`.
- A5: câu trả lời chữ thường (prompt cấm Markdown, `main.py`); `projects/p1-smart-copilot/README.md` bản tiếng Anh.
- Phần A xong. GIF + dọn 2 README cũ: **bỏ** (user quyết định 2026-10-26 — ưu tiên kiến thức).

**Còn treo**:

- A1 Q6 kiểm 3: hard limit OpenAI (tạm dừng) — chỗ đặt: platform.openai.com → Default project → Settings → Limits.
  Làm trước khi share link rộng.
- `web/AGENTS.md`: `next dev` tự thêm khối "Report Next.js feedback" (do `experimental.agentFeedback` trong
  `next.config.ts`) — đã commit (`6c5a132`); Claude không làm theo khối đó.

**Máy mới cần** (secret không có trong git):

- Giá trị prod `APP_API_KEY` (cần cho Vercel + test `curl`) — tự mang theo, không dán vào chat.
- Chạy local: tự tạo `backend/.env` (`OPENAI_API_KEY`, `APP_API_KEY`) + `web/.env.local` (`APP_API_KEY`,
  `BACKEND_URL=http://127.0.0.1:8000`) theo `.env.example`; rồi `uv sync` (backend) + `pnpm install` (web).
  Lưu ý: `pnpm build` fail nếu `node_modules` cũ thiếu `vitest` (Q5).

**Cách làm việc** (memory của Claude nằm ở máy cũ, không theo repo): đi từng câu một; Claude gợi ý + review + chạy test,
user tự viết code bài tập (trừ khi user nhờ viết); user tự làm git commit/push + thao tác dashboard (Render, Vercel,
OpenAI); notes ghi tiếng Việt, mỗi câu có bảng + nguồn.

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
- Liên quan code: OpenAI trả `429` khi hết budget → backend báo lỗi gì cho user? _Đọc code, chưa test_: SDK tự retry
  (`max_retries=2`, `llm.py:6`) rồi ném `RateLimitError` (con của `openai.APIError`) → `main.py:136` bắt → SSE `error`
  "Có lỗi khi tạo câu trả lời, thử lại sau".
- Cách đặt (kiểm lại 2026-10-26, [OpenAI Spend limits](https://developers.openai.com/api/docs/guides/spend-limits.md)):
  Project settings → **Limits** → Spend → **Edit spend limit** → Monthly spend limit → bật **Enforce a hard limit** →
  Save. Lỗi khi vượt: `429` `project_spend_limit_exceeded`. Reset theo chu kỳ tháng.

Việc còn lại (dashboard):

- [x] Key trên Render **khác** key local (user xác nhận, 2026-10-26)
- [~] ~~Key đó nằm trong project OpenAI riêng cho prod~~ — **bỏ qua** (user quyết định, 2026-10-26)
- [ ] Bật hard limit theo tháng cho project (mức tự chọn, vd vài $) + alert — **tạm dừng** (user, 2026-10-26).
  Đã biết: cả 10 key (kể cả key prod "Smart Copilot" `sk-...sU4A`, tạo 25/10) đều trong **Default project** → limit đặt
  ở đây chặn luôn key local. Chỗ đặt: Settings → Limits (không phải Render: dialog "purchase minutes" là build minutes
  của Render)

## Bài A2 — Backend trên Render

Root Directory: `projects/p1-smart-copilot/backend` · Build: `uv sync --frozen && uv cache prune --ci` · Start:
`uv run fastapi run`

- Root Directory bắt buộc: gốc repo cũng có `pyproject.toml` + `uv.lock` (môi trường notes) → để trống sẽ cài nhầm.
- Build: Render điền sẵn. `--frozen` = cài đúng `uv.lock`, không tự sửa lock (`uv lock --check` local: khớp).
- Start: `run` (host `0.0.0.0`, no reload); không cần `--port` (đọc `PORT`); không cần path (tự tìm `app/main.py`).
  Placeholder `gunicorn …wsgi` là cho app sync (Flask/Django), FastAPI là ASGI.
- Env: `OPENAI_API_KEY` (key prod mới), `APP_API_KEY` (giá trị prod mới, Vercel dùng chung), `PYTHONUNBUFFERED=1`.
  Health check: `/health`. Instance: Free.

| Thử                          | Kết quả |
| ---------------------------- | ------- |
| `/health`                    | ✅ `200` `{"status":"ok"}`, 1.4s (service đang thức) |
| Stream có key (`curl -N`)    | ✅ câu thời tiết: `tool_call` → `tool_result` (`get_weather` ok) → 34 `delta` → `done` (2 bước, 1020 in / 58 out, $0.000131). **Chảy từng mảnh qua proxy Render** ✅: đo bằng `curl -sN … | perl` (ms từ lúc gửi) → `tool_call` 2545ms, `tool_result` 2949ms, 34 `delta` rải từ 3583 → 3895ms, `done` 4038ms. Vài delta trùng ms = gom theo gói mạng, bình thường; không bị buffer tới cuối |
| Không key                    | ✅ `401` `Missing API Key`; key sai → `401` `Invalid API Key` |
| 6 lần liên tiếp              | ✅ 1–5 → `200`, 6 → `429` (`LIMIT = 5` / `WINDOW_S = 60`, `rate_limit.py:6-7`) |
| Tool đơn hàng (đọc CSV)      | ✅ `query_orders(customer="An", status="shipping")` ok → 0 đơn. Đúng: An có 4 đơn (1007, 1020, 1032, 1036) đều `delivered` → `orders.csv` có trên server |
| Cold start (> 15ph không gọi) | ✅ đo được: `/health` → `200` sau **52.5s** (lúc thức: 1.4s). Khớp docs Render (~1ph). Health check nội bộ của Render không giữ service thức |

Quan sát:

- URL: `https://llm-foundations-notes.onrender.com` — deploy từ commit `0e2b5e8` (đã push).
- CORS đã bỏ thật trên prod: preflight `OPTIONS /chat/stream` với `Origin: http://localhost:3100` → `405`, không có
  header `access-control-*`.
- Render Logs có `[step 1]` + `[cost] …` → `PYTHONUNBUFFERED=1` có tác dụng (local ghi ra file thì không thấy).
- TTFT trên Render (câu ngắn "hi", 1 bước, không tool): 543ms / 969ms / 1439ms; total 0.8–2.1s → con số 28.8s ở local
  (Q5) là bất thường, không phải do code.
- Request `/health` đến từ IP nội bộ `10.219.x.x` = health check của Render.
- **Manh mối cho A4**: dòng log uvicorn ghi IP thật của mình `1.54.116.251:0` (không phải IP proxy) → uvicorn đang lấy IP
  từ `X-Forwarded-For` (`fastapi run` mặc định `--proxy-headers`). Port `:0` là dấu hiệu IP được điền từ header.
  Chưa rõ vì sao được tin (`--forwarded-allow-ips` mặc định chỉ tin `127.0.0.1` theo uvicorn — _chưa kiểm_; có thể
  Render đặt `FORWARDED_ALLOW_IPS`) → kiểm ở A4. Sau khi có Vercel, IP này sẽ là IP của Vercel, không phải user.
- Cold start ~52s: user đầu tiên sau 15ph phải chờ gần 1 phút mới có chữ → ghi README "Hạn chế đã biết"; A3 kiểm widget
  hiện gì trong lúc chờ (cần báo "đang khởi động" không?). Còn trong giới hạn 300s của Vercel function.

## Bài A3 — Frontend trên Vercel

Root Directory: `projects/p1-smart-copilot/web` · Env: `BACKEND_URL`, `APP_API_KEY`

- Root Directory: thư mục có `package.json` của Next. Gốc repo không có `package.json` → bắt buộc trỏ vào `web`.
- `BACKEND_URL` = `https://llm-foundations-notes.onrender.com` (không `/` cuối — `route.ts:12` tự nối `/chat/stream`).
- `APP_API_KEY` = **đúng giá trị prod đã đặt trên Render** (khác → mọi request `401`).
- Không dùng `NEXT_PUBLIC_`: biến có prefix này bị **inline vào JS bundle lúc `next build`** → ai mở DevTools / Sources cũng
  đọc được key (`node_modules/next/dist/docs/01-app/02-guides/self-hosting.md:39`). Không prefix → chỉ có ở server
  (Route Handler), trình duyệt không thấy.
- pnpm: Vercel chọn theo **lockfile**, **không** theo `packageManager` (field này chỉ dùng khi bật Corepack).
  `lockfileVersion: '9.0'` → pnpm 9 hoặc 10 (project mới ưu tiên 10) → kiểm dòng install trong build log.
  Nguồn: [Vercel Package Managers](https://vercel.com/docs/package-managers).
- Giới hạn Hobby (Fluid compute): default = max = **300s**, tính cả thời gian **stream**; quá → `504`
  `FUNCTION_INVOCATION_TIMEOUT`. Function chạy ở `iad1` mặc định. Nguồn:
  [Functions limits](https://vercel.com/docs/functions/limitations).
- Deployment Protection (Standard, mặc định): URL **production** (`<project>.vercel.app`) public; URL riêng từng deploy
  (`<project>-<hash>-….vercel.app`) bắt đăng nhập Vercel → share / iframe dùng URL production. Nguồn:
  [Deployment Protection](https://vercel.com/docs/deployment-protection).

| Thử                                 | Kết quả |
| ----------------------------------- | ------- |
| 4 câu thật                          | ✅ Trình duyệt (user): 4 câu (đơn của Chi đang giao / bán chạy / thời tiết Đà Nẵng / doanh thu theo ngày + thời tiết TP.HCM) đều ra kết quả. `curl` qua `/api/chat`: 1 tool + 2 tool đều đủ event |
| Dừng → Render log `cancelled`       | ❌ Dừng trên trình duyệt: Render log không có `cancelled`. `curl -m 2.5` (10:04:05, Claude test, user xác nhận đúng dòng log): Render vẫn chạy hết, `[cost] ok steps=2 tools=sales_summary,get_weather … total=4508ms` → huỷ **không** tới FastAPI. Nguyên nhân (docs): Vercel huỷ request là **opt-in** (`supportsCancellation` trong `vercel.json`), mặc định `request.signal` không bao giờ fire. ✅ **Sau khi sửa** (commit `c26f72b`, ngắt ngay sau `tool_result` đầu, 2919ms, 10:10:11): `[stream cancelled] sau 0 delta` + `[cost] cancelled steps=2 … in=475 out=55 $0.000075 ttft=- total=2776ms` (trước: chạy hết, $0.000315) |
| DevTools không thấy key             | ✅ 9 file JS của `/` + `/embed` (603KB): 0 lần `onrender`, `APP_API_KEY`, `X-API-Key`, `BACKEND_URL`, `OPENAI`; `sk-` 1 lần = `mask-type` (không phải key). Tab Network (user): hỏi 1 câu chỉ thấy `https://llm-foundations-notes.vercel.app/api/chat` |
| `/mock` → 404                       | ✅ `GET /mock` → `404`; `POST /api/chat-mock` → `404` |
| iframe từ origin khác               | ✅ `curl -I /embed`: không có `X-Frame-Options` / CSP. Nhúng thật: `embed-test/index.html` `src` → Vercel `/embed` (Claude sửa theo yêu cầu), mở `localhost:5500`, hỏi "Thời tiết ở Hà Nội và HCM hôm nay" → 2 `WeatherCard` + chữ trong iframe. Vẫn thấy **Markdown thô** (`**Hà Nội:**`, `*Cập nhật…*`) — nợ Buổi 11, nên sửa trước khi quay GIF (A5) |
| Hỏi lúc Render đang ngủ             | ✅ Có ra kết quả (user, ~10:55, không bấm giờ; cold start `curl /health` đo được 50–75s). Suốt lúc chờ widget chỉ hiện **"Đang trả lời…"** (`ChatWidget.tsx:134`) giống câu thường → dễ tưởng treo. Quyết định: sau **5s** chưa có event thì hiện thêm dòng "Máy chủ có thể đang khởi động (~1 phút)…" — CSS `animation-delay`, không thêm state. ✅ Đã sửa (Claude viết theo yêu cầu): `globals.css` `--animate-appear-late` (delay 5s, fill `both`) + `<p>` thứ 2 trong `ChatWidget.tsx` + kịch bản mock `cold-start` (event đầu sau 8s). Kiểm: lint / tsc sạch, vitest 15/15, dev CSS có class + `@keyframes appear`, mock `tool_call` tới ở 8098ms. Đã deploy (`69ddd72`): CSS prod có `animate-appear-late` + `@keyframes appear`, JS có câu "Máy chủ có thể đang khởi động" |
| Câu dài nhất (so với giới hạn 300s) | ✅ Đo được: dài nhất ~4.5s (Render thức, 2 tool). Cộng cold start 50–75s → < 80s, xa 300s. _Ước tính, chưa đo_: ca xấu nhất `MAX_STEPS = 5` (`tools.py:248`) × OpenAI `timeout=30`, `max_retries=2` (`llm.py:6`) có thể vượt 300s → Vercel `504` — hiếm |

Quan sát:

- URL: `https://llm-foundations-notes.vercel.app` (deploy 2026-10-26). `/`, `/embed` → `200`; `GET /api/chat` → `405`.
- Stream qua Vercel (đo `curl -sN … | perl`, ms từ lúc gửi), header `text/event-stream`, `x-accel-buffering: no`:
  - Thời tiết (câu ngắn): `tool_call` 3485 → `tool_result` 3787 → 36 `delta` trong **2 cục** (4877–4913ms) → `done`
    5092ms (1019 in / 60 out, $0.000132).
  - Bán chạy + thời tiết (2 tool): 2 `tool_call` 2054–2490 → 80 `delta` đến ở **30 thời điểm khác nhau** trong 401ms
    (3727 → 4128) → `done` 4399ms (1273 in / 144 out, $0.000199).
  - Kết luận: **không bị buffer tới cuối** (tool event đến trước, delta rải ra). Câu ngắn ra 2 cục = model sinh nhanh,
    mạng gom gói. curl không xin nén → chưa kiểm trường hợp trình duyệt gửi `Accept-Encoding`.
- **Dừng không tới FastAPI trên Vercel** (local Buổi 11 thì tới). Docs
  [Functions API — Cancel requests](https://vercel.com/docs/functions/functions-api-reference#cancel-requests):
  "Cancellation is opt-in" → bật bằng `vercel.json` (đặt ở Root Directory = `web/`), key `functions.<glob>` →
  `"supportsCancellation": true`. Bật rồi: client ngắt → `request.signal` fire → `fetch` sang Render bị huỷ → function
  bị **kết thúc** (việc chưa xong mà không bọc `waitUntil` / `after` thì mất) → chỉ bật cho `app/api/chat/route.ts`.
  Không bật = bấm Dừng vẫn **tốn token OpenAI** cho cả câu.
- `x-vercel-id: sin1::iad1::…` → vào Vercel ở Singapore (`sin1`), function chạy ở Washington (`iad1`, mặc định).
- Cold start Render (`curl /health` lúc ngủ): lần 1 52.5s (A2) · lần 2 **72.5s** · lần 3 **63.3s** (2026-10-26) →
  dao động 50–75s, vẫn < 300s.

## Bài A4 — IP thật sau proxy

Đo trước khi sửa:

| Máy / mạng      | `req.client.host` | `x-forwarded-for` | Chung bộ đếm? |
| --------------- | ----------------- | ----------------- | ------------- |
| Laptop (wifi, IP thật `42.116.75.55`) | `32.199.183.79` (whois: **Amazon** = IP đi ra của function Vercel, không phải IP laptop) | `32.199.183.79, 172.71.146.108, 10.194.13.185` | 3 request cuối cùng IP → `hits` 0 → 1 → 2 (có cộng). Nhưng 6 request liên tiếp **không** ra `429` |
| Điện thoại (4G) | _không đo_ — log đã cho thấy backend chỉ thấy IP Vercel | | |

Nguồn: `print` tạm trong `rate_limit.py` (commit `be3e366`), Claude gửi 6 request `"hi"` qua Vercel lúc 12:09:34–12:09:47
(#1 kèm header giả `X-Forwarded-For: 9.9.9.9`), user dán log Render.

- 3 dòng log user dán có `out=17, 17, 10` → khớp request **#4, #5, #6** (curl thấy out 10,10,10,17,17,10). #4 có
  `hits=0` → #1–#3 (trong cùng 10s) **không** được đếm vào IP `32.199.183.79` → _suy luận, chưa thấy log #1–#3_: IP đi
  ra của Vercel **đổi giữa các request** → mỗi IP một bộ đếm → 6 lần vẫn lọt. Tức là rate limit sau Vercel vừa sai
  (không theo user) vừa gần như vô tác dụng.
- `xff` có 3 chặng: `32.199.183.79` (Vercel, AWS) → `172.71.x` / `104.22.x` (whois: **Cloudflare**, lớp trước Render) →
  `10.x` (nội bộ Render). Backend lấy chặng **đầu tiên**.
- Vì sao lấy chặng đầu (đọc code uvicorn 0.54.0): `fastapi run` bật `proxy_headers=True`, `forwarded_allow_ips=None`
  (`fastapi_cli/cli.py:356-367`) → uvicorn đọc env `FORWARDED_ALLOW_IPS`, mặc định `127.0.0.1,::1`
  (`uvicorn/config.py:363`). Mình **không** đặt env này. Với `'*'` uvicorn lấy luôn phần tử đầu của XFF
  (`proxy_headers.py:176-177`); không thì đi từ phải sang trái, lấy IP đầu tiên không được tin. Ra phần tử đầu → _giả
  thuyết_: Render tự đặt `FORWARDED_ALLOW_IPS` (có thể `*`) — chưa kiểm được env trên Render.

Sau khi sửa:

| Thử                                     | Kết quả |
| --------------------------------------- | ------- |
| Laptop 7 lần qua Vercel (sau sửa, `327eca6`) | ✅ 13:16:38–13:16:51: #1–#5 `200`, #6 + #7 `429` `{"error":"Rate limit exceeded"}` + `Retry-After: 60` (qua được proxy Next). Trước sửa: 6 lần đều `200` |
| 2 máy → 2 bộ đếm riêng                  | ⏭️ Bỏ qua (user, 2026-10-26). Chưa chứng minh chặt: `429` ở lần 6 cũng có thể ra với code cũ nếu IP Vercel tình cờ không đổi |
| `curl` thẳng Render, IP giả, không key  | ✅ `X-Client-IP: 9.9.9.9`, không `X-API-Key` → `401` `{"detail":"Missing API Key"}` |
| pytest "2 IP không chung lượt"          | ✅ `test_rate_limit_counts_per_client_ip` (1.1.1.1: 5×200 rồi 429; 2.2.2.2 vẫn 200) + `test_client_ip_header_without_key_is_401` (IP giả không key → 401, không vào `_hits`). pytest 12/12, ruff / format / pyright sạch |

Sửa (Claude viết theo yêu cầu, user duyệt plan, 2026-10-26):

- `route.ts`: lấy IP đầu tiên trong `x-forwarded-for` → gửi FastAPI header riêng **`X-Client-IP`** (không có thì không
  gửi). Không chuyển nguyên `X-Forwarded-For`: sẽ phụ thuộc cách Render / uvicorn xử lý XFF (chưa rõ env trên Render).
- `rate_limit.py`: hàm `client_ip()` — `X-Client-IP` đúng dạng IP (`ipaddress.ip_address`, chuẩn hoá) → đếm theo nó;
  thiếu / sai dạng → về `req.client.host` như cũ. Bỏ `print` tạm.

- Vì sao tin được header IP từ Next mà không tin `X-Forwarded-For` từ trình duyệt:
  - Phía Next: Vercel **ghi đè** `x-forwarded-for` bằng IP client, không chuyển giá trị client tự gửi
    ([Request headers](https://vercel.com/docs/headers/request-headers)). Tự host Next thì **không** an toàn: Next chỉ
    điền khi thiếu (`??=`, `next/dist/server/base-server.js:567`) → client tự gửi là giả được.
  - Phía FastAPI: `dependencies=[Depends(verify_api_key), Depends(rate_limit)]` (`main.py:158`) → key sai / thiếu là
    `401` trước khi đếm → chỉ ai có `APP_API_KEY` (= Next server) mới đặt được `X-Client-IP` có tác dụng.
  - Thiếu header → đếm theo IP kết nối (local, test).
- `--forwarded-allow-ips` để làm gì, vì sao `'*'` nguy hiểm: danh sách IP proxy được tin để uvicorn đọc
  `X-Forwarded-For` làm IP client (mặc định `127.0.0.1,::1`, `uvicorn/config.py:363`). Với `'*'` uvicorn lấy **phần tử
  đầu** XFF (`proxy_headers.py:176-177`) — phần tử này do **người gửi đầu tiên** tự ghi → ai gọi thẳng cũng tự đặt IP
  được → né rate limit, ghi log sai IP. Không `'*'`: đi từ phải sang trái, dừng ở IP đầu tiên không phải proxy tin cậy.

## Bài A5 — README + GIF

- [x] `projects/p1-smart-copilot/README.md` (bản nháp tiếng Anh, Claude viết theo yêu cầu 2026-10-26, số liệu lấy từ
  notes Buổi 9–12; chỗ GIF đang comment lại) · ⏭️ GIF trong `docs/` · ⏭️ dọn `web/README.md`, `backend/README.md` (bỏ, user quyết định)
- [x] Trước khi quay GIF — bỏ **Markdown thô** (nợ Buổi 11). Chọn cách A (user): thêm vào `instructions` (`main.py`)
  "chỉ văn bản thường, không Markdown; liệt kê mỗi ý 1 dòng bắt đầu '- '". Cách B (render bằng `react-markdown`) không
  làm: thêm dependency. Kiểm local (backend thật + key local): "Thời tiết ở Hà Nội và HCM hôm nay" và "Top 3 sản phẩm
  bán chạy nhất?" → 0 dấu `*` / `#`, list bằng `- `. Đánh đổi: prompt không bảo đảm 100%, model vẫn có thể lỡ dùng.

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
