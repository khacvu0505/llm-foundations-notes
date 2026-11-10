# Buổi 15 — Phase 02 Buổi 3: Ingestion Pipeline (2h)

Đề bài: `exercises.md` cùng thư mục.

- [ ] Setup · [ ] Bài 1 đọc DOCX + làm sạch · [ ] Bài 2 tài liệu internal giả · [ ] Bài 3 chunking 500/50 ·
  [ ] Bài 4 bảng + metadata · [ ] Bài 5 embed + lưu + search · [ ] 3 câu phỏng vấn

## Handoff — dừng ở đây (cập nhật 2026-11-10)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Khung buổi 15 vừa tạo.** Chưa làm bài nào.

**Việc tiếp theo**: Setup → `uv add python-docx` → chọn chỗ viết code → Bài 1.

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + mọi
lệnh **ghi DB**; notes tiếng Việt, có bảng + nguồn, mỗi câu phỏng vấn có "Câu nhớ".

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-10.)_

- Git: Buổi 14 đã commit (`e09cd26`), working tree sạch.
- DB: container `p2-pgvector` **Up**; bảng `chunks` (14 câu test, index HNSW) + `items` từ Buổi 14 — hôm nay tạo bảng
  mới cho dữ liệu thật, không đụng 2 bảng cũ.
- Dữ liệu: `projects/p2-labor-law-rag/data/raw/` có `18-VBHN-VPQH-2026.docx` (169 KB) + `.pdf` (2.3 MB). **Chưa có**
  `data/raw/internal/noi-quy-abc.md` (Bài 2).
- Thư viện: `python-docx` **chưa cài** (PyPI 1.2.0). Đã có `tiktoken`, `openai`, `psycopg`, `pgvector`.
- Giới hạn embedding (SDK `openai/types/embedding_create_params.py:15-25`): mỗi input ≤ 8192 token, mỗi request ≤
  2048 input và ≤ 300,000 token tổng.

## Setup

| Mục                         | Quyết định / kết quả |
| --------------------------- | -------------------- |
| `python-docx` đã cài        |                      |
| Code viết ở đâu + lý do     |                      |

## Bài 1 — Đọc DOCX + làm sạch

| Đo                          | Kết quả |
| --------------------------- | ------- |
| Số đoạn (thô / sau làm sạch) |         |
| Số Chương / Điều đếm được   |         |
| Đã bỏ những phần nào        |         |
| Còn rác không               |         |

- Vì sao làm sạch trước khi chunk:
- NFC vs NFD:

## Bài 2 — Tài liệu internal giả

| Mục                 | Nội dung |
| ------------------- | -------- |
| File                |          |
| Số token (cl100k)   |          |
| Dấu rò rỉ đã cài    |          |

## Bài 3 — Fixed-size chunking 500/50

| Đo                              | Kết quả |
| ------------------------------- | ------- |
| Số chunk bộ luật (ước ~213)     |         |
| Số chunk tài liệu internal      |         |
| Điều 25 có bị cắt không         |         |
| Có ký tự lỗi `�` không           |         |

- Overlap giải quyết gì, không giải quyết gì:
- Cắt giữa chữ tiếng Việt:
- Fixed-size hỏng ở đâu (bằng chứng cho Buổi 7):

## Bài 4 — Bảng + metadata

- Câu `CREATE TABLE`:
- Ràng buộc + lý do:
- `doc_id` với fixed-size chunk:
- Vì sao `allowed_groups` lấy từ tài liệu gốc:

## Bài 5 — Embed + lưu + search

| Kiểm                                          | Kết quả |
| --------------------------------------------- | ------- |
| Số dòng sau lần chạy 1 / lần chạy 2            |         |
| Chi phí embed thật (token)                     |         |
| "Thử việc tối đa bao lâu?" → top-3 có Điều 25? |         |
| Câu về thưởng: không lọc / lọc `public`        |         |

- Embed trước, xoá + insert trong 1 transaction:
- Idempotent:

## Câu phỏng vấn cuối buổi

### 1. Pipeline ingestion từ file gốc đến vector DB

### 2. Chọn chunk size + overlap; nhược điểm fixed-size

### 3. Metadata lưu kèm chunk
