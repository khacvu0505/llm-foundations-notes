# Buổi 21 — Phase 02 Buổi 9: Hybrid Search (2h)

Phase 02 — RAG + Evals, Tuần 4 "Cải tiến có đo lường". Nguồn: Notion "Phase 02 — RAG + Evals", page version 46 (Claude
đọc 2026-11-12).

Checklist Notion Buổi 9:

- **BM25/full-text** (Postgres `tsvector`) + **vector search**, trộn kết quả (**RRF**)
- **Đo lại** — thường cải thiện rõ với thuật ngữ / mã số / tên riêng tiếng Việt
- 📌 Postgres **không có** text search config tiếng Việt → dùng config **`simple`** (tách theo âm tiết) hoặc **tách từ
  trước** bằng `underthesea` / `pyvi`. **Đo cả 2 cách**, ghi số vào `eval-results.md` (kiểm chứng khi làm)

Claude kiểm trước (2026-11-13, read-only):

- `pg_ts_config` có 29 config (english, french, …, **simple**) — **không có vietnamese** ✅ đúng như Notion.
- Extension có sẵn trong image: **`unaccent`** 1.1, **`pg_trgm`** 1.6 (chưa cài) — `unaccent` giúp câu gõ không dấu.
- Postgres docs (textsearch-controls): `ts_rank` "Ranks vectors based on the frequency of their matching lexemes";
  "the ranking functions **do not use any global information**" → **không có IDF** → **không phải BM25 thật**: từ phổ
  biến ("người", "lao", "động") được tính ngang từ hiếm. `plainto_tsquery` nối các từ bằng **`&` (AND)** → câu hỏi dài
  dễ ra 0 kết quả.
- PyPI: `underthesea` **9.5.0** (2026-05-17, còn bảo trì); `pyvi` 0.1.1 (2021-06-30). Cài thử (`--dry-run`): cả hai
  **không** làm hạ phiên bản gói nào.

Nối với buổi trước: cấu hình tốt nhất **dieu-300 + rewrite** (từ chối nhầm 1/25, `fact_recall` 0.96, leak 0/5) nhưng
**dao động** giữa các lần chạy. Để đo **riêng** tác dụng của hybrid, so trên **dieu-300 không rewrite** (tất định hơn):
từ chối nhầm 4/25 (q05, q20, q23, q25), `fact_recall` 0.87.

| Phần                                                         | Thời lượng | Làm ở đâu                 |
| ------------------------------------------------------------ | ---------- | ------------------------- |
| Setup: chọn thư viện tách từ, chỗ lưu cột tìm từ khoá         | ~10ph      | `notes.md`                |
| Bài 1: full-text `simple` (cột + index, user chạy)             | ~25ph      | DB + `rag.py`             |
| Bài 2: RRF — trộn vector + từ khoá                            | ~25ph      | `rag.py`                  |
| Bài 3: tách từ tiếng Việt (`underthesea`) → cột thứ 2          | ~25ph      | `chunking.py` + DB        |
| Bài 4: đo 3 cấu hình (vector / hybrid simple / hybrid tách từ) | ~25ph      | `run_eval.py`             |

**Quy tắc DB:** thêm cột / index / cập nhật dữ liệu = **ghi DB** → user chạy. Claude chỉ `SELECT`.

---

## Setup (~10ph)

- [ ] Thư viện tách từ: `underthesea` (còn bảo trì, 2026) hay `pyvi` (2021)? Ghi lý do. `uv add` (user chạy).
- [ ] Thêm cột tìm từ khoá vào **`law_chunks_dieu300`** (cấu hình hiện tại) hay bảng mới? Gợi ý: thêm cột vào bảng hiện
      có — 2 cột `fts_simple`, `fts_seg` để so.

## Bài 1 — Full-text `simple` (~25ph)

- [ ] (User chạy) Cột sinh tự động + index GIN:

  ```sql
  ALTER TABLE law_chunks_dieu300
    ADD COLUMN fts_simple tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED;
  CREATE INDEX ON law_chunks_dieu300 USING gin (fts_simple);
  ```

- [ ] `keyword_search(conn, question, groups, k, table)`: câu hỏi → tsquery (**OR** các từ, không phải AND), xếp bằng
      `ts_rank_cd`, **luôn** lọc quyền như `retrieve`.
- [ ] Thử tay q13 ("Độ tuổi lao động tối thiểu là bao nhiêu?"): Điều 3 có lên đầu không? So với vector.

Tự trả lời:

1. Vì sao không dùng `plainto_tsquery` (AND) cho câu hỏi tự nhiên?
2. `ts_rank` không có IDF → hệ quả gì với tiếng Việt (từ "người", "lao", "động" có ở khắp nơi)? Xử lý thế nào (từ dừng,
   cụm từ)?

## Bài 2 — RRF (~25ph)

- [ ] `hybrid(conn, question, groups, k=5)`: lấy top-20 vector + top-20 từ khoá → mỗi chunk điểm
      `Σ 1/(60 + hạng)` → lấy top-5.
- [ ] Vì sao trộn theo **hạng** chứ không theo **điểm**? (Buổi 13: không so điểm giữa 2 model.)

## Bài 3 — Tách từ tiếng Việt (~25ph)

- [ ] `underthesea.word_tokenize(text, format="text")` → "người_lao_động" thành **1 từ**. Áp dụng cho **cả** nội dung
      chunk (lúc nạp) **và** câu hỏi (lúc tìm) — giống NFC ở Buổi 15.
- [ ] (User chạy) Cột `fts_seg tsvector` + script cập nhật từ nội dung đã tách từ + index GIN.
- [ ] Thử tay lại q13: tách từ giúp hay hại?

## Bài 4 — Đo 3 cấu hình (~25ph)

- [ ] Trên dieu-300, **không rewrite**: (a) vector (đã có: `runs/dieu-300.jsonl`), (b) hybrid `simple`, (c) hybrid
      tách từ → chấm code (từ chối nhầm/đúng, câu sai, `fact_recall`, **leak rate**).
- [ ] Câu nào tốt lên / tệ đi? Hybrid có giúp các câu "chữ chính xác" (Điều N, cụm thuật ngữ) như kỳ vọng không?
- [ ] Ghi `eval-results.md`.

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Hybrid search là gì, vì sao cần? Cải thiện bao nhiêu, đo bằng gì? (câu exit Phase 02)
2. RRF hoạt động thế nào, vì sao không cộng thẳng điểm?
3. Tìm kiếm từ khoá với tiếng Việt khó ở đâu?
