# Buổi 12 — Hoàn thiện Project #1 + REBUILD TEST (4h)

Đề bài: `exercises.md` cùng thư mục.

- [x] A1 chuẩn bị deploy (còn Q6 hard limit OpenAI) · [x] A2 backend Render · [x] A3 frontend Vercel (7/7; còn sửa
  dòng "đang khởi động" trong widget) · [ ] A4 IP thật · [ ] A5 README + GIF
- [ ] B Rebuild test

Link demo:

- Frontend (Vercel): https://llm-foundations-notes.vercel.app
- Backend (Render): https://llm-foundations-notes.onrender.com

## Handoff — dừng ở đây (2026-10-25)

_(Claude ghi để mở session mới trên máy khác. Đọc mục này trước, chi tiết từng bài ở dưới.)_

**Đang dừng ở**: Bài A3 — đã trả lời 3 câu chuẩn bị (Root Directory, env, vì sao không `NEXT_PUBLIC_`, xem mục A3),
**chưa tạo project Vercel**.

**Đã xong**:

- A1 Q1–Q5 (commit `0e2b5e8`, đã push): bỏ `CORSMiddleware` (`backend/app/main.py`); `/mock` → 404 ở prod
  (`web/app/mock/page.tsx` Server Component + `MockClient.tsx`).
- A2: backend chạy trên Render, đủ 6 test (health, stream từng mảnh, 401, 429, tool CSV, cold start 52.5s).
  Env trên Render: `OPENAI_API_KEY`, `APP_API_KEY`, `PYTHONUNBUFFERED=1`.

**Việc tiếp theo (theo thứ tự)**:

1. A3: Vercel → import repo, Root `projects/p1-smart-copilot/web`, env `BACKEND_URL` + `APP_API_KEY` (= giá trị
   prod trên Render) → Deploy → chạy bảng test A3.
2. A4: IP thật sau proxy (manh mối: log Render đã thấy IP thật qua `X-Forwarded-For`, xem Quan sát A2).
3. A5: README + GIF. 4. Phần B (ngày khác).

**Còn treo**:

- A1 Q6: chưa xác nhận `OPENAI_API_KEY` trên Render là key mới trong project riêng + hard limit → làm trước khi share link.
- Commit notes này (chưa commit lúc ghi handoff).

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
