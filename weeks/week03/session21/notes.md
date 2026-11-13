# Buổi 21 — Phase 02 Buổi 9: Hybrid Search (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 full-text simple · [x] Bài 2 RRF · [x] Bài 3 tách từ · [x] Bài 4 đo 3 cấu hình ·
  [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-13)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 21 xong** (2026-11-13). `law_chunks_dieu300` thêm cột `fts_simple` (sinh tự động) + `fts_seg` (điền bằng
`add_fts_seg.py`), 2 index GIN. `rag.py`: `keyword_search` (IDF tự tính bằng `ts_stat`, lọc quyền), `rrf`,
`hybrid_retrieve`, `answer(…, hybrid_column)`; `chunking.segment_text` (underthesea, nối liền vì bẫy `_`). Kết quả (37
câu, không rewrite): vector 4/27 → **hybrid tách từ 3/27**, `fact_recall` 0.88 → 0.89, leak 0/5; sửa q05 không cần rewrite,
hỏng q02 (k=5 bị chiếm).

**Việc tiếp theo**: (1) user commit Buổi 21 (`weeks/week03/session21`, `projects/p2-labor-law-rag/{rag,chunking,
add_fts_seg}.py`, `projects/p2-labor-law-rag/eval/`, `pyproject.toml`, `uv.lock`); (2) **Buổi 22 = Phase 02 Buổi 10 —
Reranking**: lấy top-20 → reranker (Cohere Rerank API hoặc cross-encoder local) → top-5; đo + **latency/cost** tăng bao
nhiêu. Mục tiêu rõ: q24 (Buổi 20) và q02 (Buổi 21) — đoạn đúng có trong top-20 nhưng bị đẩy khỏi top-5.

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + `uv add`
+ mọi lệnh ghi DB; mỗi lần đo đổi 1 thứ; notes tiếng Việt, có bảng + nguồn.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-13.)_

- Git: Buổi 20 đã commit (`89500a1`). DB `p2-pgvector` Up.
- Postgres: **không có** text search config tiếng Việt (29 config, có `simple`); có sẵn `unaccent` 1.1, `pg_trgm` 1.6.
- Postgres docs: `ts_rank`/`ts_rank_cd` **không dùng thông tin toàn cục** (không IDF) → không phải BM25 thật;
  `plainto_tsquery` = AND.
- `underthesea` 9.5.0 (2026-05-17) · `pyvi` 0.1.1 (2021) — cài thử không hạ phiên bản gói nào.
- Mốc so sánh (dieu-300, không rewrite): từ chối nhầm 4/25, `fact_recall` 0.87, 0 câu sai, leak 0/5.

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Thư viện tách từ | **`underthesea`** 9.5.0 — còn bảo trì (2026-05), `pyvi` dừng từ 2021; user `uv add` (user đồng ý 2026-11-13) |
| Chỗ lưu cột từ khoá | **2 cột** trong `law_chunks_dieu300`: `fts_simple` (theo âm tiết) + `fts_seg` (đã tách từ) → so trên **cùng** bộ chunk |

## Bài 1 — Full-text simple

**Đã làm** (user chạy 2026-11-13): cột sinh tự động `fts_simple tsvector GENERATED ALWAYS AS (to_tsvector('simple',
content)) STORED` + index GIN `law_chunks_dieu300_fts_simple_idx`; Claude kiểm read-only: 444/444 dòng có `fts_simple`.
`uv add underthesea` → `underthesea>=9.5.0`; thử: "Độ tuổi **lao_động tối_thiểu** của người **lao_động** là đủ 15 tuổi".

`to_tsvector('simple', 'Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi')` →
`'15':13 'của':7 'lao':3,9 'là':11 'người':8 'thiểu':6 'tuổi':2,14 'tối':5 'độ':1 'động':4,10 'đủ':12` — mỗi
**âm tiết** là 1 từ, kèm vị trí; "lao động" bị tách đôi.

**Thử q13 — 3 cách xếp hạng từ khoá** (Claude chạy SQL read-only, câu "Độ tuổi lao động tối thiểu là bao nhiêu?",
lọc `public`):

| Cách | Top-1 | Điều 3 (đáp án) |
| --- | --- | --- |
| OR các âm tiết + `ts_rank_cd` | Điều 219 (7.0), Điều 36 (5.7)… | **không** lọt top-5 |
| OR các **cặp âm tiết liền nhau** (`độ <-> tuổi` \| `lao <-> động`…) + `ts_rank_cd` | Điều 219 (3.5), Điều 36… | **không** lọt top-5 |
| **Tự thêm IDF**: `ts_stat` đếm số chunk chứa mỗi từ → `idf = ln(N / ndoc)`, điểm = Σ idf các từ khớp | **Điều 3** (12.25) | **hạng 1** ✅ |

IDF tính được: "động" **0.0**, "lao" **0.1** (có ở gần như mọi chunk) — "thiểu" 3.3, "tối" 2.8, "tuổi" 2.4, "độ" 2.2.

- **Vì sao không dùng AND** _(Claude)_: `plainto_tsquery` nối mọi từ bằng `&` → chunk phải chứa **tất cả** từ trong câu
  hỏi, kể cả "bao", "nhiêu", "là" → câu hỏi tự nhiên dễ ra **0 kết quả**. Dùng **OR** rồi để điểm quyết định.
- **Không có IDF → hệ quả** _(Claude, có số đo ở trên)_: `ts_rank` chỉ đếm tần suất **trong chunk**, không biết từ nào
  phổ biến trong **cả kho** → chunk dài, lặp nhiều "lao động" (Điều 219, 36) thắng → **Điều 3 không lọt top-5**. Thêm IDF
  bằng `ts_stat` (BM25 rút gọn: chỉ IDF, chưa có bão hoà tần suất / chuẩn hoá độ dài) → từ phổ biến tự về ~0 → **Điều 3
  lên hạng 1**. Đây là điểm Notion ghi "kiểm chứng khi làm": Postgres full-text **không phải BM25**.
- **Thử q13:** vector (Buổi 19, dieu-300) **không** đưa Điều 3 vào top-5; từ khoá + IDF đưa lên **hạng 1**.

**Code** (Claude viết theo yêu cầu, 2026-11-13): `rag.keyword_search(conn, question, groups, k=20, table, column)` —
`ts_stat` tính số chunk chứa mỗi từ **chỉ trên chunk user được xem** (câu SQL ghép bằng `sql.Literal` cho an toàn) →
`idf = ln(N / ndoc)` → điểm = Σ idf các từ khớp; `WHERE allowed_groups && groups` luôn bật; `groups=[]` → rỗng; trả cùng
dạng dict với `retrieve()` (điểm ở khoá `sim`). Thử (read-only):

| Câu | `["public"]` top-3 | `["public","internal"]` top-3 |
| --- | --- | --- |
| q13 "Độ tuổi lao động tối thiểu…" | **Điều 3** (12.21) · Điều 92 · Điều 185 | **Điều 3** · Điều 92 · Điều 185 |
| "Mức thưởng hiệu suất quý…" | Điều 104 · 178 · 91 (luật, **0 nội bộ** ✅) | **Điều 6. Thưởng hiệu suất quý** (18.38) · Điều 13 · 14 (nội quy) |

⚠️ Ghi cho Bài 3: parser `simple` coi **dấu `_` là dấu tách** — `ts_debug('simple','lao_động')` → `lao` | `_` | `động`
→ nếu nạp chữ dạng "lao_động" thì tách từ **vô tác dụng**. Phải nối **không dấu cách** (vd. "laođộng") trước khi
`to_tsvector`.

## Bài 2 — RRF

**Code** (Claude viết theo yêu cầu, 2026-11-13): `rag.rrf(lists, k=5, rrf_k=60)` — mỗi chunk Σ `1/(60 + hạng)` qua
các danh sách; `rag.hybrid_retrieve(…, column, pool=20)` = top-20 vector + top-20 từ khoá (**cả 2 nhánh lọc quyền**) →
RRF → top-5; `answer(…, hybrid_column=None)` (báo lỗi nếu bật cùng rewrite — đo riêng); `run_bot(…, hybrid_column)`.
Khoá `sim` của kết quả hybrid = **điểm RRF** (không còn là cosine).

Thử tay (read-only, `law_chunks_dieu300`, `["public"]`):

| Câu | Vector top-5 | Hybrid top-5 (điểm RRF) |
| --- | --- | --- |
| q13 tuổi tối thiểu | **Điều 3** · 219 · 219 · 169 · 143 | **Điều 3** (0.0328) · 219 · 219 · 219 · 185 |
| q05 "nghỉ việc… báo trước" | 115 · 205 · 115 · 113 · 110 | 113 · 139 · 205 · 219 · **36** — vẫn **không có Điều 35** |
| thưởng hiệu suất quý | 104 · 90 · 91 · 91 · 97 | 104 · 91 · 90 · 95 · 91 — **0 nội bộ** ✅ |

- Ở cỡ 300 (Buổi 19) vector **đã** đưa Điều 3 lên hạng 1 cho q13 → hybrid giữ nguyên. q05: từ khoá cũng không cứu được
  khoảng cách từ ngữ "nghỉ việc" ↔ "đơn phương chấm dứt" (luật không chứa chữ "nghỉ việc" ở Điều 35) → việc của
  **rewrite** (Buổi 20), không phải hybrid.
- **Vì sao trộn theo hạng** _(Claude)_: điểm vector (cosine ~0.3–0.7) và điểm từ khoá (Σ IDF ~5–20) **khác thang đo** —
  cộng thẳng thì điểm từ khoá "nuốt" điểm vector; chuẩn hoá thì phụ thuộc phân bố từng câu hỏi. Hạng thì luôn cùng thang
  (1, 2, 3…). `1/(60 + hạng)` giảm **chậm** → chunk đứng cao ở **cả hai** danh sách thắng, một danh sách xếp nhầm không
  kéo lệch quá nhiều. Giống Buổi 13: không so điểm giữa 2 model khác nhau.

## Bài 3 — Tách từ

**Code** (Claude viết theo yêu cầu, 2026-11-13): `chunking.segment_text()` — underthesea `word_tokenize(format="text")`
rồi **bỏ `_`** (nối liền) vì parser `simple` coi `_` là dấu tách; `rag.SEGMENTED_COLUMNS = {"fts_seg"}` →
`keyword_search` tự tách từ **câu hỏi** khi dùng cột `fts_seg` (cùng một hàm cho chunk lẫn câu hỏi, như NFC Buổi 15);
script mới `projects/p2-labor-law-rag/add_fts_seg.py` (tách từ trước, ghi trong 1 transaction, tên bảng qua
`sql.Identifier`) — **ghi DB → user chạy**.

Thử `segment_text` (không đụng DB):

| Đầu vào | Kết quả | Nhận xét |
| --- | --- | --- |
| "Độ tuổi lao động tối thiểu là bao nhiêu?" | "Độ tuổi **laođộng tốithiểu** là **baonhiêu** ?" | "tối thiểu" thành 1 từ ✅; "Độ tuổi" **không** được gộp |
| "Thời gian thử việc tối đa" | "**Thờigian** thử việc **tốiđa**" | "tốiđa" ≠ "tốithiểu" ✅; nhưng "thử việc" **không** được gộp |
| "tro cap thoi viec" | không đổi | không dấu → tách từ không giúp |

Kiểm Postgres giữ được từ đã nối: `to_tsvector('simple','… laođộng tốithiểu …')` → `'laođộng':3 'tốithiểu':4` ✅.

- **Đã chạy** (user 2026-11-13): `ALTER TABLE … ADD COLUMN fts_seg tsvector` + index GIN + `add_fts_seg.py` → "đã điền
  fts_seg cho 444 chunk"; Claude kiểm: 444/444, có `'laođộng'`, `'bộluật'`, `'giảithích'`, `'chươngxi'`…
- **Thử q13 sau tách từ:** từ khoá `fts_simple` → Điều 3 (12.21) hạng 1; `fts_seg` → Điều 3 (12.17) hạng 1 (2 mảnh Điều 3
  đứng đầu) — cả 2 cách đều đúng.

## Bài 4 — 3 cấu hình

| Cấu hình | Từ chối nhầm | Sai | `fact_recall` | Từ chối đúng | Leak |
| --- | --- | --- | --- | --- | --- |
| vector (dieu-300, chạy lại 37 câu) | 4/27 (q05, q20, q23, q25) | 0 | 0.88 (22/27) | 5/5 | 0/5 |
| hybrid `simple` | **3/27** (q05, q20, q25) | 0 | 0.86 (21/27) | 5/5 | 0/5 |
| **hybrid tách từ** | **3/27** (**q02**, q20, q25) | 0 | **0.89** (23/27) | 5/5 | 0/5 |

_(Claude chạy 2026-11-13, bảng `law_chunks_dieu300`, **không rewrite**, 37 câu → `runs/dieu300-vector.jsonl`,
`dieu300-hybrid-simple.jsonl`, `dieu300-hybrid-seg.jsonl`. Chi phí bot ~$0.0055 mỗi lượt; thời gian/câu 2.89 / 2.46 /
3.18 s — phần SQL từ khoá rất nhanh, tách từ câu hỏi thêm ~0.3 s.)_

| So với vector | Sửa được | Tệ đi | `fact_recall` đổi |
| --- | --- | --- | --- |
| hybrid `simple` | q23 | — (nhưng q09, q21 **mất bớt dữ kiện**: 1.00 → 0.25 / 0.60, vẫn trả lời) | 0.88 → 0.86 |
| hybrid tách từ | **q05**, q23 | **q02** | 0.88 → **0.89** |

- **q05 được sửa nhờ tách từ** (không cần rewrite!): câu hỏi tách thành "Người laođộng muốn **nghỉviệc** … baolâu" → nhánh
  từ khoá kéo **Điều 35 + 36** vào top-5 (vector chỉ ra Điều 115, 205, 113…).
- **q02 tệ đi:** top-5 có 2 mảnh Điều 137 + 3 mảnh Điều 139 nhưng **thiếu Khoản 1 Điều 139** (06/07 tháng) — đúng hiện
  tượng "k=5 bị chiếm" như q24 ở Buổi 20 → việc của **rerank** (Buổi 22).
- **q13 đúng ở cả 3 cấu hình** (cỡ 300 đã sửa từ Buổi 19). Leak **0/5** và từ chối đúng **5/5** ở cả 3 → hybrid không mở
  cửa sau (cả 2 nhánh đều lọc quyền).
- **Thật thà về cỡ hiệu quả:** chênh nhau **1 câu** (4 → 3), `fact_recall` ±0.02 — nhỏ. Notion nói hybrid "thường cải
  thiện rõ với thuật ngữ / mã số / tên riêng" — eval set của mình **ít** câu kiểu mã số (đa số là câu hỏi tự nhiên), nên
  lợi ích chưa thể hiện nhiều. Phần retrieve ở đây **tất định** (không rewrite) → khác biệt là thật, nhưng mẫu nhỏ.

## Câu phỏng vấn cuối buổi

### 1. Hybrid search + cải thiện bao nhiêu

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13 — dùng số đo thật của buổi này.)_

> Hybrid = tìm bằng **2 cách** rồi trộn: **vector** (theo nghĩa — giỏi đồng nghĩa, diễn đạt khác) và **từ khoá** (theo
> chữ chính xác — giỏi mã số, thuật ngữ hiếm như "Điều 113", "độ tuổi lao động tối thiểu"). Trộn bằng **RRF** theo hạng.
> Mỗi cách bù chỗ yếu của cách kia: vector "làm mờ" mã số và cụm hiếm, từ khoá thì không hiểu đồng nghĩa.
>
> Với tiếng Việt mình phải sửa 2 chỗ: Postgres full-text **không có IDF** (không phải BM25) nên từ phổ biến như "lao",
> "động" lấn át → tự tính IDF bằng `ts_stat`; và Postgres **không có config tiếng Việt** → so tách theo âm tiết với **tách
> từ** bằng underthesea.
>
> Đo trên 37 câu, chỉ đổi cách tìm: từ chối nhầm **4/27 → 3/27**, `fact_recall` **0.88 → 0.89**, leak vẫn **0/5**. Ví dụ
> rõ: câu "nghỉ việc… báo trước bao lâu" — vector chỉ ra các Điều về nghỉ phép, nhánh từ khoá kéo được **Điều 35** vào nên
> trả lời đúng mà không cần rewrite. **Thật thà:** cải thiện **nhỏ**, vì eval của mình ít câu mã số/thuật ngữ (chỗ hybrid
> mạnh nhất), và chunk đã gắn tiêu đề "Điều N" từ trước; còn 1 câu tệ đi do 5 chỗ trong context bị chiếm → cần rerank.

Câu nhớ: **Hybrid = nghĩa (vector) + chữ chính xác (từ khoá + IDF tự tính), trộn RRF; tiếng Việt phải tách từ; trên dữ
liệu mình: từ chối nhầm 4→3, leak 0/5 — nhỏ vì ít câu mã số.**

### 2. RRF

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

```
Đoạn X: hạng 1 ở vector, hạng 3 ở từ khoá → 1/(60+1) + 1/(60+3) = 0.0164 + 0.0159 = 0.0323
Đoạn Y: hạng 1 ở vector, không có ở từ khoá → 1/(60+1)                = 0.0164
→ X thắng: cao ở CẢ HAI danh sách
```

> RRF (Reciprocal Rank Fusion) gộp nhiều danh sách theo **hạng**: mỗi đoạn được cộng `1/(60 + hạng)` ở mỗi danh sách nó
> xuất hiện, rồi sắp theo tổng. Đoạn đứng cao ở **cả hai** cách tìm sẽ thắng.
>
> Không cộng thẳng điểm vì **2 thang đo khác nhau**: cosine của vector khoảng 0.3–0.7, còn điểm từ khoá (tổng IDF) khoảng
> 5–20 → cộng thẳng thì từ khoá "nuốt" vector; chuẩn hoá thì phụ thuộc phân bố từng câu hỏi, dễ lệch. Giống Buổi 13: không
> so được điểm của 2 model khác nhau. Hạng thì luôn cùng thang (1, 2, 3…).
>
> Hằng số **60** làm điểm giảm **chậm** theo hạng (hạng 1 = 0.0164, hạng 10 = 0.0143) → không để hạng 1 của một danh sách
> áp đảo; một cách tìm xếp nhầm cũng không kéo lệch kết quả quá nhiều. Ưu điểm phụ: không cần tinh chỉnh trọng số.

Câu nhớ: **RRF = Σ 1/(60 + hạng): trộn theo HẠNG vì điểm 2 cách tìm khác thang đo; 60 làm điểm giảm chậm để không danh
sách nào áp đảo; đoạn cao ở cả hai thắng.**

### 3. Từ khoá với tiếng Việt

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

| Khó khăn | Bằng chứng (buổi này) | Cách xử lý |
| --- | --- | --- |
| **Không có config tiếng Việt** | `pg_ts_config` có 29 config, không có vietnamese | Dùng `simple` (không stemming, không từ dừng) |
| **Âm tiết ≠ từ** | `simple` tách "lao động" → "lao" + "động"; "tối thiểu" khớp nhầm "**tối** đa" (nghĩa ngược) | Tách từ trước (underthesea) → "tốithiểu" ≠ "tốiđa" |
| **Bẫy dấu `_`** | `ts_debug('simple','lao_động')` → lao \| _ \| động: tách từ xong lại bị tách lại | Nối liền "laođộng" trước khi `to_tsvector` |
| **Từ phổ biến lấn át** (không IDF) | `ts_rank` "do not use any global information" → Điều 219, 36 thắng; IDF "động" = 0.0, "lao" = 0.1 | Tự tính IDF bằng `ts_stat` → Điều 3 lên hạng 1 |
| **Tách từ không hoàn hảo** | "thử việc", "Độ tuổi" **không** được gộp | Đo, chấp nhận; kết hợp với vector |
| **Gõ không dấu** | "tro cap thoi viec" — tách từ không giúp, từ khoá không khớp | `unaccent` hoặc rewrite thêm dấu (Buổi 20) |

> Tiếng Việt viết **cách theo âm tiết**, nhưng từ thường 2–3 âm tiết. Postgres không có config tiếng Việt nên `simple` tách
> theo âm tiết: "tối thiểu" bị tách thành "tối" + "thiểu" và khớp nhầm cả "tối đa" — nghĩa ngược lại. Mình tách từ bằng
> underthesea, nhưng gặp bẫy: Postgres coi `_` là dấu tách, nên phải nối liền "tốithiểu". Thêm nữa full-text của Postgres
> **không có IDF**, từ như "lao", "động" có ở mọi chunk lại được tính ngang từ hiếm → mình tự tính IDF. Tách từ cũng không
> hoàn hảo ("thử việc" không được gộp) và không giúp câu gõ không dấu → vẫn cần kết hợp vector, và **đo** để biết có lợi
> thật không (trên dữ liệu mình: tách từ tốt hơn âm tiết một chút).

Câu nhớ: **Tiếng Việt cách theo âm tiết, không có config, Postgres không IDF → tách từ (nối liền vì bẫy `_`) + tự tính
IDF; vẫn không cứu được câu không dấu → kết hợp vector và đo.**
