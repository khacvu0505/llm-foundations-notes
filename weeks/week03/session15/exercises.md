# Buổi 15 — Phase 02 Buổi 3: Ingestion Pipeline (2h)

Phase 02 — RAG + Evals (Tuần 3–5). Nguồn: Notion "Phase 02 — RAG + Evals" (đọc 2026-11-10).

Checklist Notion Buổi 3:

- Đọc PDF/Markdown (pypdf/unstructured), làm sạch text
- Fixed-size chunking (500 token, overlap 50) — bản đơn giản nhất trước
  - 📌 Overlap chính là sliding window: cửa sổ 500 token trượt mỗi bước 450 token, để câu nằm ở ranh giới 2 chunk
    không bị mất ngữ cảnh
- Embed + lưu kèm metadata (nguồn, trang, mục, `doc_id`, `content_hash`, `allowed_groups`) — `allowed_groups` gán
  theo quyền tài liệu gốc (dữ liệu public thì tự chia 2 nhóm giả: public / internal), **không** để LLM tự đoán

Nối với buổi trước:

- Buổi 13: dữ liệu `projects/p2-labor-law-rag/data/raw/18-VBHN-VPQH-2026.docx` (~96k token cl100k → ước ~213 chunk,
  embed ≈ $0.002); kế hoạch tài liệu `internal` giả; `doc_id` + `content_hash` cho vòng đời tài liệu.
- Buổi 14: bảng `chunks` + `search()` trong `weeks/week03/session14/exercises.py`; 2 bài học mang sang hôm nay:
  **embed trước, xoá sau** và Điều 25 có **4 mức** thử việc (180/60/30/6 ngày) → chunk cắt ngang Điều là mất ý.

Dữ liệu của mình là **DOCX** (không phải PDF) → đọc bằng `python-docx` thay cho pypdf. Hôm nay làm **fixed-size**
đúng Notion; chunk theo Điều là việc của **Buổi 7 (Chunking nâng cao)** — hôm nay chỉ cần **thấy** chỗ fixed-size làm
hỏng.

| Phần                                              | Thời lượng | Làm ở đâu                         |
| ------------------------------------------------- | ---------- | --------------------------------- |
| Setup                                             | ~10ph      | terminal                          |
| Bài 1: đọc DOCX + làm sạch                         | ~25ph      | `exercises.py`                    |
| Bài 2: tài liệu `internal` giả                     | ~15ph      | `data/raw/internal/noi-quy-abc.md` |
| Bài 3: fixed-size chunking 500/50                  | ~25ph      | `exercises.py`                    |
| Bài 4: bảng mới + metadata                         | ~15ph      | `exercises.py` + `notes.md`        |
| Bài 5: embed + lưu (idempotent) + thử search       | ~30ph      | `exercises.py`                    |

**Quy tắc DB** (như Buổi 14): Claude **không** chạy lệnh ghi DB; user chạy script/SQL ghi. Claude chỉ chạy `SELECT`
khi được nhờ.

---

## Setup (~10ph)

- [ ] DB còn chạy: `docker ps --filter name=p2-pgvector` (tắt máy thì `docker start p2-pgvector`).
- [ ] `uv add python-docx` (user tự chạy) — PyPI `python-docx` 1.2.0 (Claude kiểm 2026-11-10).
- [ ] Tạo `weeks/week03/session15/exercises.py`. Tự quyết: viết ở đây (giống các buổi trước) hay viết thẳng vào
      `projects/p2-labor-law-rag/` để Project #2 dùng lại — ghi lý do vào `notes.md`.

---

## Bài 1 — Đọc DOCX + làm sạch (~25ph)

- [ ] Đọc file bằng `python-docx` → list đoạn văn (`doc.paragraphs`, mỗi đoạn có `.text`). In số đoạn, 10 đoạn đầu.
- [ ] Viết `clean(text) -> str`:
  - bỏ đoạn rỗng, gộp khoảng trắng thừa;
  - chuẩn hoá Unicode về **NFC** (`unicodedata.normalize`) — tiếng Việt có 2 cách mã hoá dấu (dựng sẵn vs tổ hợp),
    lệch là search "thử việc" không khớp "thử việc";
  - tự quyết bỏ phần nào: tiêu đề Công báo, phần "căn cứ", chú thích cuối trang… (xem 30 đoạn đầu rồi chọn).
- [ ] Kiểm: số **Chương** và **Điều** đếm được có khớp Buổi 13 (17 Chương, 220 Điều) không? Còn rác kiểu
      `<w:pgSz…>` như lần trích nhanh ở Buổi 13 không?

Tự trả lời:

1. Vì sao phải làm sạch **trước** khi chunk/embed? Rác lọt vào thì hỏng ở bước nào (token, embedding, câu trả lời)?
2. NFC vs NFD: thử `len("ệ")` với 2 dạng — khác gì? Ở đâu trong pipeline phải chuẩn hoá (lúc nạp, lúc hỏi, hay cả 2)?

## Bài 2 — Tài liệu `internal` giả (~15ph)

Theo kế hoạch Buổi 13 (`weeks/week03/session13/notes.md`, Bài 4):

- [ ] Viết `projects/p2-labor-law-rag/data/raw/internal/noi-quy-abc.md` — "Nội quy Công ty ABC (nội bộ) — **TÀI
      LIỆU GIẢ**", 2–3 trang: lương theo bậc, thưởng, quy trình kỷ luật.
- [ ] Cài **số lạ làm dấu rò rỉ** (vd. "thưởng 7,350,000đ", "mã KL-0429") — ghi danh sách dấu vào `notes.md` để Buổi 8
      test.
- [ ] Ghi rõ đầu file: toàn bộ là giả, không phải nội quy công ty thật.

Tự viết hoặc nhờ Claude viết nháp (nội dung giả, không phải trọng tâm buổi học).

## Bài 3 — Fixed-size chunking 500/50 (~25ph)

- [ ] Viết `chunk_tokens(text, size=500, overlap=50) -> list[str]` bằng `tiktoken` `cl100k_base` (tokenizer của
      `text-embedding-3-small`): encode → cắt cửa sổ 500, bước 450 → decode từng cửa sổ.
- [ ] Chạy trên bộ luật (đã làm sạch) và tài liệu internal. Bao nhiêu chunk? So với ước tính ~213 của Buổi 13.
- [ ] Tìm chunk chứa "Điều 25" → in ra. Điều 25 có bị **cắt đôi** không? 4 mức thử việc có nằm trọn 1 chunk không?
- [ ] In 2 chunk liền nhau → thấy phần **overlap** (50 token cuối chunk trước = 50 token đầu chunk sau).

Tự trả lời:

1. Overlap giải quyết vấn đề gì? Có giải quyết hết không (Điều 25 dài hơn 50 token thì sao)?
2. Decode từng cửa sổ token có thể cắt **giữa 1 chữ tiếng Việt** (1 chữ = nhiều token) — thấy ký tự lạ `�` không? Xử
   lý thế nào?
3. Fixed-size hỏng ở đâu với văn bản luật → ghi lại làm "bằng chứng" cho Buổi 7.

## Bài 4 — Bảng mới + metadata (~15ph)

- [ ] Thiết kế bảng (vd. `law_chunks` — tên tự đặt) cho dữ liệu thật. Gợi ý cột:

  | Cột              | Ý nghĩa                                                              |
  | ---------------- | -------------------------------------------------------------------- |
  | `id`             | khoá chính                                                           |
  | `doc_id`         | tài liệu gốc (vd. `bllđ-18-vbhn-2026`, `noi-quy-abc`)                 |
  | `chunk_index`    | thứ tự chunk trong tài liệu                                          |
  | `source`         | đường dẫn file gốc                                                   |
  | `heading`        | Chương/Điều ở đầu chunk (nếu bắt được) — thay cho "trang/mục" của PDF |
  | `content`        | text chunk                                                           |
  | `content_hash`   | SHA-256 của `content`                                                |
  | `allowed_groups` | `text[]`, vd. `{public}` hoặc `{internal}`                           |
  | `embedding`      | `vector(1536)`                                                       |

- [ ] Ràng buộc nào nên có (`UNIQUE (doc_id, chunk_index)`? `NOT NULL`?) — ghi lý do.

Tự trả lời:

1. Buổi 13 câu mẫu dùng `doc_id` theo **Điều** (`bllđ:dieu-112`). Với fixed-size chunk, `doc_id` nên là gì? Vì sao
   fixed-size làm việc "chỉ embed lại Điều bị sửa" khó hơn (gợi ý: sửa 1 Điều → các chunk phía sau **dịch chỗ**)?
2. Vì sao `allowed_groups` lấy từ **tài liệu gốc** chứ không để LLM đoán (Notion nhấn mạnh)?

## Bài 5 — Embed + lưu + thử search (~30ph)

- [ ] `embed_batch(texts)`: OpenAI giới hạn mỗi request ≤ **2048** input và ≤ **300,000** token tổng (SDK
      `embedding_create_params.py:15-25`) → ~213 chunk vừa 1 request, nhưng vẫn viết theo lô cho chắc.
- [ ] `ingest(conn, doc)`: **embed trước** → rồi trong **1 transaction**: xoá chunk cũ của `doc_id` + insert chunk mới
      (`with conn.transaction():`). Chạy lại 2 lần → số dòng không đổi?
- [ ] (Thêm nếu kịp) bỏ qua chunk có `content_hash` đã tồn tại → lần chạy thứ 2 không gọi OpenAI.
- [ ] Thử `search` với "Thử việc tối đa bao lâu?" (lọc `'public' = ANY(allowed_groups)`) → top-3 có chunk Điều 25
      không? Thử 1 câu về thưởng → chunk internal có hiện **khi không lọc** và **biến mất khi lọc** không?

Tự trả lời:

1. Vì sao embed **trước** rồi mới xoá + insert trong 1 transaction? Nếu OpenAI lỗi giữa chừng thì DB ra sao?
2. "Idempotent" nghĩa là gì? Vì sao pipeline ingestion cần idempotent?

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Mô tả pipeline ingestion của bạn từ file gốc đến vector DB. Bước nào dễ sai nhất?
2. Chunk size và overlap chọn thế nào? Fixed-size có nhược điểm gì với văn bản có cấu trúc?
3. Metadata nào bạn lưu kèm chunk, và mỗi cái dùng để làm gì?
