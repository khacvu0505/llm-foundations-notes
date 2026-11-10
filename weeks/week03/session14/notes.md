# Buổi 14 — Phase 02 Buổi 2: Vector Database (pgvector) (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 CRUD SQL · [x] Bài 2 Python + embedding thật · [x] Bài 3 Index HNSW vs IVFFlat ·
  [x] Bài 4 Qdrant/Pinecone · [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-10)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 14 xong** (2026-11-10). Container `p2-pgvector` (Postgres 18.6, pgvector 0.8.7, `127.0.0.1:5433`), bảng
`chunks` 14 câu test + index `chunks_embedding_hnsw`; bảng `items` (Bài 1). `exercises.py`: `get_conn` / `embed` /
`insert_chunks` / `search` (user viết, Claude gợi ý + review). Bài 1–4 + 3 câu phỏng vấn có trong notes (nhiều câu
mẫu Claude viết theo yêu cầu).

**Việc tiếp theo**: (1) user commit Buổi 14 + `pyproject.toml` / `uv.lock` (thêm `psycopg`, `pgvector`); (2) viết
`data/raw/internal/noi-quy-abc.md` (kế hoạch ở Buổi 13) trước Buổi 3; (3) **Buổi 15 = Phase 02 Buổi 3 — Ingestion**:
đọc DOCX → làm sạch → chunk 500/50 → embed → lưu kèm `doc_id`, `content_hash`, `allowed_groups`. Ghi nhớ từ Buổi 14:
**embed trước, xoá sau** (`insert_chunks` hiện xoá trước); chunk theo **cả Điều** (Điều 25 có 4 mức thử việc).
Mở lại DB: bật Docker Desktop → `docker start p2-pgvector`.

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + mọi
lệnh **ghi DB** (Claude chỉ chuẩn bị lệnh, chỉ chạy `SELECT` khi được nhờ); notes tiếng Việt, có bảng + nguồn, mỗi
câu phỏng vấn có "Câu nhớ".

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-10.)_

- Máy: `docker` 29.3.1 có, daemon **chưa chạy**. Homebrew có postgresql@12/14/15/17/18 (đều không chạy), **chưa**
  thấy pgvector cài qua Homebrew.
- `pyproject.toml` **chưa có** `psycopg` / `pgvector` → Bài 2 cần `uv add`.
- pgvector README (https://github.com/pgvector/pgvector, đọc 2026-11-10):
  - Toán tử: `<->` L2 · `<#>` inner product **âm** · `<=>` cosine distance · `<+>` L1. Cosine similarity =
    `1 - (embedding <=> ...)`.
  - Mặc định tìm **chính xác** (exact, recall hoàn hảo); thêm index HNSW / IVFFlat → **gần đúng** (ANN), đổi một
    ít recall lấy tốc độ, kết quả có thể khác.
  - Index giới hạn: `vector` tối đa **2,000 chiều**, `halfvec` 4,000, `bit` 64,000 → `-3-small` 1536 index được;
    `-3-large` 3072 thì không (trừ khi `halfvec` hoặc `dimensions`). _(Buổi 13 Claude ghi "~2000, chưa kiểm" — giờ
    đã kiểm.)_
  - Lọc `WHERE` với index gần đúng: lọc **sau** khi quét index → có thể ra ít dòng hơn `LIMIT` (cần iterative
    index scan từ 0.8.0).
  - Docker image: `pgvector/pgvector:pg18-trixie`.

## Setup

| Mục                       | Quyết định / kết quả (nguồn) |
| ------------------------- | ---------------------------- |
| Chạy ở đâu + lý do        | **Docker local** — miễn phí, offline, xoá/làm lại dễ; Supabase để Buổi 17 deploy (user chọn 2026-11-10) |
| Lệnh chạy container       | `docker run -d --name p2-pgvector -e POSTGRES_PASSWORD=dev -p 127.0.0.1:5433:5432 -v p2-pgvector-data:/var/lib/postgresql pgvector/pgvector:pg18-trixie`. Lần đầu chạy `-p 5433:5432` → mở `0.0.0.0` cho cả mạng (mật khẩu yếu) → chạy lại với `127.0.0.1` (Claude kiểm `docker ps`: `127.0.0.1:5433->5432/tcp`). Volume ở `/var/lib/postgresql` vì Postgres 18 đổi `VOLUME` (hub.docker.com/_/postgres). Log: PostgreSQL **18.6**, "ready to accept connections" |
| Phiên bản pgvector        | **0.8.7** (`SELECT extversion FROM pg_extension WHERE extname = 'vector'`) → ≥ 0.8.0 nên có **iterative index scan** (cần ở Buổi 8 khi lọc `allowed_groups`) |
| `DATABASE_URL` trong `.env` |                            |

## Bài 1 — CRUD bằng SQL

| Toán tử | Ý nghĩa | Kết quả với dữ liệu thử |
| ------- | ------- | ----------------------- |
| `<->`   | L2 — khoảng cách đường thẳng | **id 1** (0) → id 2, 4 hoà (1) → id 3 (1.414). id 2 cùng hướng nhưng bị phạt vì **dài hơn** |
| `<#>`   | inner product **âm** | **id 2** (−2) → id 1, 4 (−1) → id 3 (−0). id 2 **thắng cả id 1 giống hệt** vì inner product **thưởng độ dài** |
| `<=>`   | cosine distance = 1 − cos | **id 1, 2 hoà** (0) → id 4 (0.293 = 1 − cos45°) → id 3 (1). **Bỏ qua độ dài**, chỉ xét góc |

_(Dữ liệu: `[1,0,0]`, `[2,0,0]`, `[0,1,0]`, `[1,1,0]`; truy vấn `[1,0,0]`; số nhỏ hơn = gần hơn. Output thật user
chạy 2026-11-10.)_ → 3 toán tử cho **3 người thắng khác nhau** khi vector **chưa chuẩn hoá**.

- Lỗi khi chèn sai số chiều: `INSERT '[1,2]'` vào `vector(3)` → bị từ chối, không chèn gì (sau đó còn đúng 3 dòng id 1, 2, 4). Câu lỗi trong source pgvector: `"expected %d dimensions, not %d"` (`src/vector.c:78`, tag v0.8.1 — Claude đọc; user không dán câu lỗi thật). Ý nghĩa: đổi model (1536 → 3072/384) thì insert **báo lỗi ngay**, không lặng lẽ trộn vector không so được.
- **Vì sao `<#>` âm** _(câu mẫu Claude, user nhờ giải thích)_: inner product **càng lớn càng gần**, nhưng index Postgres
  chỉ quét **từ nhỏ đến lớn** (ASC). pgvector trả **số âm** (vd. 2, 1, 0 → −2, −1, −0) để "nhỏ nhất" = "gần nhất" →
  `ORDER BY embedding <#> q` đúng thứ tự **và dùng được index**. Giá trị thật: `(embedding <#> q) * -1`. (README:
  "Postgres only supports `ASC` order index scans on operators")
- **Cosine distance → similarity** _(user trả lời đúng)_: `1 - (embedding <=> q)` (README "Querying"). Kiểm: 1 − 0.293
  = 0.707 = cos45°. Similarity −1…1 → distance 0…2. **Sắp theo distance** (ASC, dùng index), similarity chỉ để hiển
  thị; `ORDER BY similarity DESC` có thể mất index (_suy luận_, Bài 3 kiểm bằng `EXPLAIN`).
- **Vector đã chuẩn hoá → toán tử nào** _(câu mẫu Claude)_: độ dài đều = 1 → 3 toán tử **cùng thứ hạng** (Bài 1 lệch
  chỉ vì độ dài khác nhau). Chọn **`<#>`** cho nhanh: cosine = a·b / (|a|·|b|) = a·b khi |a| = |b| = 1 → bỏ được phép
  tính độ dài. README: "If vectors are normalized to length 1 (like OpenAI embeddings), use inner product for best
  performance". Đánh đổi: nếu sau này đổi sang model **không** chuẩn hoá thì `<#>` xếp sai (thưởng vector dài) →
  `<=>` an toàn hơn. Index phải **khớp toán tử**: `<#>` ↔ `vector_ip_ops`, `<=>` ↔ `vector_cosine_ops`.

## Bài 2 — Python + embedding thật

| Hạng | Câu | Similarity (pgvector) | Cosine tự viết (Buổi 13) |
| ---- | --- | --------------------- | ------------------------ |
| 1    | Thử việc được bao lâu? (chính câu truy vấn) | **1.0000** | — (cùng 1 câu → 1.0) |
| 2    | Thời gian thử việc tối đa 60 ngày | **0.6087** | — (Buổi 13 không đo cặp này) |
| 3    | Thời gian thử việc không quá 60 ngày đối với công việc cần trình độ cao đẳng trở lên | **0.5553** | **0.5553** (Buổi 13 Bài 3, cặp "Câu hỏi ↔ đoạn") ✅ khớp 4 chữ số |

_(Truy vấn "Thử việc được bao lâu?", `<=>`, k=3, 14 câu `TEXTS`. Claude chạy `search()` read-only 2026-11-10.)_ #1 là
chính nó → kiểm tra nhanh "search chạy đúng". #2 câu **ngắn, gần chữ** thắng đoạn dài #3 dù #3 mới đúng hình dạng
RAG (đoạn luật dài) — cả hai đều đúng chủ đề. 11 câu khác chủ đề không lọt top 3.

- **Bỏ `register_vector` thì** _(user thử 2026-11-10)_: `psycopg.ProgrammingError: cannot adapt type 'Vector' using
  placeholder '%s' (format: AUTO)` — vỡ ở chiều **Python → DB**: psycopg không biết đổi object `Vector` thành giá trị
  SQL. `register_vector` dạy psycopg 2 chiều: gửi `Vector` (hoặc numpy array) vào DB và đọc cột `vector` ra thành object `Vector` (có `.to_numpy()`, float32) — theo source `pgvector/psycopg/vector.py:34-60`, `pgvector/vector.py:47`. Chiều đọc
  không bị chạm vì `search()` chỉ trả `content` + `similarity` (không có cột vector). _Giả thuyết, chưa thử:_ thiếu
  đăng ký mà `SELECT embedding` thì nhận về **chuỗi** `'[...]'` thay vì mảng số.
- **Vì sao dùng `%s`** _(câu mẫu Claude, user nhờ)_: (1) **An toàn** — giá trị gửi **tách riêng** khỏi câu SQL →
  text có `'` không làm vỡ câu, và user (Project #2) gõ `'; DROP TABLE chunks; --` cũng chỉ là chữ, không thành lệnh
  (chống **SQL injection**). (2) **Đúng kiểu** — psycopg + `register_vector` tự đổi `Vector` thành kiểu `vector`,
  không phải tự format 1536 số thành chuỗi. (3) **Nhanh hơn khi lặp lại** — câu SQL giữ nguyên, chỉ đổi giá trị →
  psycopg tự **prepare** câu chạy ≥ 5 lần (`prepare_threshold` mặc định 5, `psycopg/_connection_base.py:392-401`),
  Postgres khỏi phân tích lại.
- **Top-3 hợp lý không** _(user: "câu hỏi không nằm trong DB" ✅; phần còn lại câu mẫu Claude)_:
  - #1 = chính câu hỏi → **sản phẩm phụ của bài test** (RAG thật: DB chỉ chứa chunk tài liệu, câu hỏi embed lúc hỏi,
    không lưu). Vẫn có ích như phép kiểm tra: tìm chính nó phải ra 1.0.
  - #3 **tốt hơn** #2 vì có **điều kiện** ("cao đẳng trở lên"). Luật thật — **Điều 25** (18/VBHN-VPQH, Claude đọc DOCX)
    — có **4 mức**: ≤ 180 ngày (quản lý doanh nghiệp) · ≤ 60 ngày (cao đẳng trở lên) · ≤ 30 ngày (trung cấp, công
    nhân kỹ thuật, nhân viên nghiệp vụ) · ≤ 06 ngày làm việc (công việc khác); chỉ thử việc 1 lần cho 1 công việc.
    → trả lời "tối đa 60 ngày" (#2) là **sai một phần**.
  - #2 xếp cao hơn vì **ngắn + trùng chữ** với câu hỏi ngắn; đoạn dài chứa thêm ý ("cao đẳng trở lên") nên vector bị
    "pha" → similarity thấp hơn (_giả thuyết_, cách giải thích phổ biến).
  - Bài học: **điểm similarity cao ≠ câu trả lời tốt** → lấy top-k > 1, **chunk theo cả Điều** để giữ đủ 4 mức (Buổi 3,
    7), **rerank** (Buổi 10). Câu eval hay cho Buổi 5: "Thử việc tối đa bao lâu?" → đáp án phải nêu đủ 4 mức (Điều 25).

## Bài 3 — Index HNSW vs IVFFlat

| Tiêu chí              | HNSW | IVFFlat |
| --------------------- | ---- | ------- |
| Cấu trúc              | **Đồ thị nhiều tầng** ("multilayer graph") — ví von: tầng trên là đường cao tốc, tầng dưới là đường nhỏ, đi từ xa → gần | **Chia vector thành các nhóm (`lists`)**, chỉ tìm trong vài nhóm gần câu hỏi nhất — ví von: thư viện chia kệ, chỉ lục vài kệ |
| Thời gian build       | **Chậm hơn** | **Nhanh hơn** |
| Bộ nhớ                | **Nhiều hơn** (bài này: index 120 kB > 84 kB vector) | **Ít hơn** |
| Tốc độ / recall       | **Tốt hơn** ("better query performance… speed-recall tradeoff") | **Kém hơn** |
| Cần data trước không  | **Không** — "can be created without any data… there isn't a training step" | **Có** — "Create the index *after* the table has some data" (cần data để chia nhóm) |
| Tham số chính         | Build: `m` (16), `ef_construction` (64). Query: `hnsw.ef_search` (**40**) — cao hơn = recall tốt hơn, chậm hơn | Build: `lists` (bắt đầu `rows/1000` nếu ≤ 1M dòng, `sqrt(rows)` nếu > 1M). Query: `ivfflat.probes` (**1**), bắt đầu `sqrt(lists)` |

_(Nguồn: pgvector README mục "HNSW", "IVFFlat", "Query Options", Claude đọc 2026-11-10. Ví von "cao tốc / kệ sách"
là của Claude, không phải README. Câu mẫu Claude viết theo yêu cầu.)_

⚠️ **Bẫy HNSW:** kết quả bị giới hạn bởi `hnsw.ef_search` = **40** → `LIMIT 100` có thể chỉ ra ≤ 40 dòng; lọc `WHERE`
còn ra ít hơn (README: "Results are limited by the size of the dynamic candidate list… 40 by default"). Cách xử lý:
tăng `ef_search` hoặc bật **iterative index scan** (≥ 0.8.0, mình có 0.8.7).

**Chọn cho Project #2:** **HNSW** — tạo được khi bảng rỗng (pipeline ingestion tạo bảng + index trước, nạp sau), recall
tốt hơn; nhược điểm build chậm + tốn RAM không đáng kể với ~213 chunk.

- **`EXPLAIN` trước / sau index** _(user chạy trong DBeaver, 2026-11-10; truy vấn = vector dòng 13, `<=>`, LIMIT 3)_:

  | Lúc | Plan (đọc từ dưới lên) | Cost |
  | --- | --- | --- |
  | Chưa có index vector | `Seq Scan` (đọc hết) → `Sort` theo `embedding <=> …` → `Limit`. Dòng "Index Scan using chunks_pkey" chỉ là lấy vector dòng 13 theo `id` — **không phải** tìm vector. `rows=810` = planner đoán vì bảng mới chưa có thống kê | 38.76 |
  | Có HNSW (`chunks_embedding_hnsw`, `vector_cosine_ops`) | **Vẫn** `Seq Scan` + `Sort`, `rows=14` (CREATE INDEX cập nhật thống kê; bảng 14 dòng = **1 trang**) → planner chọn cách rẻ hơn | **2.54** |
  | Ép `SET enable_seqscan = off` | `Index Scan using chunks_embedding_hnsw` + `Order By: embedding <=> …` → **mất bước `Sort`** (index trả dòng theo thứ tự gần → xa) | **69.15** |

  → Với 14 dòng, đi index **đắt gấp ~27 lần** đọc thẳng → index chỉ đáng khi bảng lớn. Index HNSW **120 kB > 84 kB**
  dữ liệu vector (lưu bản sao vector + liên kết đồ thị) — Claude kiểm `\di+` read-only.
- **Exact vs approximate** _(user: "index chỉ giúp nhanh hơn; không index thì tìm gần đúng" → **ngược**; câu mẫu
  Claude)_: **không index = chính xác** (exact, so với **mọi** dòng — `Seq Scan` + `Sort` — "perfect recall").
  **Có index = gần đúng** (ANN: đi đồ thị/nhóm rồi dừng sớm → **nhanh hơn** nhưng **có thể bỏ sót** dòng gần nhất
  thật). Khác index thường (btree chỉ làm nhanh, kết quả y hệt): README "Unlike typical indexes, you will see
  different results for queries after adding an approximate index". Bù lại bằng `ef_search` / `probes`.
- **Giới hạn số chiều** _(câu mẫu Claude)_: index với `vector` tối đa **2,000** chiều (`halfvec` 4,000, `bit` 64,000 —
  README). `-3-small` **1536 → index được**; `-3-large` **3072 → không**. Nếu cần large, 3 cách:

  | Cách | Làm gì | Đánh đổi |
  | --- | --- | --- |
  | 1. `dimensions` (Buổi 13) | Gọi API với `dimensions=1536` (hoặc 1024) → cột `vector(1536)` | Mất một ít độ chính xác (docs: large cắt 256 vẫn hơn ada-002) |
  | 2. Index bằng `halfvec` | Giữ `vector(3072)`, index biểu thức `(embedding::halfvec(3072))` với `halfvec_cosine_ops`; query cũng phải ép kiểu `embedding::halfvec(3072) <=> …` (README "Half-Precision Indexing") | Số 2 byte thay vì 4 → index nhỏ một nửa, sai số làm tròn lớn hơn; quên ép kiểu khi query → không dùng index |
  | 3. Không index | Tìm chính xác (`Seq Scan`) | Chỉ ổn khi bảng nhỏ — bộ luật ~213 chunk là ổn |

  _(Cột 2: README chỉ có ví dụ `halfvec(3)` + `halfvec_l2_ops`; bản 3072 + cosine là Claude suy ra theo cùng mẫu,
  chưa chạy thử.)_
- **Lọc sau index → hệ quả cho `allowed_groups`** _(câu mẫu Claude)_: HNSW lấy tối đa **40 ứng viên** (`ef_search`)
  **rồi mới** lọc `WHERE`. README: "If a condition matches 10% of rows… only 4 rows will match on average". Vd. 90%
  chunk là `internal`, user `public` hỏi → 40 ứng viên còn ~4 → `LIMIT 5` ra **ít hơn 5**, tệ nhất **0** → RAG trả "không
  tìm thấy" dù có đoạn `public` đúng.
  - **Không rò rỉ** (lọc vẫn trong SQL, dòng `internal` không bao giờ lọt ra) — vấn đề là **mất recall**, không phải lộ
    dữ liệu. Rò rỉ chỉ xảy ra nếu lọc **ở code app sau khi lấy** hoặc quên lọc.
  - Cách xử lý (README "Filtering", "Iterative Index Scans"): (1) **iterative scan** `SET hnsw.iterative_scan =
    strict_order;` (≥ 0.8.0) → tự quét thêm tới khi đủ dòng; (2) **partial index** theo nhóm `... WHERE (...)` khi ít
    giá trị lọc; (3) **partitioning** khi nhiều giá trị; (4) index btree trên cột lọc → tìm **chính xác** khi điều
    kiện khớp ít dòng; (5) tăng `ef_search`. Bảng nhỏ (~213 chunk) không index thì **không gặp** bẫy này.
  - → Buổi 8: viết **test** "user public hỏi → đủ k kết quả, 0 dòng internal".

## Bài 4 — Qdrant / Pinecone vs pgvector

| Tiêu chí         | pgvector | Qdrant | Pinecone |
| ---------------- | -------- | ------ | -------- |
| Loại             | **Extension** của Postgres (thêm kiểu + toán tử + index vào DB sẵn có) | **Vector DB riêng**, client–server ("Qdrant operates in a client-server architecture") | **Dịch vụ search cho AI** ("a search engine for AI agents and applications") |
| Chạy ở đâu       | Mọi nơi chạy Postgres (mình: Docker local; Supabase khi deploy) | Open-source **tự host**, hoặc Managed / Hybrid / Private Cloud | **Cloud của Pinecone**; BYOC ("deploying in your own cloud account"). Trang overview **không** nói tự host trên máy mình |
| Lọc metadata     | SQL `WHERE` — với index HNSW thì **lọc sau** (bẫy 40 ứng viên) → cần iterative scan | Payload index, lọc **ngay trong lúc đi đồ thị HNSW** (theo trang overview) → không mắc bẫy "lọc sau" | Có ("Narrow results with metadata filters") |
| Hybrid search    | Tự ghép với full-text search của Postgres (README "Hybrid Search": RRF / cross-encoder) | Có sẵn: dense + sparse, BM25, SPLADE++/miniCOIL | Có sẵn: "hybrid search from one index" |
| Chi phí          | Miễn phí (open source), chỉ tốn máy chạy Postgres | Bản tự host miễn phí; cloud tính phí (_chưa kiểm bảng giá_) | Có gói free + trả theo dùng (_chưa kiểm bảng giá_) |
| Khi nào chọn     | **Đã dùng Postgres**, dữ liệu vừa (tới cỡ triệu dòng), muốn 1 DB cho cả dữ liệu + vector + quyền | Vector là **việc chính**, nhiều dữ liệu, lọc metadata nặng, cần hybrid có sẵn, muốn tự host | Không muốn tự vận hành gì, chấp nhận dữ liệu nằm trên cloud của họ |

_(Nguồn: https://qdrant.tech/documentation/overview/, https://docs.pinecone.io/guides/get-started/overview, pgvector
README — Claude đọc 2026-11-10. Trang filtering của Qdrant dài, Claude chưa đọc hết phần cơ chế lọc. "Khi nào chọn" là
tổng hợp của Claude.)_

- **Vì sao Project #2 chọn pgvector** — user: "vì db mình đang dùng Postgres, dùng pgvector cho tiện (extension của
  PostgreSQL)" ✅ đúng lý do chính. Câu mẫu đầy đủ (Claude bổ sung):

  > Chọn **pgvector** vì: (1) **đã dùng Postgres** → không thêm hệ thống mới để vận hành, backup, bảo mật; (2) **1 DB
  > cho cả** chunk, metadata (`doc_id`, `content_hash`, `allowed_groups`) và vector → lọc quyền là `WHERE`, cập nhật
  > tài liệu nằm trong **1 transaction** (xoá chunk cũ + thêm chunk mới cùng lúc); (3) **quy mô nhỏ** (~213 chunk) —
  > pgvector thừa sức, thậm chí chưa cần index; (4) SQL quen thuộc + JD hay nhắc (Notion). Đổi sang Qdrant khi
  > dữ liệu lên rất lớn hoặc lọc metadata nặng làm recall tụt.

## Câu phỏng vấn cuối buổi

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-10. Tập nói to mỗi câu ~30–40 giây.)_

### 1. HNSW vs IVFFlat

> **HNSW** = đồ thị nhiều tầng, đi từ xa lại gần → tìm **tốt hơn** (tốc độ/recall), nhưng **build chậm, tốn RAM**, và
> tạo được **khi bảng rỗng** (không cần "train").
>
> **IVFFlat** = chia vector thành `lists` nhóm, chỉ tìm trong vài nhóm gần nhất (`probes`) → **build nhanh, ít RAM**,
> nhưng recall kém hơn và phải tạo **sau khi có dữ liệu** (cần data để chia nhóm; _suy luận, chưa kiểm_: dữ liệu đổi nhiều sau khi build → nhóm lệch, recall giảm).
>
> Cả hai đều là **gần đúng**, có núm vặn recall: `hnsw.ef_search` (mặc định 40) / `ivfflat.probes` (mặc định 1).
> Project #2 chọn **HNSW**: pipeline tạo bảng + index trước rồi mới nạp, cần recall tốt; RAM không đáng kể với ~213
> chunk. Chọn IVFFlat khi dữ liệu rất lớn, ít thay đổi, RAM hạn chế, cần build nhanh.

Câu nhớ: **HNSW = đồ thị, tốt hơn, tốn hơn, tạo lúc rỗng được; IVFFlat = chia nhóm, rẻ hơn, cần data trước.**

**User trả lời thử (2026-11-10) → 2 chỗ nhầm hay gặp:**

| User nói | Sửa |
| --- | --- |
| "HNSW là đồ thị nhiều tầng giống LangGraph, quy trình từng bước" | **Cùng chữ "đồ thị", khác nghĩa.** LangGraph: node = **bước xử lý**, cạnh = "làm tiếp cái này" (workflow). HNSW: node = **vector/chunk**, cạnh = "**hai cái này gần nhau**" (bản đồ hàng xóm) |
| "IVFFlat dùng thuật toán kiểm cái nào gần nhất, tốc độ nhanh hơn" | Quá chung (cả hai đều tìm cái gần nhất). Ý chính: **chia vector thành nhóm** (`lists`) trước, khi tìm chỉ lục **vài nhóm** gần câu hỏi (`probes`). "Nhanh hơn" chỉ đúng với **build** + ít RAM; **tìm** thì kém HNSW (README) → nói "build nhanh hơn", đừng nói "tìm nhanh hơn" |

```
HNSW — mỗi chấm là 1 chunk, đường nối = "gần nhau"

Tầng 2 (ít điểm, nhảy xa):      A ─────────────── F
                                │                 │
Tầng 1 (nhiều hơn):             A ──── C ──── E ── F
                                │      │      │    │
Tầng 0 (tất cả chunk):          A─B─C─D─E─F─G─H─I─J
                                             ↑
                                        câu hỏi rơi gần đây
Tìm: vào ở tầng trên → nhảy về phía câu hỏi → xuống tầng dưới → nhảy tiếp → dừng
```

Ví von: tìm 1 địa chỉ — chạy **cao tốc** (tầng trên) → **đường lớn** → **hẻm nhỏ** (tầng 0) tới đúng nhà. (Hình +
ví von: Claude vẽ minh hoạ, không phải hình trong README.)

Câu của user, đã sửa:

> **HNSW** = đồ thị nối các **vector gần nhau**, nhiều tầng (cao tốc → đường nhỏ) → **tìm tốt hơn**, build chậm, tốn
> RAM, tạo được khi bảng rỗng. **IVFFlat** = **chia vector thành nhóm**, chỉ lục vài nhóm gần câu hỏi → **build
> nhanh, ít RAM**, nhưng tìm kém hơn và cần dữ liệu trước.

### 2. Vì sao pgvector mà không vector DB riêng?

_(User nêu được lý do chính — "đang dùng Postgres, pgvector là extension, cho tiện" ✅; ý 2–3 Claude bổ sung.)_

> (1) **Đã dùng Postgres** → pgvector chỉ là extension, **không thêm hệ thống mới** phải vận hành, backup, bảo mật.
>
> (2) **1 DB cho cả** text, metadata và vector → **lọc quyền** chỉ là `WHERE 'public' = ANY(allowed_groups)` ngay trong
> câu tìm; **cập nhật luật** (xoá chunk Điều cũ + thêm chunk mới) nằm trong **1 transaction** → không bao giờ có lúc
> DB chứa cả bản cũ lẫn bản mới. Với vector DB riêng: dữ liệu ở 2 nơi, phải tự giữ cho khớp.
>
> (3) **Quy mô nhỏ** (~213 chunk) → pgvector thừa sức. **Sẽ đổi** sang Qdrant/Pinecone khi: dữ liệu rất lớn (hàng chục
> triệu vector), lọc metadata nặng làm recall tụt (Qdrant lọc ngay khi đi đồ thị), hoặc cần hybrid search có sẵn.

| Ý | Nối với bài nào |
| --- | --- |
| Lọc quyền = `WHERE` | Buổi 8 (permission filter + leak test) |
| 1 transaction khi cập nhật | Buổi 13 câu "luật sửa đổi" (chunk cũ còn trong DB) |
| Khi nào đổi | Bài 3 câu 3 (bẫy lọc sau index), Bài 4 (bảng so sánh) |

Câu nhớ: **Đã có Postgres + 1 DB cho cả dữ liệu, quyền, vector + đủ cho quy mô nhỏ; to/lọc nặng mới đổi.**

### 3. Exact vs approximate (ANN) search

> **Exact** (không index): so câu hỏi với **mọi** dòng (`Seq Scan` + `Sort`) → **luôn đúng** (recall hoàn hảo), nhưng
> chậm dần **tỉ lệ thuận** với số dòng.
>
> **ANN** (có index HNSW/IVFFlat): đi đồ thị/nhóm rồi **dừng sớm** → **nhanh hơn nhiều** khi bảng lớn, nhưng **có thể
> bỏ sót** vài dòng gần nhất thật. Núm vặn: `ef_search` / `probes` (tăng = đúng hơn, chậm hơn).
>
> **Chấp nhận mất recall khi:** (1) bảng **lớn**, exact quá chậm; (2) đã **đo** recall đủ cao (so kết quả có index với
> không index trên bộ câu eval); (3) lấy **top-k rộng** (vd. 20) rồi **reranker/LLM** chọn lại → sót 1 dòng trong
> nhiều dòng tốt thường không sao.
>
> **Không nên khi:** bảng **nhỏ** (exact vẫn nhanh — bộ luật ~213 chunk: dùng exact), hoặc lọc `WHERE` khớp ít dòng
> (bẫy "lọc sau index").

Cách đo recall của index (dùng ở Buổi 6 / Buổi 10, _đề xuất của Claude_): chạy cùng bộ câu hỏi 2 lần — `SET
enable_indexscan = off` (exact) và bình thường (ANN) → recall@k = số dòng trùng / k.

Câu nhớ: **Exact = so hết, luôn đúng, chậm khi lớn; ANN = dừng sớm, nhanh, có thể sót → chỉ dùng khi lớn + đã đo
recall + có rerank.**
