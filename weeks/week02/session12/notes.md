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
| `fastapi dev` vs `fastapi run`            |                      |
| CORS `origins` còn cần không              |                      |
| `logs/cost.jsonl` trên Render             |                      |
| File phải / không được có trong git       |                      |
| `pnpm build && pnpm start`: stream, `/mock` |                    |
| Key prod + giới hạn chi tiêu OpenAI       |                      |

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
