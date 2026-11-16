# Buổi 25 — Phase 02 Buổi 13: Project #2 (phần 1/3) — Kế hoạch + API chat streaming có citation (2h)

Đề bài: `exercises.md` cùng thư mục.

- [ ] Setup · [ ] Bài 1 kế hoạch (user duyệt) · [ ] Bài 2 `answer_stream()` · [ ] Bài 3 API SSE · [ ] 3 câu phỏng vấn

## Handoff — dừng ở đây (cập nhật 2026-11-16)

_(Claude ghi để mở session mới — có thể ở **máy khác**. Đọc mục này trước.)_

**Khung buổi 25 vừa tạo** (2026-11-16). Chưa làm bài nào.

**Việc tiếp theo**: Setup (5 quyết định kiến trúc) → Bài 1 kế hoạch → **dừng chờ user duyệt** → Bài 2.

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
| Code app đặt ở đâu | |
| Backend | |
| Sự kiện SSE | |
| Nhóm người dùng (`allowed_groups`) | |
| Hướng deploy (Buổi 17) | |

## Bài 1 — Kế hoạch

- File kế hoạch:
- User duyệt: ⏸ chưa
- Câu hỏi mở:

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
