# Buổi 19 — Phase 02 Buổi 7: Chunking nâng cao (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 key_facts + fact_recall · [x] Bài 2 chunker theo cấu trúc · [x] Bài 3 nạp bảng mới ·
  [x] Bài 4 eval + so baseline · [x] Bài 5 2–3 cỡ chunk · [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-13)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 19 xong** (2026-11-13). Code mới: `projects/p2-labor-law-rag/chunking.py` (đọc + làm sạch + gom theo Điều +
chia theo Khoản + gắn tiêu đề + `read_markdown` + `build_records`), `ingest.py` (`<bảng> <max_tokens>`, `sql.Identifier`),
`rag.py` thêm tham số `table` (mặc định `law_chunks` = baseline), `run_eval.py` thêm `fact_recall` + `run_bot(table=…)`.
`eval_set.jsonl` có `key_facts` (74 chuỗi, Claude soạn + kiểm). Bảng DB: `law_chunks` (baseline), `law_chunks_dieu`
(500), `law_chunks_dieu300`, `law_chunks_dieu800`. **Chọn 300** → từ chối nhầm **4/25** (baseline 9), sai **0** (1),
`fact_recall` **0.87** (0.69), bot rẻ hơn 35%.

**Việc tiếp theo**: (1) user commit Buổi 19 (`weeks/week03/session19`, `projects/p2-labor-law-rag/chunking.py`,
`ingest.py`, `rag.py`, `eval/`); (2) **Buổi 20 = Phase 02 Buổi 8 — Query rewriting + Metadata filtering + permission +
5 câu test rò rỉ**, so với **dieu-300**; mục tiêu: q05 ("nghỉ việc" vs "đơn phương chấm dứt"), q20 (không dấu), q23 +
q25 (nhiều Điều). (3) Tuỳ chọn: chấm DeepEval faithfulness/relevancy cho `dieu-300` (~$0.25).

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + mọi lệnh
ghi DB; mỗi lần đo chỉ đổi 1 thứ; notes tiếng Việt, có bảng + nguồn.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-13.)_

- Git: Buổi 18 đã commit (`8839f74`), working tree sạch. `.deepeval/` chưa có trong `.gitignore` (thư mục rỗng → git
  chưa thấy).
- Code hiện có: `projects/p2-labor-law-rag/rag.py` — `retrieve` đọc cứng bảng `law_chunks` (`rag.py:72`); chunk + nạp ở
  `weeks/week03/session15/exercises.py` (`read_docx`, `clean_paragraphs`, `chunk_tokens`, `build_records`,
  `embed_batch`, `ingest` — `ingest` xoá cứng `law_chunks`, dòng 114).
- Baseline (Buổi 18): từ chối đúng 5/5 · **từ chối nhầm 9/25** · DeepEval recall không tin được · faithfulness khớp 18/20.

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Chỗ để chunker | `projects/p2-labor-law-rag/chunking.py` — cạnh `rag.py`, Project #2 dùng lại (user đồng ý 2026-11-13) |
| Cách lưu nhiều bộ chunk | **Mỗi kiểu chunk 1 bảng** cùng cấu trúc: `CREATE TABLE law_chunks_<tên> (LIKE law_chunks INCLUDING ALL)`; `rag.retrieve(…, table=…)`. `law_chunks` giữ nguyên = baseline, chạy lại được bất cứ lúc nào |

## Bài 1 — key_facts + fact_recall

| Đo | Baseline (fixed 500/50) |
| --- | --- |
| `fact_recall` trung bình (25 câu) | **0.69** (DeepEval contextual recall cùng dữ liệu: 0.94 — **lạc quan 25 điểm**) |
| Số câu đủ 100% dữ kiện | **15/25** |

_(`key_facts`: **Claude soạn theo yêu cầu** 2026-11-13 — 74 chuỗi cho 25 câu, mỗi chuỗi kiểm bằng code: **có thật trong
đúng Điều nguồn** (0 lỗi) và **chỉ xuất hiện 1 lần** trong cả bộ luật (không cảnh báo nào). `fact_recall` Claude thêm vào
`grade_by_code` trong `run_eval.py`; chấm lại `runs/baseline.jsonl`, không gọi API.)_

**Kiểm chéo — `fact_recall` khớp gần như hoàn hảo với hành vi bot:**

| Nhóm | Câu | `fact_recall` |
| --- | --- | --- |
| Bot trả lời đúng (15) | q01, q02, q04, q06–q08, q10–q12, q14, q15, q18, q19, q21, q24 | **1.00** cả 15 câu |
| Bot từ chối nhầm (9) | q03 0.50 · q05 0.00 · q09 0.00 · q16 0.67 · q17 0.00 · q20 0.00 · q22 0.33 · q23 0.50 · q25 0.33 | **< 1.00** cả 9 câu |
| Bot trả lời **sai** (1) | q13 | **0.00** |

→ Đủ dữ kiện ⇒ bot trả lời đúng; thiếu dữ kiện ⇒ bot từ chối (hoặc sai, q13). Metric này **giải thích được** hành vi bot,
còn DeepEval recall thì không (cho 1.0 cả câu thiếu dữ kiện).

- **`key_facts` vs `sources`** _(câu mẫu Claude)_: `sources` hỏi "**Điều** đúng có lọt top-k không" → khớp "Điều 20." ở
  **cuối** chunk vẫn tính trúng dù thân điều không có → lạc quan (21/25). `key_facts` hỏi "**nội dung** cần thiết có lọt
  top-k không" — đếm đúng chuỗi dữ kiện → không bị lừa bởi tiêu đề.
- **Tránh bẫy trùng số** _(câu mẫu Claude)_: chọn cụm **đủ dài để chỉ có ở 1 chỗ** trong luật — vd. q05 không dùng "45
  ngày" (có ở cả Điều 35 và 36) mà dùng "Ít nhất 45 ngày **nếu làm việc theo** hợp đồng lao động không xác định thời
  hạn" (cách viết riêng của Điều 35; Điều 36 viết "…**đối với** hợp đồng…"); kiểm bằng code: mỗi chuỗi xuất hiện đúng 1
  lần trong cả bộ luật.

## Bài 2 — Chunker theo cấu trúc

| Đo | Kết quả |
| --- | --- |
| Số chunk | **307** (baseline fixed: 210) — `max_tokens=500` |
| Token min / median / max | **51 / 306 / 1,202** (baseline: mọi chunk ~500) |
| Số Điều phải tách | **66 / 220** |
| Chunk vượt 500 | **9** — 1 Khoản quá dài, không tách nhỏ hơn: Điều 5 (598), 20 (553), 35 (529), 36 (958), 174 (840), 188 (568), 219 ×3 (566–1,202). Vẫn < 8,192 token giới hạn embedding → **chấp nhận** cho lần đo này |

_(Code `projects/p2-labor-law-rag/chunking.py` — user viết theo khung của Claude, bước A + B; Claude chạy kiểm
read-only 2026-11-13.)_ Kiểm Điều trong eval: **Điều 20** 2 chunk (234, 553) — "không quá 36 tháng" ở chunk 1; **Điều 35**
2 chunk — "Ít nhất 45 ngày nếu làm việc theo…" ở chunk 1; **Điều 107** 3 chunk (372, 424, 131); **Điều 115** 1 chunk
(397); **Điều 190** 1 chunk (497, đủ 3 mốc 06/09 tháng + 01 năm). **Mọi chunk đều mở đầu bằng tiêu đề Điều** ✅. Bước A:
220 Điều, 0 dòng Chương/Mục lẫn vào, "1.4" Điều 139 đã thành "1.", 92 dòng tên chương/mục bị bỏ.

- Vì sao gắn tiêu đề đầu mỗi chunk:
- Gộp Điều ngắn:

## Bài 3 — Nạp bảng `law_chunks_dieu`

Bước C: `chunking.py` thêm `read_markdown` (bỏ `**`, `#`, `>`, dòng kẻ bảng → tiêu đề "Điều N." của nội quy khớp
`DIEU_RE`) + `build_records`; file mới `projects/p2-labor-law-rag/ingest.py` (`embed_batch`, `ingest(conn, table, …)` —
embed trước, xoá + thêm trong 1 transaction, tên bảng qua **`sql.Identifier`** để chống SQL injection ở **tên**; user viết
C1, Claude điền C2 theo yêu cầu). User tạo bảng `CREATE TABLE law_chunks_dieu (LIKE law_chunks INCLUDING ALL)` (cột `id`
dùng chung sequence `law_chunks_id_seq` — vô hại) và chạy `ingest.py` 2026-11-13.

| Kiểm (Claude, read-only) | Kết quả |
| --- | --- |
| Số dòng | luật **307** `{public}` + nội quy **14** `{internal}` (Buổi 15: 210 + 6) |
| Có `heading` | **321/321** — nội quy lần đầu có tiêu đề |
| Tiêu đề cụt | **0** — "Điều 103. Chế độ nâng lương, nâng bậc, phụ cấp, trợ cấp" (Buổi 16: "…nâ") |
| Chunk mở đầu bằng tiêu đề | **321/321** |
| Ký tự `�` | 0 |
| Bảng baseline `law_chunks` | vẫn 216 dòng, không đụng |

## Bài 4–5 — So với baseline

| Lần chạy | Từ chối nhầm | Từ chối đúng | `fact_recall` | Faithfulness | Relevancy (không từ chối) |
| --- | --- | --- | --- | --- | --- |
| Baseline fixed 500/50 | 9/25 | 5/5 | **0.69** | 0.97 (mini) | 0.95 (mini) |
| **Theo Điều/Khoản, max 500** (`dieu-500`) | **3/25** | **5/5** | **0.85** (21/25 đủ 100%) | _chưa chấm_ | _chưa chấm_ |

| **Theo Điều/Khoản, max 300** (`dieu-300`) | 4/25 | 5/5 | **0.87** (20/25) | _chưa chấm_ | _chưa chấm_ |
| **Theo Điều/Khoản, max 800** (`dieu-800`) | 3/25 | 5/5 | 0.85 (21/25) | _chưa chấm_ | _chưa chấm_ |

_(User chạy 2026-11-13 → `runs/dieu-500.jsonl`; chấm bằng code. Bot: $0.0055 / 30 câu, **3.13 s**/câu, token vào TB
**1,346** — baseline $0.0068, 3.55 s, 1,803 → chunk nhỏ hơn nên **rẻ + nhanh hơn**.)_

- **Câu tốt lên** (6 câu từ chối nhầm → trả lời, `fact_recall` → 1.00): **q03, q09, q16, q17, q22, q23**. Đúng 4 câu lỗi
  "tiêu đề cuối chunk" (q03, q09, q17, q22) + q16 (Điều 190 giờ đủ 3 mốc trong 1 chunk) + q23 (đủ Điều 35 + 20).
- **Câu tệ đi:** **0** — 15 câu baseline trả lời được vẫn trả lời; từ chối đúng vẫn 5/5.
- **Còn lỗi (4)** — đều **không phải lỗi chunking**:

  | Câu | Kết quả | Vì sao | Buổi sửa |
  | --- | --- | --- | --- |
  | q05 | từ chối, `fact_recall` 0 | Top-5: Điều 115 (nghỉ việc riêng), 205, 29, 110, 109 — câu hỏi "**nghỉ việc**" bị hiểu là "**nghỉ**" (nghỉ phép); Điều 35 dùng chữ "**đơn phương chấm dứt hợp đồng**" | **8** (query rewrite) |
  | q13 | **vẫn sai**: "đủ 13 tuổi … (Điều 143)" | Điều 3 vẫn không lọt top-5 | **9** (hybrid) + 11 |
  | q20 | từ chối | không dấu | **8** |
  | q25 | từ chối, 0.33 | thiếu Điều 34 + 46 | **8 / 10** |

- Lưu ý: q03 giờ trả lời "Có 2 loại…" nhưng **không nêu** "không quá 36 tháng" dù dữ kiện có trong context → trả lời
  **thiếu** (chấm tay/đúng câu hỏi mới thấy, `fact_recall` không đo phần này).

## Bài 5 — So 3 cỡ chunk

_(Bảng `law_chunks_dieu300` / `law_chunks_dieu800`: user tạo + nạp; Claude chạy bot (đọc DB + gọi LLM) + chấm bằng code,
2026-11-13 → `runs/dieu-300.jsonl`, `runs/dieu-800.jsonl`.)_

| | baseline | dieu-300 | **dieu-500** | dieu-800 |
| --- | --- | --- | --- | --- |
| Số chunk luật (median token) | 210 (~500) | 430 (224) — **54 chunk > 300** | 307 (306) | 246 (347) |
| Từ chối nhầm | 9/25 | 4/25 (q05, q20, **q23**, q25) | **3/25** (q05, q20, q25) | 3/25 (như 500) |
| Trả lời **sai** | q13 | **0** ✅ q13 đúng "đủ 15 tuổi (Điều 3)" | q13 ("13 tuổi", Điều 143) | q13 |
| `fact_recall` / đủ 100% | 0.69 / 15 | **0.87** / 20 | 0.85 / 21 | 0.85 / 21 |
| Chi phí bot · s/câu · token vào | $0.0068 · 3.55 · 1,803 | **$0.0044 · 3.07 · 1,018** | $0.0055 · 3.13 · 1,346 | $0.0062 · 3.30 · 1,556 |

**Đọc kết quả:**
- **300 sửa được q13** (câu sai nguy hiểm nhất): Điều 3 "Giải thích từ ngữ" dài, nhiều định nghĩa → ở cỡ 500 nằm chung
  1 chunk to, vector bị "pha" → không lọt top-5; ở cỡ 300, chunk chứa "Độ tuổi lao động tối thiểu… đủ 15 tuổi" **gọn,
  sắc** → lên **hạng 1**. Đúng lý thuyết Buổi 15: chunk nhỏ = vector sắc.
- **Nhưng 300 làm hỏng q23** (câu nhiều Điều): Điều bị chia nhiều mảnh hơn → top-5 không chứa đủ Điều 35 → từ chối.
  Đúng đánh đổi: chunk nhỏ = thiếu ngữ cảnh.
- **800 = 500** trên mọi chỉ số code, chỉ tốn token hơn (+16%) → không có lý do chọn 800.
- **Chênh nhau chỉ 1 câu** ở mỗi chiều → nằm trong vùng **dao động** (bot có ngẫu nhiên; riêng phần retrieve gần như
  tất định nên q13/q23 đổi là thật). Không kết luận mạnh từ 1 câu.
- **Overlap 0/50/100** (Notion): chunk theo cấu trúc không cắt giữa Khoản, và mỗi mảnh đã lặp lại **tiêu đề Điều** làm
  ngữ cảnh → overlap ít ý nghĩa ở đây; **chưa đo** — ghi lại là quyết định có chủ đích.

**Quyết định (user, 2026-11-13): chọn `max_tokens = 300`** (bảng `law_chunks_dieu300`) làm cấu hình mang sang Buổi 20.
Lý do: **0 câu trả lời sai** (câu luật sai mà tự tin — q13 — hại user hơn câu "không tìm thấy"), rẻ nhất ($0.0044, 1,018
token vào); đổi lại thêm 1 câu từ chối nhầm (q23, câu nhiều Điều) — Buổi 20 (query rewriting) nhắm đúng loại câu này.

## Câu phỏng vấn cuối buổi

### 1. Chunk size chọn thế nào

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13 — dùng số đo thật của buổi này.)_

> Không chọn bằng cảm giác mà **đo**: mình giữ nguyên mọi thứ, chỉ đổi cỡ chunk (300 / 500 / 800, cắt theo cấu trúc
> Điều/Khoản), chạy cùng 30 câu eval, so số từ chối nhầm, câu sai, `fact_recall` và chi phí.
>
> Đánh đổi thấy rõ: **chunk nhỏ** thì vector **sắc** — Điều 3 là danh sách định nghĩa dài, ở cỡ 500 bị "pha" nên không
> tìm ra, ở cỡ 300 thì đoạn "độ tuổi lao động tối thiểu" lên hạng 1 và câu trả lời hết sai; nhưng chunk nhỏ thì **thiếu
> ngữ cảnh** — câu cần 2 Điều (q23) bị rơi mất 1 Điều. **Chunk lớn** (800) không giúp thêm gì, chỉ tốn token hơn 16%.
>
> Mình chọn **300** vì không còn câu trả lời sai (với luật, trả lời sai mà tự tin hại hơn nói "không tìm thấy") và rẻ
> nhất; câu nhiều Điều để query rewriting xử lý. Ngoài ra cỡ chunk phải tôn trọng **cấu trúc**: với luật, ranh giới tự
> nhiên là Điều/Khoản — 54 chunk vẫn vượt 300 vì có Khoản dài hơn 300, và mình chấp nhận chứ không cắt giữa Khoản.

Câu nhớ: **Chunk size = cân "sắc" vs "đủ ngữ cảnh", chọn bằng đo trên eval set (300/500/800); theo ranh giới tự nhiên
của tài liệu; chọn 300 vì 0 câu sai + rẻ nhất.**

### 2. Theo cấu trúc vs fixed-size

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

| | Fixed-size (baseline) | Theo cấu trúc (dieu-300) |
| --- | --- | --- |
| Cắt ở đâu | Mỗi 500 token, **mù** — giữa câu, giữa Điều | Theo **Điều**; Điều dài chia theo **Khoản** |
| Tiêu đề | Chỉ chunk chứa dòng tiêu đề mới có | **Mọi** chunk mở đầu bằng "Điều N. Tên điều" |
| Lỗi điển hình | Tiêu đề cuối chunk, thân điều ở chunk sau; vỡ chữ; tiêu đề cụt | Khoản quá dài vẫn vượt cỡ (54 chunk) |

> Fixed-size cắt mù mỗi 500 token nên hay **tách tiêu đề khỏi nội dung**: chunk có "Điều 20." ở cuối, còn "không quá 36
> tháng" nằm ở chunk sau không được lấy → bot nói "không tìm thấy". Theo cấu trúc thì cắt theo Điều/Khoản và **gắn tiêu
> đề vào đầu mọi chunk**, nên dữ kiện luôn đi cùng "địa chỉ" của nó.
>
> Đo trên **30 câu eval**, chỉ đổi cách chunk: **từ chối nhầm 9/25 → 4/25**, câu trả lời sai **1 → 0**, **`fact_recall`
> 0.69 → 0.87** (tỷ lệ dữ kiện chính có trong top-5, kiểm bằng code), từ chối đúng giữ **5/5**, chi phí bot **giảm 35%**
> vì chunk gọn hơn. Không câu nào trước đúng mà giờ sai — đó là lý do chạy lại **cả** bộ eval chứ không chỉ các câu lỗi.

Câu nhớ: **Fixed-size cắt mù → tách tiêu đề khỏi nội dung; theo cấu trúc + gắn tiêu đề → từ chối nhầm 9→4, fact_recall
0.69→0.87, rẻ hơn 35%, không câu nào tệ đi.**

### 3. Cải tiến làm vài câu tệ đi

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

> Có. Khi giảm cỡ chunk từ 500 xuống 300: **q13 tốt lên** — định nghĩa "độ tuổi lao động tối thiểu" nằm trong Điều 3 rất
> dài, chunk nhỏ làm đoạn đó "sắc" hơn nên tìm ra và hết trả lời sai; nhưng **q23 tệ đi** — câu cần 2 Điều (báo trước khi
> nghỉ + hợp đồng hết hạn), chunk nhỏ chia Điều thành nhiều mảnh hơn nên top-5 rơi mất Điều 35, bot từ chối.
>
> **Phát hiện** được vì mỗi lần sửa mình chạy lại **cả 30 câu** và so **từng câu** với lần trước, không chỉ nhìn điểm
> trung bình (trung bình gần như hoà: 4 vs 3 từ chối nhầm). **Xử lý:** không cố "ăn cả hai" bằng cách chỉnh cỡ chunk, mà
> (1) cân **mức nghiêm trọng** — câu luật sai mà tự tin hại hơn câu "không tìm thấy" → chọn 300; (2) ghi rõ đánh đổi trong
> `eval-results.md`; (3) giao loại câu nhiều Điều cho cải tiến **khác** — query rewriting tách câu hỏi (Buổi 20), rerank
> (Buổi 22) — rồi đo lại xem q23 có quay về không.

Câu nhớ: **300 sửa q13 nhưng làm hỏng q23 → phát hiện nhờ so từng câu trên cả bộ eval → chọn theo mức nghiêm trọng (sai >
từ chối), ghi đánh đổi, giao q23 cho query rewriting.**
