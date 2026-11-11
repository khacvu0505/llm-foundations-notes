# Buổi 15 — Phase 02 Buổi 3: Ingestion Pipeline (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 đọc DOCX + làm sạch · [x] Bài 2 tài liệu internal giả · [x] Bài 3 chunking 500/50 ·
  [x] Bài 4 bảng + metadata · [x] Bài 5 embed + lưu + search · [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-10)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 15 xong** (2026-11-11). `exercises.py` (user viết, Claude gợi ý + review): `read_docx` → `clean_paragraphs`
(NFC, bỏ phần đầu) → `chunk_tokens` 500/50 (decode bỏ mảnh vỡ) → `build_records` (heading mang theo, sha256, groups)
→ `embed_batch` (lô 100) → `ingest` (embed trước, 1 transaction xoá + thêm theo `doc_id`) → `search` (lọc nhóm tuỳ
chọn). Bảng `law_chunks`: **216 dòng** (luật 210 `{public}` + nội quy 6 `{internal}`), idempotent đã kiểm. Tài liệu
giả `data/raw/internal/noi-quy-abc.md` (Claude viết nháp) + danh sách dấu rò rỉ ở Bài 2.

**Việc tiếp theo**: (1) user commit Buổi 15 + `pyproject.toml` / `uv.lock` (thêm `python-docx`) +
`projects/p2-labor-law-rag/data/raw/internal/`; (2) **Buổi 16 = Phase 02 Buổi 4 — Naive RAG end-to-end**: câu hỏi →
**NFC** → embed → top-k (lọc `allowed_groups`) → prompt yêu cầu trích nguồn (`heading`) → "không tìm thấy" khi thiếu
context.

**Để dành cho Project #2 / Buổi 7** (ghi lại từ buổi này): cột `embedding_model`; bước dọn `doc_id` không còn file
gốc; bỏ qua embed khi `content_hash` đã có; tiêu đề `**Điều N.**` trong file markdown chưa bắt được (heading rỗng);
chưa đo `usage` token thật khi ingest; chỉ 1 lần nạp chạy cùng lúc (lock); chunk theo Điều/Khoản + gắn tiêu đề.
Mở lại DB: bật Docker Desktop → `docker start p2-pgvector`.

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
| `python-docx` đã cài        | ✅ `python-docx>=1.2.0` (user `uv add`, 2026-11-11). Import tên là `docx`; `docx.Document()` khai báo nhận `str` → dùng `str(path)` cho pyright |
| Code viết ở đâu + lý do     | `weeks/week03/session15/exercises.py` (mặc định — user chưa chọn; Claude gợi ý: học ở đây, Project #2 mới chuyển phần tốt sang `projects/p2-labor-law-rag/`) |

## Bài 1 — Đọc DOCX + làm sạch

| Đo                          | Kết quả |
| --------------------------- | ------- |
| Số đoạn (thô / sau làm sạch) | **1415 → 1367** (`read_docx` + `clean_paragraphs`, user viết; Claude chạy read-only 2026-11-11) |
| Số Chương / Điều đếm được   | **17 Chương, 220 Điều** — khớp Buổi 13 ✅ (regex `^Chương [IVXLC]+$`, `^Điều \d+\.`) |
| Đã bỏ những phần nào        | 38 đoạn rỗng; **phần đầu** (quốc hiệu, tên văn bản, danh sách 3 luật sửa đổi, "Căn cứ…") — cắt từ "Chương I" đầu tiên (chỉ xuất hiện 1 lần). Bảng xác thực của VPQH (số hiệu, chữ ký) nằm trong `doc.tables` nên `doc.paragraphs` **tự bỏ qua** |
| Còn rác không               | Không thấy rác XML (khác lần trích bằng regex ở Buổi 13). File gốc **không** có đoạn NFD (đếm 0) — NFC vẫn giữ vì câu hỏi của user có thể là NFD. Đoạn cuối: Điều 220 "Hiệu lực thi hành" |

- **Vì sao làm sạch trước khi chunk** _(user: "tránh dữ liệu phình to" → đúng 1 phần; câu mẫu Claude bổ sung)_:
  **rác vào → rác ra**, hỏng dây chuyền qua cả 4 bước:

  | Bước | Rác làm hỏng gì |
  | --- | --- |
  | **Token / chunk** | Rác **chiếm chỗ** trong 500 token (100 token rác → còn 400 token luật); tốn tiền embed (ý "phình to" của user) |
  | **Embedding** | Vector bị **kéo lệch** về phía rác → không còn đại diện đúng nghĩa đoạn luật |
  | **Retrieval** | Chunk rác (vd. toàn quốc hiệu, `<w:pgSz…>`) có thể **lọt top-k**, đẩy đoạn đúng ra ngoài |
  | **Câu trả lời** | LLM đọc rác trong context → trả lời lạc đề, **trích nguồn sai**, tốn context |

  Thêm: làm sạch **1 lần ở đầu** rẻ hơn sửa ở cuối; và **đổi cách làm sạch** sau này → text đổi → `content_hash` đổi
  → phải **embed lại** → nên chốt bước làm sạch sớm.
- **NFC vs NFD** _(user chạy: `False 1 3`; giải thích + đo thêm: Claude, 2026-11-11)_:
  - "ệ" **NFC** = 1 ký tự dựng sẵn (U+1EC7). **NFD** = 3 ký tự: `e` + dấu nặng (U+0323) + dấu mũ (U+0302). Nhìn **giống
    hệt**, nhưng máy so từng mã → **khác nhau**.
  - Đo với câu "Thời gian thử việc tối đa bao lâu?" (NFC vs NFD):

    | Đo | NFC | NFD |
    | --- | --- | --- |
    | Số ký tự | 34 | 43 |
    | Số token (cl100k) | 20 | **32** |
    | SHA-256 giống nhau? | — | **Không** |
    | `"thử" in text` | — | **False** |
    | Cosine giữa 2 embedding (`-3-small`) | — | **0.3511** (!) |

  - Hệ quả: câu hỏi NFD → vector **lệch hẳn** (0.35, gần mức "không liên quan" của Buổi 13) → search trượt; keyword
    search (Buổi 9) không khớp; `content_hash` khác → cùng nội dung bị coi là chunk mới → embed lại / trùng.
  - **Chuẩn hoá ở cả 2 đầu:** lúc **nạp** (trước chunk, trước hash) và lúc **hỏi** (trước embed câu hỏi, trước keyword
    search). NFD hay đến từ đâu: copy từ PDF/web, vài bộ gõ/hệ điều hành (_kiến thức chung, chưa kiểm_).

## Bài 2 — Tài liệu internal giả

| Mục                 | Nội dung |
| ------------------- | -------- |
| File                | `projects/p2-labor-law-rag/data/raw/internal/noi-quy-abc.md` — "Nội quy lao động Công ty ABC (nội bộ) — TÀI LIỆU GIẢ" (**Claude viết nháp theo yêu cầu**, 2026-11-11). 5 chương / 14 điều: thử việc nội bộ, thang lương bậc, thưởng, giờ làm + làm thêm + phép bổ sung, kỷ luật. Đầu file ghi rõ **toàn bộ là giả** |
| Số token (cl100k)   | **2,422 token** (978 từ) → ~5–6 chunk 500/50 |
| Dấu rò rỉ đã cài    | Xem danh sách bên dưới |

**Dấu rò rỉ (Buổi 8 test: user `public` hỏi → câu trả lời KHÔNG được chứa chuỗi nào sau đây):**

| Nhóm | Chuỗi |
| --- | --- |
| Mã tài liệu / quy trình / mẫu | `ABC-INT-2026-07`, `KL-0429`, `BB-KL-03`, `ĐG-TV-11`, `OT-77`, `REF-ABC-58`, `VP-A1`…`VP-D4` |
| Bậc lương | `BL-11`, `BL-13`, `BL-15`, `BL-17`, `BL-19` |
| Số tiền | `11.640.000`, `15.280.000`, `19.870.000`, `26.430.000`, `34.910.000`, `7.350.000`, `3.920.000`, `5.610.000`, `1.180.000`, `265.000`, `430.000` |
| Hệ số / tỷ lệ lạ | `1,37`, `1,75`, `2,2`, `3,1`, `92%`, `95%`, `1,15 tháng`, `28 giờ/tháng`, `"ABC Care"` |

**Câu hỏi "bẫy" cố ý trùng chủ đề luật** (dùng cho Buổi 8): thử việc (nội quy 45/75 ngày vs luật Điều 25), làm thêm
giờ (nội quy hệ số 1,75 vs luật Điều 98 "ít nhất bằng 150%" — Claude kiểm DOCX), nghỉ phép, kỷ luật lao động → user
`public` hỏi các chủ đề này phải chỉ nhận đoạn **luật**, không nhận đoạn nội quy.

## Bài 3 — Fixed-size chunking 500/50

| Đo                              | Kết quả |
| ------------------------------- | ------- |
| Số chunk bộ luật (ước ~213)     | **210** (text sạch 94,524 token; ước 213 ở Buổi 13 tính trên text chưa sạch 95,759). Chunk cuối 474 token |
| Số chunk tài liệu internal      | **6** (2,422 token) |
| Điều 25 có bị cắt không         | **Có.** Tiêu đề "Điều 25. Thời gian thử việc" nằm **cuối chunk 23**; thân điều (đủ 4 mức 180/60/30/06 ngày) nằm ở **chunk 24 — không có chữ "Điều 25"** → chunk trả lời đúng nhưng **không trích được số Điều**; chunk 24 còn dính sang Điều 26 |
| Có ký tự lỗi `�` không           | **Có: 8 chunk**, mỗi chunk 1 ký tự `�` — cửa sổ token cắt **giữa 1 chữ** (1 chữ Việt có dấu = nhiều byte/nhiều token) |

_(Code `chunk_tokens` user viết; số đo Claude chạy read-only 2026-11-11.)_ Chunk cũng bắt đầu/kết thúc **giữa chữ**:
chunk 0 hết ở "trường hợp qu", chunk 1–3 mở đầu bằng `' sử dụng lao độ'`, `'p pháp, đại diệ'`, `', tôn giáo, tín'`.

- **Overlap giải quyết gì, không giải quyết gì** _(user: "đoạn trùng giữa 2 chunk, đảm bảo không bị mất info" →
  định nghĩa đúng, nhưng "đảm bảo" là quá; câu mẫu Claude)_:
  - **Giải quyết:** ý **ngắn hơn 50 token** nằm đúng ranh giới → vẫn nằm **trọn** trong ít nhất 1 chunk.
  - **Không giải quyết:** ý **dài hơn overlap** bị cắt. Điều 25 dài **347 token** (Claude đo) ≫ 50 → tiêu đề ở chunk 23,
    thân ở chunk 24, không chunk nào có **trọn** "Điều 25 + 4 mức". Overlap cũng không biết ranh giới **ý nghĩa**
    (Điều/Khoản) — chỉ đếm token mù.
  - Tăng overlap (vd. 200) đỡ hơn nhưng **tốn hơn** (nhiều chunk trùng → nhiều token embed, top-k chứa nội dung lặp)
    và vẫn không đảm bảo → cách gốc là cắt theo **cấu trúc** (Buổi 7).
- **Cắt giữa chữ tiếng Việt → `�`** _(câu mẫu Claude, user nhờ)_:
  - **Vì sao:** UTF-8 lưu chữ có dấu bằng **nhiều byte** ("ệ" = 3 byte `E1 BB 87`). Tokenizer cl100k làm việc trên
    **byte**, nên 1 token có thể chỉ chứa **một phần** của 1 chữ. Cửa sổ cắt giữa các byte đó → `decode()` gặp mảnh
    byte không thành chữ → thay bằng `�` (tiktoken `decode(..., errors="replace")` mặc định, `tiktoken/core.py:275`).
  - **Ví dụ thật (chunk 63):** "ĐỘNG" — "Ộ" = `E1 BB 98`; token trước giữ `E1 BB`, token đầu chunk 63 chỉ có `\x98` →
    chunk mở đầu bằng `'�NG TẬP THỂ'`.
  - **Cách sửa:** (1) bỏ mảnh vỡ: `ENC.decode_bytes(window).decode("utf-8", errors="ignore")` — mất nửa chữ ở mép,
    nhưng nhờ **overlap** chữ đó vẫn còn nguyên ở chunk bên cạnh; (2) dời điểm cắt về **ranh giới đẹp** (xuống dòng
    `\n` gần nhất trong cửa sổ) → không vỡ chữ, không cắt giữa câu — bước đầu của chunk theo cấu trúc (Buổi 7).
  - Ảnh hưởng: 1 ký tự rác/chunk làm vector lệch rất ít, nhưng hiện ra **xấu** khi trích dẫn cho user.
- **Fixed-size hỏng ở đâu — bằng chứng cho Buổi 7** _(câu mẫu Claude, user nhờ)_:

  | Lỗi | Bằng chứng (Buổi 15) | Hệ quả |
  | --- | --- | --- |
  | Cắt đôi 1 Điều | Điều 25: tiêu đề ở chunk 23, 4 mức ở chunk 24 | Không chunk nào trả lời trọn |
  | Mất "địa chỉ" | Chunk 24 không có chữ "Điều 25" | LLM **không trích được nguồn** |
  | Trộn 2 Điều | Chunk 24 dính sang Điều 26 | Vector "pha" 2 ý, LLM dễ lẫn |
  | Vỡ chữ / cắt giữa câu | 8 chunk có `�`; chunk mở đầu `'p pháp, đại diệ'` | Trích dẫn xấu, nhiễu nhẹ |

  Độ dài 220 Điều (Claude đo, cl100k): **min 51 · median 353 · max 3,682** token; **70 Điều > 500**, 10 Điều < 100.
  → "1 Điều = 1 chunk" **chưa đủ**: Điều dài phải chia tiếp theo **Khoản**, và mỗi chunk **gắn tiêu đề** "Điều N.
  Tên điều" ở đầu (để trích nguồn được); Điều quá ngắn có thể gộp. Đó là việc của Buổi 7 — làm xong **đo lại** bằng eval
  set (Buổi 5–6) để biết có tốt hơn thật không.

## Bài 4 — Bảng + metadata

- **Câu `CREATE TABLE`** _(Claude soạn, user chạy)_:

  ```sql
  CREATE TABLE IF NOT EXISTS law_chunks (
    id             bigserial PRIMARY KEY,
    doc_id         text    NOT NULL,
    chunk_index    int     NOT NULL,
    source         text    NOT NULL,
    heading        text,
    content        text    NOT NULL,
    content_hash   text    NOT NULL,
    allowed_groups text[]  NOT NULL CHECK (cardinality(allowed_groups) > 0),
    embedding      vector(1536) NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    UNIQUE (doc_id, chunk_index)
  );
  CREATE INDEX IF NOT EXISTS law_chunks_content_hash_idx ON law_chunks (content_hash);
  ```

- **Ràng buộc + lý do** _(câu mẫu Claude, user nhờ)_:

  | # | Quyết định | Lý do |
  | --- | --- | --- |
  | 1 | **Giữ** `UNIQUE (doc_id, chunk_index)` | Lỡ chạy ingest 2 lần mà quên xoá → **báo lỗi to** thay vì nhân đôi chunk âm thầm (search ra trùng). Sau này dùng được `ON CONFLICT … DO UPDATE` (upsert) |
  | 2 | **Thêm** `CHECK (cardinality(allowed_groups) > 0)` | `{}` mơ hồ: "ai cũng xem" hay "không ai xem"? Code quên gán nhóm → insert **thất bại** thay vì lặng lẽ rò rỉ/ẩn mất. Nguyên tắc **fail closed** (lỗi thì chặn, không mở) |
  | 3 | **Không** UNIQUE `content_hash`, chỉ **index thường** | Cùng 1 đoạn text có thể hợp lệ ở 2 tài liệu (nội quy trích nguyên văn luật). Index thường đủ để tra nhanh "hash này có chưa?" (bỏ qua embed lại — Bài 5) |

  Kiểm (Claude `\d law_chunks` read-only, 2026-11-11): đủ 10 cột, `law_chunks_pkey`, `law_chunks_content_hash_idx`,
  `law_chunks_doc_id_chunk_index_key` (UNIQUE **tự tạo index btree**), `law_chunks_allowed_groups_check`; 0 dòng.

  Thêm `created_at` để biết chunk nạp lúc nào (debug vòng đời tài liệu). Vector index (HNSW) **chưa tạo**: 216 dòng thì
  tìm chính xác vẫn nhanh (Buổi 14).
- **`doc_id` với fixed-size chunk** _(câu mẫu Claude, user nhờ)_:
  - `doc_id` = **cả tài liệu** (`bllđ-18-vbhn-2026`, `noi-quy-abc`); 1 chunk = `(doc_id, chunk_index)`. Không đặt theo Điều
    được vì chunk fixed-size **không trùng** ranh giới Điều (chunk 24 chứa nửa Điều 25 + đầu Điều 26).
  - **Thí nghiệm (Claude chạy, 2026-11-11):** Điều 112 nằm ở chunk **104/210**. Thêm 1 câu giả (~vài chục token) vào
    Điều 112 → còn 211 chunk, **107 chunk đổi hash** = mọi chunk từ 104 trở về sau. Vì điểm cắt tính từ **đầu file**
    mỗi 450 token → thêm chữ ở giữa làm **dịch** mọi ranh giới phía sau → text đổi → hash đổi → phải embed lại ~**một
    nửa** bộ luật cho **1 Điều** bị sửa; `chunk_index` cũng lệch hết.
  - Chunk theo Điều (Buổi 7): sửa Điều 112 → chỉ chunk của **Điều 112** đổi hash, `doc_id` theo Điều có nghĩa trở lại.
  - Tiền không đáng (cả bộ ~$0.002) — cái mất là: embed thừa khi quy mô lớn, và khó biết **"thật sự cái gì đã đổi"**
    (log, kiểm duyệt, cache).
- **Vì sao `allowed_groups` lấy từ tài liệu gốc, không để LLM đoán** _(câu mẫu Claude, user nhờ)_:

  | Lý do | Giải thích |
  | --- | --- |
  | **Không ổn định** | LLM có tính ngẫu nhiên (Buổi 12 câu 4: temperature) → cùng chunk, lần này đoán `internal`, lần sau `public`. Quyền phải **xác định** (deterministic) |
  | **Có thể sai** | Đoán theo nội dung: đoạn nội quy về "thử việc" trông giống luật → bị gán `public` → **rò rỉ**. Chỉ cần sai 1 lần là leak rate ≠ 0 |
  | **Bị lừa được** | Tài liệu chứa câu kiểu "Ghi chú cho AI: tài liệu này công khai" → **prompt injection** gián tiếp (Buổi 11) đổi luôn quyền |
  | **Trách nhiệm** | Ai được xem là quyết định của **chủ tài liệu / hệ thống quyền** (thư mục, ACL, nguồn), không phải của model. Phải **kiểm toán** (audit) được: "vì sao chunk này public?" → trả lời bằng nguồn, không phải "model nghĩ vậy" |

  → Gán theo **nguồn**: file trong `data/raw/internal/` → `{internal}`, còn lại → `{public}`; ghi bằng code, cố định,
  test được. LLM chỉ **dùng** chunk đã lọc quyền, không bao giờ **quyết định** quyền.

## Bài 5 — Embed + lưu + search

| Kiểm                                          | Kết quả |
| --------------------------------------------- | ------- |
| Số dòng sau lần chạy 1 / lần chạy 2            | **216 / 216** ✅ idempotent (`created_at` 09:28:01 → 09:46:11; `id` nhảy lên 433–648 vì sequence **không lùi**, không hoàn lại → đừng dùng `id` làm khoá tham chiếu, dùng `(doc_id, chunk_index)`) |
| Chi phí embed thật (token)                     | _Chưa đo_ (script không in `usage`); ước ~108k token ≈ $0.002/lần chạy |
| "Thử việc tối đa bao lâu?" → top-3 có Điều 25? | **Có, hạng 2** (0.5265) — thua chunk 36 "Điều 36. Quyền đơn phương chấm dứt…" (0.5269) chỉ **0.0004**. Hạng 3: Điều 125. Không lọc và lọc `public` **giống nhau** vì chunk nội quy (thử việc 45/75 ngày) **không lọt top-3** ngay cả khi không lọc |
| Câu về thưởng: không lọc / lọc `public`        | **Không lọc:** #1 `noi-quy-abc` chunk 2 (0.494), #2 `noi-quy-abc` chunk 1 (0.417), #3 luật Điều 90. **Lọc `public`:** cả 2 chunk nội quy **biến mất** → Điều 90, 103, 96 ✅ bộ lọc chặn đúng |

_(User chạy `search()`, 2026-11-11.)_ Quan sát thêm:
- Chunk nội quy **đứng đầu** câu thưởng là chunk 2 (nâng bậc, "1 bậc") — **không phải** chunk chứa 7.350.000; chunk
  fixed-size trộn nhiều chủ đề (lương + nâng bậc + thưởng) → vector "pha" → xếp hạng lệch.
- Similarity lệch nhẹ giữa 2 lần gọi cùng câu (0.52688 vs 0.52678) — embedding API không tất định tuyệt đối (giống
  Buổi 13 Bài 1).
- Điều 25 chỉ hơn/thua chunk khác ~0.0004 → retrieval thô **mong manh**; cần eval set (Buổi 5) để đo thay vì nhìn bằng mắt.

- **Embed trước, xoá + insert trong 1 transaction** _(câu mẫu Claude, user nhờ)_:

  | Thứ tự | Lỗi ở… | User tìm **ngay lúc đó** thấy gì |
  | --- | --- | --- |
  | **A** (kiểu Buổi 14): xoá → embed → thêm | OpenAI lỗi ở lô 2 | **Bảng rỗng** cho tài liệu đó → "không tìm thấy" cho mọi câu về luật, tới khi chạy lại thành công |
  | **B** (hôm nay): embed → `transaction { xoá → thêm }` | OpenAI lỗi ở lô 2 | **Bản cũ nguyên vẹn** — lỗi xảy ra **trước** khi đụng DB, chưa xoá gì |
  | **B** | INSERT lỗi ở dòng 150 | **Bản cũ nguyên vẹn** — transaction **rollback** cả DELETE lẫn 149 dòng đã thêm |

  Ngoài ra trong lúc transaction đang chạy, người khác vẫn thấy **bản cũ** (chưa commit thì chưa ai thấy thay đổi) → không
  bao giờ có lúc "nửa cũ nửa mới" hay "không có gì". Quy tắc: **bước chậm/dễ lỗi (mạng, API) làm trước, ngoài
  transaction; bước ghi DB gom vào 1 transaction ngắn.** Transaction ngắn còn đỡ giữ khoá DB lâu.
- **Idempotent** _(câu mẫu Claude, user nhờ)_: chạy **1 lần hay N lần** với cùng đầu vào → DB ở **cùng 1 trạng thái**.
  Đã chứng minh: lần 1 → 216 dòng, lần 2 → vẫn 216.

  | Pipeline bị chạy lại khi… | Không idempotent | Idempotent (delete + insert theo `doc_id`) |
  | --- | --- | --- |
  | Cron mỗi đêm nạp lại | Mỗi đêm **+216 dòng** → sau 1 tuần mỗi chunk có 7 bản → top-k toàn bản trùng | Luôn 216 |
  | Retry sau sự cố | Lần lỗi để lại **nửa** dữ liệu + lần retry thêm đủ → trùng 1 phần | Lần lỗi rollback, retry ra đúng |
  | Bấm "nạp lại" 2 lần | Gấp đôi | Không đổi |

  Vì sao cần: ngoài đời pipeline **chắc chắn** sẽ bị chạy lại (lịch, retry, thao tác tay) → phải **an toàn khi chạy
  lại** thì mới dám tự động hoá và dám retry. Cách làm hôm nay: khoá theo `doc_id` + xoá-rồi-thêm trong 1 transaction +
  `UNIQUE (doc_id, chunk_index)` làm lưới an toàn. Bước sau (Project #2): bỏ qua chunk có `content_hash` đã có → chạy
  lại **không tốn** tiền embed.

  Câu nhớ: **Idempotent = chạy lại bao nhiêu lần kết quả cũng như chạy 1 lần.**

## Câu phỏng vấn cuối buổi

### 1. Pipeline ingestion từ file gốc đến vector DB

_(User: "chia chunk → clean data → embedding → lưu vector db" → đúng các khối chính nhưng **sai thứ tự** (clean phải
**trước** chunk) và thiếu đọc file, metadata, cách lưu an toàn. Câu mẫu Claude bổ sung, 2026-11-11.)_

```
① Đọc file (python-docx)  → ② Làm sạch (NFC, khoảng trắng, bỏ phần đầu)  → ③ Chunk 500/50 (tiktoken cl100k)
→ ④ Metadata (doc_id, chunk_index, heading, content_hash, allowed_groups theo nguồn)
→ ⑤ Embed theo lô (NGOÀI DB)  → ⑥ 1 transaction: DELETE chunk cũ của doc_id + INSERT chunk mới  → ⑦ Kiểm (đếm, search)
```

> Pipeline của mình: đọc DOCX bằng python-docx → **làm sạch trước** (NFC, gộp khoảng trắng, bỏ phần đầu văn bản) →
> chunk 500 token, overlap 50 bằng tokenizer của model embedding → gắn **metadata** (`doc_id`, `heading`,
> `content_hash`, `allowed_groups` lấy theo **nguồn**, không để LLM đoán) → **embed trước, ngoài DB** → **1
> transaction** xoá bản cũ + thêm bản mới theo `doc_id` → chạy lại bao nhiêu lần cũng ra 216 dòng (**idempotent**).
>
> **Dễ sai nhất:** (1) **làm sạch / chuẩn hoá** — sai 1 lần là hỏng mọi bước sau, và lỗi **im lặng** (NFD làm cosine
> tụt còn 0.35 mà không báo lỗi gì); (2) **gán quyền** — sai là **rò rỉ**. Cả hai đều không "crash", nên phải có
> kiểm tra/test riêng.

Câu nhớ: **Đọc → sạch → cắt → gắn nhãn → embed (ngoài DB) → thay trong 1 transaction; dễ sai nhất là làm sạch và gán
quyền vì lỗi im lặng.**

### 2. Chọn chunk size + overlap; nhược điểm fixed-size

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-11.)_

| Chunk | Được | Mất |
| --- | --- | --- |
| **Nhỏ** (vd. 200 token) | Vector **sắc** (1 ý), trích chính xác | Thiếu ngữ cảnh, ý dài bị cắt vụn, nhiều chunk hơn |
| **Lớn** (vd. 1000 token) | Đủ ngữ cảnh | Vector **bị pha** nhiều ý (Buổi 14: câu ngắn thắng đoạn dài), tốn context LLM (top-k × size) |

> Chọn chunk size theo **4 ràng buộc**: (1) giới hạn model embedding (8192 token/input); (2) **mật độ ý** của tài liệu
> — muốn mỗi chunk ~1 ý trọn; (3) **ngân sách context** của LLM: top-k × size phải vừa prompt; (4) **đo bằng eval**:
> thử vài cỡ (200 / 500 / 1000) trên bộ câu hỏi thật, chọn cỡ có recall tốt nhất — không chọn bằng cảm giác. Mình bắt
> đầu từ **500/50** (overlap 10%) làm baseline. Overlap thường ~10–20% (_kinh nghiệm phổ biến, chưa kiểm nguồn_).
>
> **Fixed-size với văn bản có cấu trúc** cắt **mù** theo token: Điều 25 (347 token) bị **cắt đôi** — tiêu đề chunk 23,
> nội dung chunk 24 → **mất số Điều** để trích dẫn; 1 chunk **trộn 2 Điều**; **vỡ chữ** tiếng Việt (`�`); sửa 1 câu ở
> Điều 112 làm **107/211 chunk** đổi hash. Nhưng "1 Điều = 1 chunk" cũng chưa đủ (median 353, **70 Điều > 500**, dài
> nhất 3,682) → cắt theo **Điều**, Điều dài chia theo **Khoản**, mỗi chunk **gắn tiêu đề Điều** (Buổi 7) — rồi **đo
> lại**.

Câu nhớ: **Size = cân giữa "sắc" và "đủ ngữ cảnh", chọn bằng eval; fixed-size cắt mù → cắt đôi Điều, mất trích dẫn,
sửa 1 Điều đổi nửa bộ → cắt theo cấu trúc.**

### 3. Metadata lưu kèm chunk

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-11.)_

| Metadata | Dùng để |
| --- | --- |
| `doc_id` | Gom chunk theo tài liệu → **thay/xoá cả tài liệu** 1 lần (idempotent) |
| `chunk_index` | Thứ tự chunk; cùng `doc_id` làm **khoá ổn định** (`id` đổi sau mỗi lần nạp); lấy chunk **hàng xóm** khi cần thêm ngữ cảnh |
| `source` | Truy ngược **file gốc** (kiểm toán, link cho user) |
| `heading` | **Trích nguồn** "theo Điều 25" — kể cả khi chunk không chứa chữ đó (mang tiêu đề theo) |
| `content` | Text cho LLM đọc — vector **không đổi ngược** ra chữ được |
| `content_hash` | Phát hiện **thay đổi** → chỉ embed lại phần đổi; kiểm trùng |
| `allowed_groups` | **Lọc quyền** ngay trong SQL (`WHERE`) → leak rate = 0; gán theo **nguồn**, không để LLM đoán |
| `embedding` | Tìm theo nghĩa |
| `created_at` | Biết chunk nạp lúc nào → debug vòng đời tài liệu |
| _Nên thêm:_ `embedding_model` | Tránh trộn vector của 2 model cùng số chiều |
| _Nên thêm:_ `effective_from` | Luật có ngày hiệu lực khác nhau theo Điều (Buổi 13) |

> Mỗi chunk lưu: **`doc_id` + `chunk_index`** (tài liệu nào, vị trí nào — để thay cả tài liệu và làm khoá ổn định),
> **`source`** (truy ngược file), **`heading`** (trích "theo Điều 25"), **`content_hash`** (biết cái gì đổi, khỏi embed
> lại), và quan trọng nhất **`allowed_groups`** — lọc quyền ngay trong SQL, gán theo nguồn chứ không để LLM đoán. Nếu
> làm tiếp sẽ thêm `embedding_model` để không trộn vector của 2 model, và `effective_from` vì luật có ngày hiệu lực khác
> nhau.

Câu nhớ: **Mỗi metadata trả lời 1 câu hỏi: của tài liệu nào (`doc_id`), ở đâu (`chunk_index`, `heading`), đổi chưa
(`content_hash`), ai được xem (`allowed_groups`).**
