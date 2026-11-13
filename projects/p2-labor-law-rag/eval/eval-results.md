# Eval results — RAG Bộ luật Lao động

Mọi thay đổi RAG từ giờ đều ghi số vào đây (Notion Phase 02, Buổi 6). Mỗi lần chạy = 1 mục, **mới nhất ở trên**. Không
sửa số cũ — chỉ thêm mục mới.

Cách chạy: `uv run python projects/p2-labor-law-rag/eval/run_eval.py` (bật/tắt từng bước trong `__main__`).

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
| Baseline (2026-11-12) | 9/25 | 5/5 | ≥ 1 | 0.62 | naive RAG |
