# Buổi 24 — Phase 02 Buổi 12: Tổng hợp bảng evals + 1 trang phân tích (4h, T7)

Phase 02 — RAG + Evals, cuối Tuần 4 "Cải tiến có đo lường". Nguồn: Notion "Phase 02 — RAG + Evals", page version 46
(Claude đọc 2026-11-16 qua `curl …/api/v3/loadPageChunk` — Notion MCP + WebFetch không đọc được link công khai).

Checklist Notion Buổi 12:

- **Hoàn thiện bảng trước/sau toàn bộ**: naive → +chunking → +hybrid → +rerank (vd. faithfulness 0.62 → 0.85)
- **Viết 1 trang phân tích**: cải tiến nào **đáng nhất**, cái nào **không như kỳ vọng**, **vì sao**
- 📌 Trang này = nội dung chính của **blog post** sau này + **chuyện kể phỏng vấn**

Nối với Exit criteria Phase 02 (cổng qua Phase 03): "Bảng evals trước/sau đầy đủ, **giải thích được từng bước nhảy
số**" + trả lời trôi: "Khi nào RAG thua fine-tuning? Hallucination còn lại đến từ đâu? Hybrid search cải thiện bao
nhiêu %, đo bằng gì? Rerank đổi lấy bao nhiêu latency?"

Claude kiểm trước (2026-11-16, đọc file run + `eval-results.md` + `SELECT`, không gọi API):

| Hiện trạng | Bằng chứng |
| --- | --- |
| Bảng trước/sau **đã có đủ dòng** naive → … → cấu hình cuối Buổi 23, nhưng các dòng đo trên **bộ câu khác nhau**: baseline + dieu-300 = **30 câu**, vector/hybrid/rerank = **37**, cấu hình cuối = **39** | `wc -l runs/{baseline,dieu-300,dieu300-vector,dieu300-hybrid-seg,dieu300-hybrid-seg-rerank-mmarco,dieu300-final-cite-guard-delim}.jsonl` |
| Prompt **đã đổi** ở Buổi 23 (quy tắc 2 trích Khoản) → chạy lại cấu hình cũ hôm nay **không** giống y lúc đó | `rag.py` `INSTRUCTIONS` |
| Cột faithfulness / relevancy: **chỉ baseline có điểm** (relevancy `gpt-5.4` 0.62), mọi dòng sau "_chưa chấm_" | `eval-results.md` bảng cuối; `runs/*scores*.jsonl` chỉ có 2 file baseline |
| Chi phí giám khảo (baseline, 25 câu có đáp án): `gpt-5.4` faithfulness **$0.78** + relevancy **$0.15**; `gpt-5.4-mini` **$0.23** + **$0.04** | trường `cost` trong `runs/baseline_scores*.jsonl` |
| Bài học baseline: giám khảo LLM **không đo được recall** trên dữ liệu này → recall đo bằng code (`fact_recall`) | `eval-results.md` "Kết luận baseline" mục 3 |
| 4 bảng vẫn còn trong DB → chạy lại được mọi cấu hình cũ: `law_chunks` 216 · `law_chunks_dieu` 321 · `law_chunks_dieu800` 260 · `law_chunks_dieu300` 446 | `SELECT count(*)` |
| Lỗi mở: **q25 rỗng** (chạm `max_output_tokens=600`, hỏng 3/4 lần Buổi 23) và `grade_by_code` **không tính câu rỗng** là lỗi → bảng đang ghi 1/27, thật là 2/27 | `session23/notes.md` Handoff |
| `eval-results.md` quy ước "mới nhất ở trên", nhưng Buổi 22–23 **chưa có mục riêng** ở đầu file (chỉ thêm dòng vào bảng cuối) | `grep -n "^## " eval-results.md` |

| Phần | Thời lượng | Làm ở đâu |
| --- | --- | --- |
| Setup: 4 quyết định (đo lại hay dùng số cũ, giám khảo nào, chạy mấy lần, chỗ đặt trang phân tích) | ~20ph | `notes.md` |
| Bài 0: sửa lỗi q25 + `grade_by_code` đếm câu rỗng | ~20ph | `rag.py` + `run_eval.py` |
| Bài 1: chạy lại chuỗi cấu hình trên **cùng 1 bộ câu** | ~60ph | `run_eval.py` |
| Bài 2: chấm faithfulness + relevancy, đọc tay chỗ lệch | ~50ph | `run_eval.py` + `runs/` |
| Bài 3: viết **1 trang phân tích** | ~60ph | file phân tích (Setup chọn chỗ) |
| Bài 4: tự kiểm Exit criteria + câu phỏng vấn | ~30ph | `notes.md` |

**Quy tắc đo:** mọi dòng trong bảng cuối **cùng bộ câu, cùng prompt, cùng giám khảo** — chỉ khác đúng 1 bước cải tiến.
**Không sửa số cũ** trong `eval-results.md` — thêm mục mới. **Không ghi DB** buổi này (chỉ đọc).

---

## Setup (~20ph)

- [ ] **Số cũ hay đo lại?** (a) **Đo lại** 5 cấu hình chính trên **cùng 37 câu** (q01–q37, bỏ q38/q39 vì tài liệu
      injection chỉ có ở `law_chunks_dieu300`) với code hôm nay — tiền LLM ~$0.006/lần × 5 ≈ $0.03, số so được trực
      tiếp; (b) **dùng số cũ** — $0, nhưng 30/37/39 câu + prompt khác → bước nhảy lẫn nhiễu. Gợi ý: (a), giữ số cũ làm
      tham khảo.
- [ ] **Giám khảo**: metric nào, model nào. Recall/precision bằng LLM đã bị loại (baseline). Còn faithfulness +
      relevancy: `gpt-5.4` (~$1/lần chạy, khớp cột 0.62 cũ) hay `gpt-5.4-mini` (~$0.3/lần chạy, từng lệch). Gợi ý:
      `gpt-5.4`, chỉ trên câu có đáp án → 5 cấu hình ≈ **$5** (ước tính từ chi phí baseline, chưa kiểm).
- [ ] **Chạy mấy lần**: LLM dao động (q25; rewrite q17 ↔ q24). (a) 1 lần — rẻ, ghi rõ hạn chế; (b) **2 lần** cho số đo
      bằng code (~$0.06 tổng), giám khảo chỉ 1 lần. Gợi ý: (b).
- [ ] **Chỗ đặt trang phân tích**: `projects/p2-labor-law-rag/ANALYSIS.md` (đi cùng code, dễ đưa vào README Buổi 17)
      hay mục đầu `eval-results.md`. Gợi ý: file riêng + mục ngắn trỏ tới nó trong `eval-results.md`.

## Bài 0 — Sửa lỗi trước khi đo (~20ph)

- [ ] `grade_by_code`: câu **rỗng** = lỗi (đếm riêng "rỗng", tính vào "không trả lời được"), không còn lọt vào "có
      trả lời".
- [ ] q25: tìm vì sao chạm 600 token mà ra rỗng — xem `resp.usage` có token **suy luận** (reasoning) không. Tăng
      `max_output_tokens` (vd. 1200) — áp dụng **cho mọi dòng** khi đo lại để công bằng. Chạy riêng q25 × 3 lần để kiểm.

Tự trả lời:

1. Vì sao 1 lỗi ở **bộ chấm** (đếm câu rỗng) nguy hiểm hơn 1 lỗi ở bot?

## Bài 1 — Chuỗi cấu hình trên cùng 1 bộ câu (~60ph)

Mỗi dòng **chỉ thêm 1 bước** so với dòng trên:

| Dòng | Bảng | Retrieve | Sau retrieve | Prompt |
| --- | --- | --- | --- | --- |
| 1. naive | `law_chunks` (fixed 500) | vector | — | `rule4` |
| 2. + chunking | `law_chunks_dieu300` | vector | — | `rule4` |
| 3. + hybrid | `law_chunks_dieu300` | vector + `fts_seg` (RRF) | — | `rule4` |
| 4. + rerank | `law_chunks_dieu300` | hybrid top-20 | `mmarco` → top-5 | `rule4` |
| 5. + guard + delimiter (cuối) | `law_chunks_dieu300` | hybrid top-20 | `mmarco` + `min_rerank=-1.5` | `delimiter` |

- [ ] Chạy 5 dòng (× số lần chọn ở Setup), `only_ids` = q01–q37. Rewrite + metadata (Buổi 20) **không** nằm trong chuỗi
      vì không giữ lại — ghi 1 dòng tham khảo từ số cũ.
- [ ] Mỗi dòng ghi: từ chối nhầm (có tính câu rỗng), từ chối đúng, `fact_recall`, leak, `check_citations` (trích đúng
      chỗ, số liệu bám nguồn), s/câu, $.
- [ ] So với số cũ: bước nhảy có **giữ hướng** không? Chỗ nào lệch → vì bộ câu, vì prompt, hay vì dao động?

Tự trả lời:

1. Vì sao phải đo lại cả chuỗi thay vì ghép số các buổi trước?

## Bài 2 — Giám khảo: faithfulness + relevancy (~50ph)

- [ ] `grade_deepeval` cho 5 dòng (model theo Setup), chỉ câu có đáp án. Ghi tiền thật vào notes.
- [ ] Bảng: faithfulness / relevancy theo dòng. Có bước nào làm **giảm** điểm không?
- [ ] Đọc tay 3–5 câu giám khảo và số đo bằng code **nói ngược nhau** (vd. faithfulness cao nhưng `fact_recall` thấp —
      nhớ q13 baseline: sai mà giám khảo cho điểm tối đa).

Tự trả lời:

1. Faithfulness cao có nghĩa là câu trả lời **đúng** không?

## Bài 3 — 1 trang phân tích (~60ph)

Viết cho người đọc **không** theo dõi các buổi (blog / người phỏng vấn). Dàn ý gợi ý:

- [ ] **Bối cảnh** (3 câu): bot tra cứu Bộ luật Lao động, 37 câu eval (loại câu), đo bằng gì.
- [ ] **Bảng cuối** (từ Bài 1 + 2) — mỗi bước nhảy số kèm **1 câu "vì sao"** + ví dụ 1 câu hỏi cụ thể đổi kết quả.
- [ ] **Đáng nhất**: bước nào cho nhiều nhất trên mỗi $ / mỗi ms, có số.
- [ ] **Không như kỳ vọng**: vd. hybrid chỉ +1 câu, rewrite dao động, test injection quá yếu (0/6 kể cả không phòng thủ)
      — và **vì sao** (đặc điểm dữ liệu / bộ eval).
- [ ] **Còn lại**: hallucination / từ chối nhầm còn đến từ đâu (q20 không dấu, q25…), việc tiếp theo.
- [ ] **Hạn chế đo**: 37 câu, ngưỡng guard chọn trên chính bộ test, giám khảo LLM có lệch.

Tự trả lời:

1. Nếu chỉ được giữ **1** cải tiến, bạn giữ cái nào? Bảo vệ bằng số.

## Bài 4 — Exit criteria + đóng Tuần 4 (~30ph)

- [ ] Đánh dấu Exit criteria nào đã đạt (bảng evals + giải thích từng bước nhảy · leak rate = 0) / còn lại (rebuild
      test, Project #2 demo).
- [ ] Thêm mục Buổi 24 lên **đầu** `eval-results.md` (+ bù mục ngắn cho Buổi 22–23 nếu muốn giữ quy ước "mới nhất ở
      trên").

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes — lấy từ Exit criteria Notion)

1. Hybrid search cải thiện bao nhiêu %, đo bằng gì?
2. Rerank đổi lấy bao nhiêu latency? Đáng không?
3. Hallucination còn lại đến từ đâu?
4. Khi nào RAG thua fine-tuning?
