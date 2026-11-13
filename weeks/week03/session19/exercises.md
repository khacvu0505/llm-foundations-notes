# Buổi 19 — Phase 02 Buổi 7: Chunking nâng cao (2h)

Phase 02 — RAG + Evals, **Tuần 4 — "Cải tiến có đo lường"** (mỗi buổi: 1 cải tiến → đo lại → ghi số). Nguồn: Notion
"Phase 02 — RAG + Evals", page version 46 (Claude đọc 2026-11-12).

Checklist Notion Buổi 7:

- Recursive character splitting **theo cấu trúc** (heading, đoạn); thử **2–3 chunk size**
- **Đo lại → ghi bảng.** Trả lời được: "chunk size chọn thế nào, vì sao?"
- Với chunk size tốt nhất, thử **overlap 0 / 50 / 100** token → đo lại **context recall**, ghi vào `eval-results.md`

Nối với buổi trước (Buổi 18 — baseline, `projects/p2-labor-law-rag/eval/eval-results.md`):

- **Từ chối nhầm 9/25**, 8/9 gốc ở retrieve; **4 câu** (q03, q09, q17, q22) do tiêu đề Điều nằm **cuối** chunk, thân
  điều ở chunk sau. Độ dài 220 Điều (Buổi 15): median 353 token, **70 Điều > 500**, dài nhất 3,682, 10 Điều < 100.
- Lỗi phụ đã ghi: heading cụt "Điều 103… nâ"; số chú thích dính chữ ("1.4", "THI HÀNH6").
- **DeepEval recall không tin được** → đo retrieve bằng **code** (`key_facts`), giám khảo `gpt-5.4-mini` chỉ cho
  faithfulness + relevancy (relevancy tính trên câu **không** từ chối).

**Quy tắc đo:** mỗi lần chỉ đổi **1 thứ** (chunking), giữ nguyên bot (k=5, prompt, model), cùng 30 câu, cùng giám khảo,
cùng ngưỡng → mới so được với baseline.

| Phần                                                         | Thời lượng | Làm ở đâu                  |
| ------------------------------------------------------------ | ---------- | -------------------------- |
| Setup: chỗ để code, cách lưu nhiều bộ chunk                  | ~10ph      | `notes.md`                 |
| Bài 1: `key_facts` + chấm recall bằng code (và chấm lại baseline) | ~25ph | eval set + `run_eval.py`  |
| Bài 2: chunker theo cấu trúc (Điều → Khoản, gắn tiêu đề)      | ~35ph      | chunker mới                |
| Bài 3: nạp vào bảng mới (user chạy)                           | ~10ph      | DB                         |
| Bài 4: chạy eval → so với baseline → `eval-results.md`        | ~25ph      | `run_eval.py`              |
| Bài 5: thử 2–3 cỡ chunk (+ overlap nếu kịp)                   | ~15ph+     | lặp Bài 2–4                |

**Quy tắc DB:** tạo bảng / nạp dữ liệu = **ghi DB** → user chạy. Claude chỉ `SELECT`.

---

## Setup (~10ph)

- [ ] **Chunker mới để ở đâu?** Gợi ý `projects/p2-labor-law-rag/chunking.py` (đọc DOCX, làm sạch, các kiểu chunk) —
      Project #2 dùng lại. Code Buổi 15 vẫn ở `weeks/week03/session15/exercises.py`.
- [ ] **Lưu nhiều bộ chunk thế nào để so?** Gợi ý mỗi kiểu chunk **1 bảng riêng** cùng cấu trúc với `law_chunks`
      (`CREATE TABLE law_chunks_dieu (LIKE law_chunks INCLUDING ALL)`), và `rag.retrieve(…, table=…)`. Giữ nguyên
      `law_chunks` = baseline để chạy lại khi cần.

## Bài 1 — `key_facts` + chấm recall bằng code (~25ph)

- [ ] Thêm trường **`key_facts`** vào 25 câu có đáp án trong `eval_set.jsonl`: các **chuỗi ngắn y nguyên trong luật**
      mà đoạn đúng **phải** chứa (vd. q03 `["không quá 36 tháng"]`, q01 `["180 ngày", "60 ngày", "30 ngày", "06 ngày làm
      việc"]`). Chuỗi phải **có thật** trong DOCX — kiểm bằng code.
- [ ] Hàm `fact_recall(chunks, key_facts)` = số dữ kiện có trong top-5 / tổng → điểm 0–1, **không cần LLM**.
- [ ] **Chấm lại baseline** bằng `fact_recall` (từ `runs/baseline.jsonl`, không chạy lại bot) → con số "trước" thật.

Tự trả lời:

1. `key_facts` khác `sources` (Buổi 17) ở chỗ nào? Vì sao `source_hit` bị lạc quan còn `fact_recall` thì không?
2. Bẫy của `fact_recall`: chuỗi "45 ngày" có ở cả Điều 35 lẫn 36 (Buổi 18 Bài 5). Chọn `key_facts` thế nào để tránh?

## Bài 2 — Chunker theo cấu trúc (~35ph)

- [ ] Cắt theo **Điều**: mỗi Điều 1 chunk; Điều **dài hơn `max_tokens`** → chia theo **Khoản** (dòng bắt đầu "1.", "2."…),
      gộp các Khoản liền nhau cho tới gần `max_tokens`.
- [ ] **Mỗi chunk bắt đầu bằng tiêu đề** "Điều N. Tên điều" (kể cả phần tách ra) → luôn trích được nguồn, vector luôn
      có "chủ đề".
- [ ] Làm sạch thêm: bỏ **số chú thích** dính chữ ("1.4" → "1.", "THI HÀNH6" → "THI HÀNH"); `heading` lưu **đầy đủ**.
- [ ] Đo: số chunk, min / median / max token, bao nhiêu Điều phải tách. Kiểm Điều 25, 20, 107, 115 nằm **trọn** trong
      chunk của mình.

Tự trả lời:

1. Vì sao gắn tiêu đề vào **đầu mỗi chunk** (cả phần tách)? Nối với Buổi 16 câu 5 (q05 nhầm Điều 36/35).
2. Điều rất ngắn (< 100 token) có nên gộp với Điều kế bên không? Được/mất gì?

## Bài 3 — Nạp vào bảng mới (~10ph, user chạy)

- [ ] Tạo bảng mới (Setup) → nạp bằng `ingest` Buổi 15 (embed trước, 1 transaction), sửa để nhận tên bảng.
- [ ] Kiểm (Claude `SELECT`): số dòng, `heading` không rỗng, không còn `�`, không còn tiêu đề cụt.

## Bài 4 — Chạy eval, so với baseline (~25ph)

- [ ] `run_bot(…, table="law_chunks_dieu")` → `runs/dieu-<size>.jsonl` (k, prompt, model **giữ nguyên**).
- [ ] Chấm: từ chối đúng / nhầm, `fact_recall` (code), faithfulness + relevancy (`gpt-5.4-mini`).
- [ ] Ghi mục mới trong `eval-results.md` + thêm dòng vào **bảng trước/sau**. q03, q09, q17, q22 đã được trả lời chưa?
      Có câu nào **tệ đi** không?

## Bài 5 — Thử 2–3 cỡ chunk (+ overlap) (~15ph+)

- [ ] Lặp Bài 2–4 với 2–3 `max_tokens` (vd. 300 / 500 / 800). Cỡ nào tốt nhất theo `fact_recall` + từ chối nhầm?
- [ ] (Nếu kịp) với cỡ tốt nhất, thử overlap **0 / 50 / 100** giữa các phần tách của Điều dài → đo `fact_recall`.
- [ ] Mỗi lần chạy tốn ~$0.007 (bot) + ~$0.25 (giám khảo mini, 2 metric) — chạy giám khảo chỉ khi cần.

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Chunk size chọn thế nào, vì sao? (Notion yêu cầu trả lời được câu này.)
2. Chunk theo cấu trúc khác fixed-size thế nào? Cải thiện bao nhiêu, đo bằng gì?
3. Có cải tiến nào làm một số câu tệ đi không? Bạn xử lý thế nào?
