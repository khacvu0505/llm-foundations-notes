# Kế hoạch Project #2 — Chatbot tra cứu Bộ luật Lao động (viết mới toàn bộ)

_Claude viết 2026-11-16 (Buổi 25 Bài 1), **bản 2** — **✅ user duyệt 2026-11-16** ("viết lại từ đầu đi"); Claude
hiểu là nhận cả 3 điểm ở mục 4 (trùng Buổi 18, lõi mới phải đo lại, thêm 1 buổi). Async hay sync: quyết ở bước API._
_Trước đó: chờ duyệt. Nguồn yêu cầu: Notion Phase 02
Buổi 13–15 (v46)._

**Lịch sử quyết định (2026-11-16):**
- Bản 1 (user đã duyệt): app trong `projects/p2-labor-law-rag/`, dùng lại `rag.py`. User nhận 3 đề xuất: user ghi DB
  khi test · chỉ key admin upload/xoá · Stop đồng bộ chấp nhận + đo.
- User đổi: **thư mục mới, viết mới toàn bộ kể cả lõi RAG**; code cũ chỉ để xem lại khi bí. Claude gợi ý + review, viết
  hộ chỉ khi user nói "write for me". → Bản 2 (file này). 3 đề xuất trên **giữ nguyên**.

## 1. Mục tiêu

App hoàn chỉnh trong **`projects/p2-chatbot/`**: hỏi → trả lời **streaming** kèm **trích dẫn bấm được**, upload / cập
nhật / xoá tài liệu, trang admin, hỏi nối tiếp — **mọi dòng code viết mới**.

**Dùng lại (không phải code):** file luật gốc `p2-labor-law-rag/data/raw/`, **bộ eval** `eval_set.jsonl` (39 câu) để
**đo lại** lõi mới và so với bảng trong `ANALYSIS.md`.

**Ngoài phạm vi:** LangChain (Buổi 16), README + deploy thật (Buổi 17).

## 2. Kiến trúc

```
web/ (Next.js) ──/api/chat (proxy, giữ key)──▶ api/ (FastAPI) ──▶ rag/ (lõi mới) ──▶ Postgres + pgvector
     ◀──────── SSE: sources → delta… → done / error ◀──────────┘
```

| Thư mục | Nội dung | Ghi chú |
| --- | --- | --- |
| `projects/p2-chatbot/rag/` | `chunking.py`, `ingest.py`, `retrieve.py` (vector + từ khoá + RRF), `rerank.py`, `answer.py` (prompt, guard, `answer()` + `answer_stream()` dùng chung `prepare()`) | Viết mới. Cùng **thiết kế** đã chứng minh tốt (Điều/Khoản ≤ 300 token, hybrid, rerank, guard, delimiter) — đó là kiến thức, không phải chép code |
| `projects/p2-chatbot/api/` | FastAPI: `/health`, `/chat/stream`, `/docs` (upload/xoá), auth key → nhóm, rate limit | Viết mới |
| `projects/p2-chatbot/web/` | Next.js 16: chat streaming, citation, admin | Viết mới |
| `projects/p2-chatbot/eval/` | Script đo lại bằng `eval_set.jsonl` cũ (đọc file, không chép code chấm) | Viết mới |
| DB | **Bảng mới** (vd. `p2_chunks`) — không đụng bảng cũ → `ANALYSIS.md` vẫn tái hiện được | Tạo bảng + nạp = **user chạy** |

Nhóm người dùng: **server quyết** qua `API_KEYS_JSON` (key → nhóm, có nhóm `admin`). Cấu hình qua biến môi trường;
reranker tắt được.

## 3. Chia việc — ⚠️ cần 4 buổi, không phải 3

Viết lại lõi RAG ≈ 1 buổi thêm. Đề xuất mượn **1 buổi** (Notion có Buổi 16 LangChain + 17 Polish phía sau).

| Buổi | Việc | Đầu ra kiểm được |
| --- | --- | --- |
| **25** | Khung thư mục + `pyproject`/deps · `chunking.py` (Điều/Khoản) · `ingest.py` (embed + `content_hash`, ghi bảng mới) · `retrieve.py` vector | Chạy thử chunking không ghi DB (số chunk ≈ 430 luật) · **user** tạo bảng + nạp · `SELECT` đếm dòng · hỏi thử 3 câu thấy đúng Điều |
| **26** | Hybrid (từ khoá tách từ + RRF) · rerank · guard · prompt (citation Khoản, delimiter) · `answer()` + `answer_stream()` · **đo lại bằng eval** | Bảng: từ chối nhầm / `fact_recall` / leak / injection của lõi mới **so với** cấu hình cuối Buổi 23 |
| **27** | `api/`: `/chat/stream` SSE, auth key → nhóm, rate limit, `/docs` upload/xoá (chỉ admin) · `web/`: chat streaming + citation bấm được | `curl -N` đúng sự kiện · key public không lộ · UI chữ chạy dần, `[1]` mở đúng đoạn |
| **28** | Admin (xem chunk, chạy eval nhỏ) · multi-turn (`condense` + 3–5 câu eval) · vòng đời (so `content_hash`, chỉ embed chunk đổi, xoá → hết chunk) | Upload lại file không đổi → 0 lần embed · hỏi tài liệu đã xoá → `NOT_FOUND` · câu nối tiếp retrieve đúng |

## 4. Rủi ro + câu hỏi mở

1. **Trùng với Buổi 18 (Rebuild test)** — Buổi 18 cũng là "repo trắng → RAG trong 2h, không nhìn tài liệu". Viết lại
   bây giờ = luyện trước, nhưng Buổi 18 sẽ bớt "mới". → Chấp nhận?
2. **Lõi mới có thể ra số kém hơn** cấu hình cuối Buổi 23 (lỗi nhỏ khi viết lại) → đo lại ở Buổi 26 là bắt buộc; số kém
   thì so từng câu với run cũ để tìm chỗ lệch.
3. **Thêm 1 buổi** (25–28) → lịch Phase 02 lùi 1 buổi. → Đồng ý?
4. Giữ từ bản 1: ghi DB khi test = **user** chạy (Claude chỉ `SELECT`) · chỉ key **admin** upload/xoá · Stop đồng bộ:
   chấp nhận + đo (cân nhắc viết async ngay từ đầu vì đằng nào cũng viết mới) · khởi động chậm do nạp model · giới hạn cỡ
   file upload · eval từ admin chỉ bộ nhỏ · deploy chưa chọn.

## 5. Cách kiểm chung

- Mỗi bước có đầu ra kiểm được (bảng mục 3); mỗi thay đổi tự kiểm edge case / lỗi / bảo mật + tóm tắt tác động.
- **Mốc so sánh**: `p2-labor-law-rag/eval/runs/dieu300-final-cite-guard-delim.jsonl` (từ chối nhầm 1/27 — thật 2/27,
  từ chối đúng 5/5, `fact_recall` 0.95, leak 0/5, injection 0/2, 3.38 s/câu).
- Git + ghi DB: **user** làm; Claude chuẩn bị lệnh.
