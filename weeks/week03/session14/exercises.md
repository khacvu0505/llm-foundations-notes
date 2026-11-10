# Buổi 14 — Phase 02 Buổi 2: Vector Database (pgvector) (2h)

Phase 02 — RAG + Evals (Tuần 3–5). Nguồn: Notion "Phase 02 — RAG + Evals" (đọc 2026-11-10).

Checklist Notion Buổi 2:

- Setup pgvector (Supabase free tier hoặc Postgres local) — chọn pgvector vì JD hay nhắc + tận dụng SQL sẵn có
- CRUD vectors, index (HNSW vs IVFFlat — hiểu trade-off ở mức nói được)
- (Đọc 20ph) Qdrant/Pinecone khác gì — đủ để trả lời "vì sao chọn pgvector"

Nối với Buổi 13: chọn model trước rồi mới tạo bảng (đổi model = đổi số chiều = embed lại hết). Hôm nay dùng
`text-embedding-3-small` → cột `vector(1536)`. Chưa nạp bộ luật — việc đó là Buổi 3 (ingestion).

| Phần                                          | Thời lượng | Làm ở đâu           |
| --------------------------------------------- | ---------- | ------------------- |
| Setup: chạy Postgres + pgvector               | ~20ph      | terminal            |
| Bài 1: CRUD bằng SQL với vector 3 chiều        | ~25ph      | `psql`              |
| Bài 2: Python + embedding thật (1536 chiều)    | ~35ph      | `exercises.py`      |
| Bài 3: Index HNSW vs IVFFlat                  | ~25ph      | `psql` + `notes.md` |
| Bài 4: Đọc — Qdrant/Pinecone vs pgvector      | ~20ph      | `notes.md`          |

**Quy tắc DB:** Claude **không** chạy lệnh ghi DB (`CREATE` / `INSERT` / `UPDATE` / `DELETE` / `DROP`), kể cả DB
local. User tự chạy; Claude chuẩn bị lệnh + output mong đợi, và chỉ chạy `SELECT` khi được nhờ.

---

## Setup — chạy Postgres + pgvector (~20ph)

- [ ] **Chọn chỗ chạy** (ghi lý do vào `notes.md`):

  | Lựa chọn               | Được                                         | Mất                                        |
  | ---------------------- | -------------------------------------------- | ------------------------------------------ |
  | **Docker local**       | Miễn phí, offline, xoá/làm lại dễ            | Phải bật Docker Desktop                    |
  | Supabase free tier     | Có sẵn pgvector, dùng lại khi deploy         | Cần tài khoản, qua mạng, giới hạn free tier |
  | Homebrew Postgres      | Máy đã có postgresql@17/18                   | Phải tự cài thêm extension pgvector        |

  Gợi ý: **Docker local** để học (Buổi 17 deploy mới tính Supabase). Image chính thức theo pgvector README:
  `pgvector/pgvector:pg18-trixie`.

- [ ] Bật Docker Desktop (Claude kiểm 2026-11-10: có `docker` 29.3.1 nhưng daemon **chưa chạy**).
- [ ] Chạy container (user tự chạy). Volume mount ở `/var/lib/postgresql` vì từ Postgres 18 image đổi `VOLUME` sang
      đó, `PGDATA` = `/var/lib/postgresql/18/docker` (https://hub.docker.com/_/postgres, Claude kiểm 2026-11-10):

  ```sh
  docker run -d --name p2-pgvector \
    -e POSTGRES_PASSWORD=dev -p 5433:5432 \
    -v p2-pgvector-data:/var/lib/postgresql \
    pgvector/pgvector:pg18-trixie
  ```

  Cổng `5433` để khỏi đụng Postgres Homebrew nếu sau này bật ở `5432`.

- [ ] Vào `psql`, bật extension, kiểm phiên bản:

  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  SELECT extversion FROM pg_extension WHERE extname = 'vector';
  ```

- [ ] Thêm `DATABASE_URL=postgresql://postgres:dev@localhost:5433/postgres` vào `.env` gốc repo (không commit).

---

## Bài 1 — CRUD bằng SQL với vector 3 chiều (~25ph)

Làm trong `psql`, vector nhỏ để nhìn bằng mắt được. Theo mục "Getting Started" / "Querying" của pgvector README.

- [ ] Tạo bảng `items (id bigserial PRIMARY KEY, embedding vector(3))`, thêm 3–4 dòng.
- [ ] Thử 3 toán tử: `<->` (L2), `<#>` (inner product **âm**), `<=>` (cosine **distance**). Mỗi cái
      `ORDER BY ... LIMIT 2`.
- [ ] `UPDATE` 1 vector, `DELETE` 1 dòng, thử `INSERT` vector sai số chiều (vd. 2 số vào `vector(3)`) → lỗi gì?

Tự trả lời:

1. Vì sao `<#>` trả về **số âm** của inner product? (README có giải thích — liên quan thứ tự sắp xếp của index.)
2. `<=>` là cosine **distance**. Đổi ra cosine **similarity** như Buổi 13 thế nào?
3. Với vector đã chuẩn hoá (OpenAI), 3 toán tử có cho **cùng thứ hạng** không? (Nối Buổi 13 câu phỏng vấn 2.) Nên
   dùng toán tử nào cho nhanh?

## Bài 2 — Python + embedding thật (~35ph)

- [ ] `uv add "psycopg[binary]" pgvector` (user tự chạy). Đọc README `pgvector-python` mục "Psycopg 3":
      `register_vector(conn)`, `Vector([...])`.
- [ ] Bảng `chunks (id, content text, embedding vector(1536))` (tên tự đặt).
- [ ] Embed 14 câu `BAI3_PAIRS` của Buổi 13 bằng `text-embedding-3-small` → `INSERT`.
- [ ] Query: embed câu hỏi "Thử việc được bao lâu?" → top-3 theo `<=>` → in câu + similarity.
- [ ] So với `cosine_similarity` tự viết ở Buổi 13 (tính trong Python) — có ra cùng số không?

Tự trả lời:

1. Không gọi `register_vector` thì sao (thử bỏ đi xem lỗi)?
2. Vì sao truyền vector qua tham số `%s` chứ không ghép chuỗi vào câu SQL?
3. Top-3 có hợp lý không? Câu nào lọt top mà không nên?

## Bài 3 — Index HNSW vs IVFFlat (~25ph)

- [ ] Đọc README mục "Indexing", "HNSW", "IVFFlat", "Filtering".
- [ ] `EXPLAIN` câu query Bài 2 → thấy `Seq Scan`. Tạo index HNSW (`vector_cosine_ops`) → `EXPLAIN` lại. Bảng chỉ
      14 dòng: planner có dùng index không? Vì sao? (Gợi ý: thử `SET enable_seqscan = off;` để ép.)
- [ ] Điền bảng so sánh HNSW vs IVFFlat trong `notes.md` (build, bộ nhớ, tốc độ/recall, cần data trước không,
      tham số chính).

Tự trả lời:

1. Không có index thì pgvector tìm **chính xác** (exact) hay **gần đúng** (approximate)? Thêm index thì đổi gì?
2. Index chỉ hỗ trợ tối đa bao nhiêu chiều với kiểu `vector`? `-3-small` (1536) và `-3-large` (3072) có index được
   không? Cách xử lý nếu cần large? (Nối Buổi 13: `dimensions`.)
3. README nói lọc `WHERE` với index gần đúng thì lọc **sau** khi quét index. Hệ quả gì cho **permission filter**
   `allowed_groups` (Buổi 8) — có thể trả về ít hơn `LIMIT` không?

## Bài 4 — Đọc: Qdrant / Pinecone vs pgvector (~20ph)

- [ ] Đọc nhanh trang chủ / docs Qdrant và Pinecone (tự tìm, ghi link).
- [ ] Điền bảng trong `notes.md`: loại (extension / DB riêng / dịch vụ cloud), chạy ở đâu, lọc metadata, hybrid
      search, chi phí, khi nào chọn.
- [ ] Viết 2–3 câu: "Vì sao Project #2 chọn pgvector?"

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. HNSW và IVFFlat khác nhau thế nào? Khi nào chọn cái nào?
2. Vì sao chọn pgvector mà không dùng vector DB riêng (Qdrant/Pinecone)?
3. Exact search vs approximate (ANN) search — đánh đổi gì? Khi nào chấp nhận mất recall?
