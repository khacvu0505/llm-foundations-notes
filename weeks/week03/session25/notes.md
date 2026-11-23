# Buổi 25 — Phase 02 Buổi 13: Project #2 (phần 1/3) — Kế hoạch + API chat streaming có citation (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 kế hoạch (bản 2 ✅) · ~~Bài 2 `answer_stream()`~~ · ~~Bài 3 API SSE~~ (thay bằng việc Buổi 25 của
  kế hoạch bản 2) · [x] 25.0 khung project `p2-chatbot` · [ ] 25.1 `chunking.py` · [ ] 25.2 `ingest.py` + bảng mới ·
  [ ] 25.3 `retrieve.py` vector · [ ] 3 câu phỏng vấn

## Handoff — dừng ở đây (cập nhật 2026-11-23)

_(Claude ghi để mở session mới — có thể ở **máy khác**. Đọc mục này trước.)_

**Đã đổi hướng**: Project #2 **viết mới toàn bộ** trong `projects/p2-chatbot/` (kế hoạch bản 2 `plans/p2-chatbot.md`,
user duyệt 2026-11-16) — 4 buổi 25–28. Bài 2–3 cũ (sửa `rag.py`) **bỏ**.

**Đã xong**: khung project `projects/p2-chatbot/` (uv app riêng, Python 3.12, 6 thư viện; Claude bỏ layout `src/` +
`build-system` theo yêu cầu user — cấu trúc app phẳng như P1 backend). **Chưa commit**: `plans/`, `projects/p2-chatbot/`,
notes này.

**Đang làm**: `rag/chunking.py` — file **đang trống** (0 byte). Claude giải thích từng hàm, user tự viết. Đã giải thích
hàm 1/4 `read_paragraphs` (đọc .docx → NFC → bỏ dòng rỗng; mong đợi **1377** dòng = 1415 − 38 rỗng). Tiếp: hàm 2
`group_by_dieu` → 3 `split_dieu` (≤ 300 token theo Khoản) → 4 `build_records` (+ `content_hash`). Mốc tự kiểm: bản cũ
**430 chunk luật, median 224 token**.

**Chạy**: `cd projects/p2-chatbot && uv run python -m rag.chunking` (cảnh báo `VIRTUAL_ENV` vô hại — `deactivate` .venv
gốc). Cần DB/OpenAI thì thêm `--env-file ../../.env`.

**Project #2 = 3 buổi** (repo session 25–27 = Notion Buổi 13–15). Buổi 17 deploy → thiết kế phải tính tới deploy.

**Máy khác**: DB local `localhost:5433`, `law_chunks_dieu300` **446 dòng** (thiếu 2 dòng test → user chạy
`ingest_test.py --write`).

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nói "write for me" — khi đó viết +
giải thích); user tự làm git + ghi DB; **tính năng nhiều bước → kế hoạch + user duyệt trước khi code** (CLAUDE.md);
notes tiếng Việt, có bảng + nguồn. Tải model treo → `HF_HUB_DISABLE_XET=1`. Đọc Notion: memory `phase02-notion-syllabus`.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-16.)_

- Git: Buổi 24 đã commit + push (`d861d4a`).
- Lõi RAG (cấu hình cuối Buổi 23): `rag.answer(…, table="law_chunks_dieu300", hybrid_column="fts_seg",
  rerank_model="mmarco", min_rerank=-1.5, prompt="delimiter")` — từ chối nhầm 1/27 (thật 2/27), từ chối đúng 5/5,
  leak 0/5, injection 0/2, 3.38 s/câu.
- Project #1 (tái dùng pattern): FastAPI SSE + Next.js 16 proxy, deploy Vercel + Render (`projects/p1-smart-copilot/`).

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Code app đặt ở đâu | **Trong `projects/p2-labor-law-rag/`**: thêm `api/` (FastAPI) + `web/` (Next.js), `rag.py` là thư viện lõi → eval và app chạy **cùng 1 code** |
| Backend | **FastAPI + SSE như P1** — chép `sse.py`, `auth.py`, `rate_limit.py`, `cost_log.py`; giữ được reranker `mmarco` + `underthesea` (thư viện Python) |
| Sự kiện SSE | **`sources` → `delta` → `done` / `error`**: `sources` (top-5: `[n]`, Điều, doc_id) gửi **trước** LLM → UI hiện nguồn ngay; `done` có token, $, `guarded`, `cited`. Câu bị guard chặn: `sources` + `done`, không có chữ LLM |
| Nhóm người dùng (`allowed_groups`) | **Server quyết qua API key**: mỗi nhóm 1 key phía server, Next.js proxy chọn key; trình duyệt **không** gửi `groups` → không ai tự chọn `internal` được |
| Hướng deploy (Buổi 17) | **Chưa chọn nhà cung cấp** (chưa kiểm RAM / giá). Hôm nay chỉ: mọi cấu hình đọc từ **biến môi trường**, reranker **tắt được** bằng cấu hình (Claude đặt mặc định an toàn, không hỏi user) |

## Bài 1 — Kế hoạch

- File kế hoạch: `plans/p2-chatbot.md` (Claude viết bản nháp 2026-11-16, sau khi đọc P1 `sse.py`, `auth.py`,
  `main.py`, `web/app/api/chat/route.ts` + `rag.py`)
- User duyệt: ✅ 2026-11-16 — đồng ý kế hoạch + 3 đề xuất (user ghi DB khi test, chỉ admin upload/xoá, Stop đồng bộ:
  chấp nhận + đo, async ở Buổi 26 nếu cần)
- Đổi cách làm (user chọn): `api/` + `web/` **user tự viết mới**, P1 chỉ để xem khi bí; `rag.py` giữ làm lõi. Lý do user
  hỏi: tưởng Project #2 là viết mới toàn bộ — Notion Buổi 13–15 ghi "**ghép** thành app… **tái dùng pattern** Project
  #1"; viết mới hoàn toàn là Buổi 18 (Rebuild test).
- **Đổi lần 2 (user chọn): thư mục mới `projects/p2-chatbot/`, viết mới toàn bộ kể cả lõi RAG.** → Kế hoạch **bản 2**
  (`plans/p2-chatbot.md`): 4 buổi (25–28), bảng mới trong DB, dùng lại file luật + `eval_set.jsonl` để đo lại. ✅ **User
  duyệt bản 2** ("viết lại từ đầu đi" — Claude hiểu là nhận cả 3 điểm: trùng Buổi 18, lõi mới phải đo lại, thêm 1 buổi).
  Bài 2–3 cũ của buổi này (`answer_stream`, API trên `rag.py`) **thay** bằng việc Buổi 25 trong kế hoạch bản 2.
- Câu hỏi mở (mục 4 kế hoạch): ai bấm ghi DB khi test upload/xoá · chỉ nhóm admin được upload/xoá · Stop có thể không
  dừng ngay (rag.py đồng bộ) · khởi động chậm (nạp model) · giới hạn cỡ file · eval từ admin chỉ bộ nhỏ · deploy chưa chọn

## Bài 2 — `answer_stream()`

- Phần dùng chung tách ra:
- Kiểm cùng hành vi (eval `only_ids`):
- Tự trả lời:

## Bài 3 — API `POST /chat/stream`

- File:
- Test `curl -N`: có đáp án __ · not_found __ · leak __
- Tự trả lời:

## Câu phỏng vấn cuối buổi

### 1. Luồng streaming cho chatbot RAG

### 2. Eval đo đúng code production

### 3. Phân quyền tài liệu trong RAG
