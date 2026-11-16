# Buổi 25 — Phase 02 Buổi 13: Project #2 (phần 1/3) — Kế hoạch + API chat streaming có citation (2h)

Phase 02 — RAG + Evals, Tuần 5 "Project #2 hoàn chỉnh + Framework + Rebuild test". Nguồn: Notion "Phase 02 — RAG +
Evals", page version 46 (Claude đọc 2026-11-16 qua `curl …/api/v3/loadPageChunk` — xem memory `phase02-notion-syllabus`).

Checklist Notion **Buổi 13–15** (2h × 3) — Project #2: Domain Knowledge Chatbot:

- Ghép thành **app hoàn chỉnh**: upload/ingest → **chat có citation** → **UI Next.js streaming** (tái dùng pattern
  Project #1)
- **Trang admin** nhỏ: xem chunks, chạy lại evals
- **Hỏi nối tiếp (multi-turn)**: viết lại câu hỏi dựa trên lịch sử hội thoại trước khi retrieve ("thế còn trường hợp
  kia?" → câu hỏi đầy đủ). Thêm **3–5 câu hỏi nối tiếp** vào eval set
- **Vòng đời tài liệu**: upload lại cùng `doc_id` → so `content_hash`, **chỉ re-embed khi đổi**; xoá tài liệu → **xoá hết
  chunks**. Trang admin: nút cập nhật/xoá. Test: hỏi nội dung tài liệu đã xoá → phải "không tìm thấy"

Buổi 17 (sau đó): README kiến trúc + bảng evals + **deploy demo** → thiết kế hôm nay phải tính tới deploy.

Claude kiểm trước (2026-11-16, đọc code, không gọi API):

| Hiện trạng | Bằng chứng |
| --- | --- |
| **Project #1 có sẵn pattern cần tái dùng**: FastAPI `POST /chat/stream` trả **SSE** (`delta` / `tool_result` / `done` / `error`), Next.js 16 **Route Handler làm proxy** (giữ API key phía server, không CORS), API key + rate limit, nút Stop huỷ tới tận OpenAI, log chi phí | `projects/p1-smart-copilot/README.md`, `backend/app/{main,sse,auth,rate_limit,cost_log}.py`, `web/app/api/chat/route.ts`, `web/lib/{sse,applyEvent}.ts` |
| P1 deploy: web **Vercel**, backend **Render free** (ngủ sau 15ph, dậy ~1ph) | P1 README |
| **Project #2 hiện chỉ là thư viện + script**: `rag.py` (417 dòng — retrieve/hybrid/rerank/guard/answer), `ingest.py`, `ingest_test.py`, `chunking.py`, `eval/run_eval.py`. **Chưa có** API, UI, upload | `ls projects/p2-labor-law-rag` |
| `answer()` gọi LLM **không stream** (`client.responses.create`, đợi cả câu) → cần thêm bản **stream** | `rag.py` `answer()` |
| Đã có sẵn cho citation: `cited` (`[n]` → heading), `chunks` (doc_id, chunk_index, heading, nội dung), `check_citations` | `rag.py`, `eval/run_eval.py` |
| Đã có `content_hash` (sha256) mỗi chunk + `ingest()` xoá theo `doc_id` rồi thêm lại (**luôn re-embed**) → vòng đời tài liệu mới làm một nửa | `chunking.py` `build_records`, `ingest.py` |
| Phân quyền theo `allowed_groups` đã chạy (leak 0/5) — app cần cách xác định **nhóm của người dùng** | `rag.py` `WHERE allowed_groups && %(groups)s` |
| DB **local** (`localhost:5433`), reranker `mmarco` (118M) chạy **local** → deploy cần Postgres + pgvector trên cloud và đủ RAM cho model | `.env` (đã che mật khẩu), `rag.py` `RERANKERS` |
| Thư mục `plans/` **chưa có**; skill `/ck:plan` **không có** trong danh sách skill của session này | `ls`, danh sách skill |

| Phần | Thời lượng | Làm ở đâu |
| --- | --- | --- |
| Setup: 5 quyết định kiến trúc | ~25ph | `notes.md` |
| Bài 1: viết **kế hoạch** Project #2 (3 buổi) → **user duyệt** | ~35ph | `plans/` |
| Bài 2: `answer_stream()` — bản stream của `answer()` | ~30ph | `rag.py` |
| Bài 3: API `POST /chat/stream` (SSE) + test bằng `curl` | ~30ph | thư mục app (Setup chọn) |

**Quy tắc (CLAUDE.md):** tính năng nhiều bước → **nghiên cứu → kế hoạch → user duyệt → mới code**. Làm từng bước nhỏ,
tự kiểm (edge case, lỗi, bảo mật), tóm tắt tác động sau mỗi thay đổi. **Không ghi DB** buổi này. **Không đổi hành vi**
cấu hình cuối Buổi 23 (eval phải ra số như cũ).

---

## Setup (~25ph) — 5 quyết định kiến trúc

- [ ] **Code app đặt ở đâu?** (a) **trong `projects/p2-labor-law-rag/`**: thêm `api/` (FastAPI) + `web/` (Next.js), dùng
      `rag.py` làm thư viện lõi — eval và app chạy **cùng 1 code**; (b) thư mục mới `projects/p2-chatbot/` copy từ P1. Gợi
      ý: (a) — eval đo đúng thứ chạy thật.
- [ ] **Backend**: (a) **FastAPI + SSE như P1** (chép `sse.py`, `auth.py`, `rate_limit.py`, `cost_log.py`); (b) Next.js
      gọi thẳng Postgres + OpenAI (bỏ Python) — mất reranker/underthesea (thư viện Python). Gợi ý: (a).
- [ ] **Sự kiện SSE**: gợi ý `sources` (top-5: số `[n]`, Điều, doc_id — gửi **trước** khi LLM chạy, UI hiện nguồn ngay)
      → `delta` → `done` (token, $, `guarded`, `cited`) / `error`. Câu bị guard chặn: `sources` + `done` không có `delta`
      văn bản LLM. Khác P1: không có `tool_call`.
- [ ] **Người dùng thuộc nhóm nào** (để lọc `allowed_groups`): (a) demo: **ô chọn nhóm** trên UI (`public` / `internal`)
      — đơn giản nhưng ai cũng tự chọn được `internal` → chỉ là demo; (b) mỗi nhóm 1 API key phía server → nhóm do
      **server quyết**, không do trình duyệt. Gợi ý: (b) nếu demo công khai; (a) nếu chỉ chạy local. ⚠️ Không được để
      trình duyệt tự gửi `groups` lên rồi tin luôn.
- [ ] **Deploy (Buổi 17) — chọn hướng sớm để không phải viết lại**: Postgres + pgvector cloud (Supabase / Neon / Render)
      và reranker 118M trên instance free (RAM?) — **chưa kiểm** giới hạn RAM / giá. Hôm nay chỉ cần: code đọc cấu hình
      từ biến môi trường, reranker **tắt được** bằng cấu hình.

## Bài 1 — Kế hoạch Project #2 (~35ph)

- [ ] Viết `plans/p2-chatbot.md`: chia 4 mục Notion vào 3 buổi, mỗi buổi có **đầu ra kiểm được**. Gợi ý chia:
  - **Buổi 25**: `answer_stream()` + API SSE (+ test `curl`)
  - **Buổi 26**: UI Next.js streaming + hiện citation (bấm `[n]` → xem đoạn luật) + upload/ingest + trang admin (xem
    chunks, chạy lại eval)
  - **Buổi 27**: multi-turn (viết lại câu hỏi theo lịch sử + 3–5 câu eval) + vòng đời tài liệu (`content_hash`, xoá) +
    test "hỏi tài liệu đã xoá → không tìm thấy"
- [ ] Ghi **rủi ro + câu hỏi mở** (ghi DB khi upload/xoá từ UI — ai được làm; thời gian nạp model reranker lúc khởi động
      API; chi phí embedding khi upload file lớn).
- [ ] ⏸ **Dừng — user duyệt kế hoạch** rồi mới sang Bài 2.

## Bài 2 — `answer_stream()` (~30ph)

- [ ] Tách phần **chung** của `answer()` (retrieve → rerank → guard → build_input) để `answer()` và `answer_stream()`
      **dùng chung** — không copy 2 bản logic (sửa 1 chỗ, eval vẫn đo đúng thứ app chạy).
- [ ] `answer_stream()` là generator: `sources` → từng `delta` (OpenAI Responses `stream=True`) → `done` (token, $,
      `cited`, `bad_cites`, `guarded`).
- [ ] Kiểm: chạy lại eval cấu hình cuối Buổi 23 trên vài câu (`only_ids`) → **cùng hành vi** như trước (câu trả lời có thể
      khác chữ do LLM, nhưng guard / từ chối / citation phải giữ).

Tự trả lời:

1. Vì sao gửi `sources` **trước** khi LLM trả lời? Được gì cho người dùng, có rủi ro gì (câu bị guard chặn thì sao)?

## Bài 3 — API `POST /chat/stream` (~30ph)

- [ ] FastAPI app (chỗ theo Setup): `GET /health`, `POST /chat/stream` (body: `question`) → SSE theo Setup.
- [ ] Nhóm người dùng theo Setup (**server quyết**), API key + rate limit chép từ P1.
- [ ] Nạp model reranker **1 lần lúc khởi động** (không phải mỗi request — Buổi 22: nạp ~13s).
- [ ] Test bằng `curl -N`: 1 câu có đáp án (thấy `sources` → `delta`… → `done`), 1 câu not_found (guard chặn, không
      `delta` LLM), 1 câu leak với nhóm `public` (không lộ).

Tự trả lời:

1. Vì sao nhóm người dùng phải do **server** quyết, không lấy từ request của trình duyệt?

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Bạn thiết kế luồng streaming cho chatbot RAG thế nào — sự kiện nào gửi khi nào, vì sao?
2. Làm sao đảm bảo bộ eval đo **đúng** code đang chạy trên production?
3. Phân quyền tài liệu trong RAG: lọc ở đâu, ai quyết định người dùng thuộc nhóm nào?
