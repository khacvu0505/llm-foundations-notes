# Eval results — RAG Bộ luật Lao động

Mọi thay đổi RAG từ giờ đều ghi số vào đây (Notion Phase 02, Buổi 6). Mỗi lần chạy = 1 mục, **mới nhất ở trên**. Không
sửa số cũ — chỉ thêm mục mới.

Cách chạy: `uv run python projects/p2-labor-law-rag/eval/run_eval.py` (bật/tắt từng bước trong `__main__`).

---

## 2026-11-13 — Hybrid search: vector + từ khoá (RRF) (Buổi 21)

Cùng bảng `law_chunks_dieu300`, **không rewrite**, 37 câu. Từ khoá = Postgres full-text + **IDF tự tính** (`ts_stat` —
`ts_rank` gốc không có IDF nên không phải BM25); trộn **RRF** (`Σ 1/(60 + hạng)`, top-20 mỗi nhánh → top-5); cả 2 nhánh
lọc quyền. 2 cách tách: `simple` (theo âm tiết) và **tách từ** `underthesea` (nối liền vì `simple` coi `_` là dấu tách).

| Đo (code) | vector | hybrid `simple` | **hybrid tách từ** |
| --- | --- | --- | --- |
| Từ chối nhầm | 4/27 | 3/27 | **3/27** |
| Trả lời sai | 0 | 0 | 0 |
| `fact_recall` · đủ 100% | 0.88 · 22 | 0.86 · 21 | **0.89 · 23** |
| Từ chối đúng | 5/5 | 5/5 | 5/5 |
| **Leak** | 0/5 | 0/5 | **0/5** |
| s/câu | 2.89 | 2.46 | 3.18 |

- Tách từ sửa **q05** không cần rewrite ("nghỉviệc" kéo Điều 35, 36 vào) + q23; nhưng làm hỏng **q02** (k=5 bị 2 mảnh Điều
  137 chiếm, thiếu Khoản 1 Điều 139). `simple` sửa q23 nhưng làm 2 câu mất bớt dữ kiện (q09, q21).
- Lợi ích **nhỏ** (1 câu) — eval ít câu mã số/thuật ngữ, nơi hybrid mạnh nhất. Kết quả thô `runs/dieu300-{vector,
  hybrid-simple,hybrid-seg}.jsonl`.

---

## 2026-11-13 — Metadata filtering (Buổi 20 Bài 5)

Câu hỏi nêu "Điều N" → `heading LIKE 'Điều N.%'` (lọc độ liên quan, **cạnh** lọc quyền), chunk trong phạm vi đứng trước,
bù chỗ trống từ tìm kiếm thường (`fill`). Thêm 2 câu vào eval: **q36** (theo Điều 113…), **q37** ("Điều 26 quy định gì?").
Eval set giờ **37 câu** (22 single / 5 multi / 5 not_found / 5 leak).

| Câu | Hạng Điều nguồn: không lọc → có lọc (không rewrite / có rewrite) | Đúng/sai |
| --- | --- | --- |
| q36 | 1 → 1 / 1 → 1 | đúng cả 2 |
| q37 | 2 → 1 / 3 → 1 | đúng cả 2 |

- Lợi ích **nhỏ** trên bộ dữ liệu này: mọi chunk đã mở đầu bằng "Điều N. Tên điều" (Buổi 19) nên tìm thường vẫn ra. Bộ lọc
  là lưới an toàn rẻ (đảm bảo hạng 1); 35 câu còn lại không bị ảnh hưởng (không bắt được phạm vi).
- **Lần chạy thứ 2** của cấu hình rewrite (37 câu, `runs/dieu300-rewrite-meta.jsonl`): từ chối nhầm **1/27** (lần này là
  **q17**, lần trước là **q24**) · `fact_recall` 0.96 · từ chối đúng 5/5 · **leak 0/5**. → rewrite làm kết quả **dao
  động giữa các lần chạy**; so cấu hình có rewrite cần chạy nhiều lần.

---

## 2026-11-13 — Query rewriting, multi-query (`dieu300-rewrite`, Buổi 20)

**Chỉ đổi 1 thứ so với dieu-300: thêm bước viết lại câu hỏi.** `rewrite()` (`gpt-6-luna`, structured output, câu gốc
luôn giữ, cấm trả lời/thêm số liệu) → `retrieve_multi()` (tìm từng câu, **lọc quyền mọi câu**, xen kẽ theo hạng, k=5).
Bot vẫn trả lời câu gốc, prompt không đổi. 35 câu (gồm 5 leak). Kết quả thô `runs/dieu300-rewrite.jsonl`.

| Đo (code) | dieu-300 | **dieu-300 + rewrite** | Thay đổi |
| --- | --- | --- | --- |
| **Từ chối nhầm** | 4/25 | **1/25** (q24) | **−3** ✅ |
| Trả lời sai | 0 | 0 | giữ ✅ |
| Từ chối đúng | 5/5 | 5/5 | giữ ✅ |
| **`fact_recall` TB** · đủ 100% | 0.87 · 20 | **0.96 · 23** | **+0.09** ✅ |
| **Leak rate** | 0/5 | **0/5** | giữ ✅ |
| Bot $ / 30 câu · s/câu | $0.0044 · 3.07 | **$0.0073 · 6.32** | **+66% chi phí, ×2 độ trễ** ⚠️ |

- Sửa: q05 (từ ngữ luật), q20 (thêm dấu — nhưng trả lời thiếu 2/4 mức), q23, q25 (tách câu nhiều ý). q35 giờ trả lời theo
  luật (150%) thay vì từ chối, không lộ.
- **Tệ đi: q24** — 4 câu truy vấn lấp 5 chỗ bằng mảnh Điều 137/139 nhưng thiếu Khoản 1 Điều 139 → từ chối. Giới hạn k=5
  là nút thắt → rerank (Phase 02 Buổi 10 = Session 22).

---

## 2026-11-13 — Leak test (Buổi 20 Bài 2)

5 câu `type: "leak"` (q31–q35) trong `eval_set.jsonl`: user `public` hỏi nội dung chỉ có trong nội quy giả. Cấu hình
**dieu-300** (chưa rewrite); lọc quyền `allowed_groups && groups` trong SQL. Kết quả thô `runs/dieu300-leak.jsonl`.

| Đo | Kết quả |
| --- | --- |
| **Leak rate** | **0/5** ✅ — 0 chunk nội bộ ở bước tìm, 0 dấu rò rỉ trong câu trả lời |
| Negative control (user `{public, internal}`) | Bài test **bắt được** cả 5 (1–4 chunk nội bộ + dấu rò rỉ mỗi câu) → test nhạy |

Dấu rò rỉ được chọn sao cho: có trong nội quy giả, **không** có trong luật, **không** có trong câu hỏi.

---

## 2026-11-13 — So cỡ chunk 300 / 500 / 800 (Buổi 19 Bài 5)

Cùng chunker theo Điều/Khoản, chỉ đổi `max_tokens`. Bảng `law_chunks_dieu300`, `law_chunks_dieu`, `law_chunks_dieu800`.
Kết quả thô `runs/dieu-300.jsonl`, `runs/dieu-500.jsonl`, `runs/dieu-800.jsonl`.

| Đo (code) | 300 | 500 | 800 |
| --- | --- | --- | --- |
| Chunk luật · median token · vượt max | 430 · 224 · 54 | 307 · 306 · 9 | 246 · 347 · 3 |
| Từ chối nhầm | 4/25 | **3/25** | 3/25 |
| Trả lời sai | **0** (q13 đúng) | 1 (q13) | 1 (q13) |
| Từ chối đúng | 5/5 | 5/5 | 5/5 |
| `fact_recall` · đủ 100% | **0.87** · 20 | 0.85 · 21 | 0.85 · 21 |
| Bot $ · s/câu · token vào | **$0.0044** · 3.07 · 1,018 | $0.0055 · 3.13 · 1,346 | $0.0062 · 3.30 · 1,556 |

- 300 sửa q13 (định nghĩa trong Điều 3 dài → chunk nhỏ thì "sắc", lên hạng 1) nhưng làm hỏng q23 (câu nhiều Điều).
- 800 không hơn 500 ở chỉ số nào, chỉ tốn token hơn.
- Khác biệt chỉ 1 câu mỗi chiều → coi như **hoà** giữa 300 và 500; chọn theo mức nghiêm trọng của lỗi + chi phí.
- Overlap 0/50/100: **không đo** — chunk theo cấu trúc không cắt giữa Khoản và đã lặp tiêu đề Điều ở mỗi mảnh.
- **Chọn 300** làm cấu hình hiện tại (0 câu sai, rẻ nhất); bảng `law_chunks_dieu300`. Các buổi sau so với **dieu-300**.

---

## 2026-11-13 — Chunk theo Điều/Khoản, max 500 token (`dieu-500`, Buổi 19)

**Chỉ đổi 1 thứ so với baseline: cách chunk.** Bot, prompt, k=5, model, 30 câu giữ nguyên.

| Mục | Giá trị |
| --- | --- |
| Chunking | `projects/p2-labor-law-rag/chunking.py` — 1 Điều = 1 chunk; Điều > 500 token chia theo **Khoản** (gộp Khoản liền nhau tới gần 500); **tiêu đề Điều ở đầu mọi chunk**; bỏ số chú thích ("1.4" → "1."), bỏ dòng Chương/Mục |
| Bảng | `law_chunks_dieu` — luật 307 chunk (token 51 / median 306 / max 1,202; 9 chunk > 500 vì 1 Khoản quá dài) + nội quy 14 chunk |
| Kết quả thô | `runs/dieu-500.jsonl` |

| Đo (code) | Baseline | **dieu-500** | Thay đổi |
| --- | --- | --- | --- |
| **Từ chối nhầm** | 9/25 | **3/25** | **−6** ✅ |
| Từ chối đúng | 5/5 | **5/5** | giữ nguyên ✅ |
| **`fact_recall` TB** | 0.69 | **0.85** | **+0.16** ✅ |
| Đủ 100% dữ kiện | 15/25 | **21/25** | +6 |
| Trả lời sai (đã biết) | q13 | q13 | chưa sửa |
| Bot: chi phí / thời gian / token vào TB | $0.0068 · 3.55 s · 1,803 | **$0.0055 · 3.13 s · 1,346** | rẻ + nhanh hơn |

- Tốt lên: q03, q09, q16, q17, q22, q23. **Tệ đi: 0.**
- Còn lại 4 lỗi **không do chunking**: q05 ("nghỉ việc" ≈ "nghỉ" → Buổi 8), q13 (Điều 3 không lọt top-5 → Buổi 9),
  q20 (không dấu → Buổi 8), q25 (nhiều Điều → Buổi 8/10).
- DeepEval (faithfulness/relevancy, `gpt-5.4-mini`): _chưa chấm lần này._

---

## 2026-11-12 — Baseline (naive RAG, Buổi 16)

### Cấu hình

| Mục | Giá trị |
| --- | --- |
| Bot | `projects/p2-labor-law-rag/rag.py` — chép y nguyên Buổi 16 (chỉ thêm trả `chunks` cho eval) |
| Dữ liệu | 18/VBHN-VPQH (210 chunk `{public}`) + nội quy ABC giả (6 chunk `{internal}`), bảng `law_chunks` |
| Chunking | Fixed-size 500 token, overlap 50, tokenizer `cl100k_base`, tiêu đề Điều "mang theo" |
| Retrieve | `text-embedding-3-small`, cosine `<=>`, **k = 5**, lọc `allowed_groups`, không index (tìm chính xác) |
| Sinh câu trả lời | `gpt-6-luna`, Responses API, `max_output_tokens=600`, prompt `INSTRUCTIONS` Buổi 16 |
| Eval set | `eval_set.jsonl` — 30 câu: 20 single / 5 multi / 5 not_found, `group=public` |
| Giám khảo | DeepEval 4.3.4; `gpt-5.4-mini` và `gpt-5.4`; ngưỡng **0.5** |
| Kết quả thô | `runs/baseline.jsonl` · `runs/baseline_scores.jsonl` (mini) · `runs/baseline_scores_gpt-5.4.jsonl` |
| Commit | Code chạy trên working tree sau `8159fd7` (rag.py + run_eval.py **chưa commit** lúc chạy) |

### 1. Chấm bằng code — **đáng tin nhất**

| Đo | Kết quả |
| --- | --- |
| Từ chối đúng (5 câu not_found) | **5/5** ✅ — kể cả câu "luật khác" (BHXH, thuế) |
| **Từ chối nhầm** (25 câu có đáp án) | **9/25 = 36%** ❌ — q03, q05, q09, q16, q17, q20, q22, q23, q25 |
| Trả lời **sai** mà không từ chối | ≥ 1: q13 ("đủ 13 tuổi", đúng là đủ 15 tuổi) — _đủ số sau khi chấm tay (Bài 6)_ |
| Trích dẫn `[n]` không tồn tại | 0/30 |
| Điều nguồn có trong top-5 (`source_hit`) | 21/25 — **lạc quan** (đếm cả tiêu đề Điều nằm cuối chunk dù thân điều không có) |

**9 câu từ chối nhầm, lỗi ở đâu** (kiểm dữ kiện chính có trong 5 chunk không):

| Loại lỗi | Câu | Nguyên nhân | Sửa ở |
| --- | --- | --- | --- |
| Retrieve — ranh giới chunk | q03, q09, q17, q22 | Tiêu đề Điều ở **cuối** chunk, thân điều ở chunk sau (không được lấy) | Buổi 7 — chunking |
| Retrieve — câu hỏi | q20 | Gõ không dấu | Buổi 8 — query rewrite |
| Retrieve — nhiều đoạn | q23, q25 | Thiếu 1–2 trong các Điều cần | Buổi 8–10 |
| Retrieve — sai Điều trùng số | q05 | Top-5 có "Ít nhất 45 ngày" nhưng của **Điều 36** (người sử dụng lao động), thân **Điều 35** (người lao động) không có | Buổi 7 |
| Lai: retrieve cắt + prompt quá chặt | q16 | Có 2/3 khoản Điều 190, khoản 3 bị cắt → từ chối **cả câu** thay vì trả lời phần có | Buổi 7 + 11 |

→ **8/9 có gốc ở retrieve** (q16 lai), **0 lỗi generate thuần**. _(Đính chính 2026-11-13 khi làm Bài 5: bản đầu ghi q05,
q16 là "generate" do khớp chuỗi "45 ngày" nhầm sang Điều 36.)_

### 2. DeepEval — 🚩 dùng thận trọng

| Metric | `gpt-5.4-mini` (TB / đạt) | `gpt-5.4` (TB / đạt) | Tin được? |
| --- | --- | --- | --- |
| Contextual recall | 0.94 / 25 | 0.94 / 24 | ❌ **Không** — cả 2 giám khảo cho 1.0 khi dữ kiện thiếu (q03, q17, q23) |
| Contextual precision | 0.83 / 21 | 0.78 / 21 | ⚠️ chưa kiểm |
| Faithfulness | 0.97 / 24 | 0.96 / 24 | ⚠️ cao giả: câu từ chối = 1.0, câu sai q13 = 1.0 |
| Answer relevancy | 0.77 / 20 | **0.62 / 17** | ✅ gpt-5.4 chấm câu từ chối = 0 (8/9) |

`gpt-5.4` theo loại câu — single (20): recall 0.95 · precision 0.72 · faithfulness 0.95 · relevancy 0.68; multi (5):
0.90 · 1.00 · 1.00 · **0.40**. Riêng 16 câu **không** từ chối: faithfulness 1.00, relevancy 0.91.

### 3. Chi phí + thời gian

| Hạng mục | Số |
| --- | --- |
| Bot (30 câu) | **$0.0068**; token vào TB **1,803**/câu, ra tổng 2,756; **3.55 s**/câu (median 2.91 s) |
| Giám khảo `gpt-5.4-mini` (25 câu × 4 metric) | $0.45 (≈ $0.018/câu) |
| Giám khảo `gpt-5.4` (25 câu × 4 metric) | $1.55 (≈ $0.062/câu) |

### 4. Kết luận baseline

1. **Vấn đề lớn nhất: từ chối nhầm 36%**, gần như toàn bộ do **retrieve** (fixed-size chunk cắt rời tiêu đề và thân Điều;
   câu không dấu; câu nhiều đoạn).
   Câu **nguy hiểm nhất** là q13 — trả lời **sai mà tự tin**, giám khảo vẫn cho điểm tối đa.
2. **Từ chối đúng tốt (5/5)** — giữ được khi cải tiến (không đánh đổi).
3. **Giám khảo LLM không đo được recall** trên dữ liệu này → Buổi 19+: đo retrieve bằng **code** (`key_facts` trong eval
   set); giữ DeepEval `gpt-5.4` cho faithfulness/relevancy, có kiểm tay.
4. **Kiểm giám khảo (Bài 6):** 20 câu (16 có trả lời + 4 từ chối nhầm) do **Claude chấm có bằng chứng** (user nhờ —
   _không phải người chấm_; phiếu `runs/baseline_handgrade.md`). Faithfulness khớp **18/20** với cả `gpt-5.4-mini`
   (lệch q07, q13) và `gpt-5.4` (lệch q13, q03). Faithfulness **không bắt được câu sai** (q13). Đúng câu hỏi: đúng 11 ·
   thiếu 4 · sai 1 · từ chối nhầm 4 (trên 20 câu này).

---

## Bảng trước/sau (điền dần qua Buổi 19–23)

| Lần chạy | Từ chối nhầm | Từ chối đúng | Trả lời sai | Relevancy (gpt-5.4) | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| Baseline (2026-11-12) | 9/25 | 5/5 | ≥ 1 | 0.62 | naive RAG · `fact_recall` 0.69 |
| dieu-300 (2026-11-13) | 4/25 | 5/5 | **0** | _chưa chấm_ | `fact_recall` 0.87 · rẻ nhất |
| **dieu-500** (2026-11-13) | **3/25** | 5/5 | 1 (q13) | _chưa chấm_ | chunk theo Điều/Khoản · `fact_recall` **0.85** |
| dieu-800 (2026-11-13) | 3/25 | 5/5 | 1 (q13) | _chưa chấm_ | = 500, tốn token hơn |
| **dieu-300 + rewrite** (2026-11-13) | **1/25** | 5/5 | **0** | _chưa chấm_ | `fact_recall` **0.96** · leak **0/5** · +66% $ · ×2 độ trễ |
| + rewrite + metadata, lần 2 (2026-11-13) | 1/27 (q17) | 5/5 | 0 | _chưa chấm_ | `fact_recall` 0.96 · leak 0/5 · rewrite dao động: lần 1 hỏng q24, lần 2 hỏng q17 |
| dieu-300 vector, 37 câu (2026-11-13) | 4/27 | 5/5 | 0 | _chưa chấm_ | mốc so hybrid · `fact_recall` 0.88 |
| **dieu-300 hybrid tách từ** (2026-11-13) | **3/27** | 5/5 | 0 | _chưa chấm_ | `fact_recall` **0.89** · leak 0/5 · không rewrite |
| hybrid tách từ + rerank `bge` (2026-11-13) | 2/27 (q20, q25) | 5/5 | 0 | _chưa chấm_ | `fact_recall` 0.95 · leak 0/5 · rerank 3.03 s/câu · tổng 5.93 s (+86%) |
| **hybrid tách từ + rerank `mmarco`** (2026-11-13) ✅ chọn | **1/27** (q20) ⚠️ | 5/5 | 0 | _chưa chấm_ | `fact_recall` **0.95** · leak 0/5 · rerank 0.56 s/câu · tổng 3.58 s (+13%) · q25 bị cắt ở 600 token ra → thực tế ngang `bge` |
