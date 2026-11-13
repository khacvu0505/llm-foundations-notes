# Buổi 18 — Phase 02 Buổi 6: Đo Baseline (4h)

Phase 02 — RAG + Evals. Nguồn: Notion "Phase 02 — RAG + Evals", page version 46 (Claude đọc 2026-11-12).

Checklist Notion Buổi 6:

- Chạy eval set trên naive RAG → **bảng baseline** (vd. faithfulness 0.6x)
- Đọc kỹ **5 case tệ nhất**: lỗi do retrieval hay generation? — kỹ năng debug RAG bắt đầu từ đây
- Tạo file **`eval-results.md`** trong repo: mọi thay đổi từ giờ đều ghi số vào đây
- Kiểm tra độ tin cậy (~1h): **tự chấm tay 20 câu** (bám nguồn: có/không), so với điểm faithfulness → ghi **tỉ lệ
  khớp** (vd. 17/20). Lệch nhiều → xem lại judge model / prompt chấm trước khi tin bảng số
- 📌 Điểm do LLM chấm (LLM-as-judge) — chưa kiểm tra thì chưa chắc con số phản ánh đúng chất lượng

Nối với buổi trước:

- Buổi 16: naive RAG `answer()` (retrieve k=5 có lọc quyền → context đánh số → `gpt-6-luna`) ở
  `weeks/week03/session16/exercises.py`.
- Buổi 17: `projects/p2-labor-law-rag/eval/eval_set.jsonl` (30 câu: 20 single / 5 multi / 5 not_found); chấm bằng
  **DeepEval 4.3.4** (4 metric, ngưỡng mặc định 0.5); 5 câu `not_found` chấm riêng bằng so chuỗi.

**Nguyên tắc:** baseline = đo **đúng** bản naive RAG Buổi 16, **không sửa gì** trong lúc đo (thấy lỗi → ghi lại, sửa ở
Buổi 7+). Đổi code RAG giữa chừng thì con số không còn là baseline.

| Phần                                                       | Thời lượng | Làm ở đâu            |
| ---------------------------------------------------------- | ---------- | -------------------- |
| Setup: chỗ để code, chọn giám khảo                          | ~20ph      | `notes.md`           |
| Bài 1: chạy bot trên 30 câu → lưu kết quả thô                | ~40ph      | runner + `runs/`     |
| Bài 2: chấm bằng code (Điều nguồn, từ chối)                  | ~25ph      | runner               |
| Bài 3: chấm 4 metric DeepEval cho 25 câu                     | ~50ph      | runner               |
| Bài 4: `eval-results.md` — bảng baseline                     | ~20ph      | `eval-results.md`    |
| Bài 5: 5 case tệ nhất — retrieve hay generate?               | ~40ph      | `notes.md`           |
| Bài 6: chấm tay 20 câu, so với faithfulness                  | ~60ph      | `notes.md`           |

**Quy tắc DB:** chỉ đọc. **Chi phí:** có gọi LLM nhiều (bot 30 câu + giám khảo 25 câu × 4 metric) — ước ở Setup.

---

## Setup (~20ph)

- [ ] **Chỗ để code.** Từ giờ RAG sẽ được sửa ở Buổi 7–11 và **chạy lại eval sau mỗi lần sửa** → nên có 1 chỗ cố định.
      Gợi ý: chép code Buổi 16 sang `projects/p2-labor-law-rag/rag.py` (bot) + `projects/p2-labor-law-rag/eval/run_eval.py`
      (chấm). Hoặc tiếp tục kiểu `weeks/week03/session18/exercises.py`. Tự quyết, ghi lý do.
- [ ] **Chọn model giám khảo** (Buổi 17 Bài 5: khác model bot, mạnh hơn). Bot đang dùng `gpt-6-luna`.
- [ ] Ước chi phí trước khi chạy; nhớ **hard limit** chi tiêu OpenAI (còn treo từ Phase 01).

## Bài 1 — Chạy bot trên 30 câu, lưu kết quả thô (~40ph)

- [ ] Đọc `eval_set.jsonl` → mỗi câu gọi `answer(conn, question, group)` → lưu 1 dòng JSONL vào
      `projects/p2-labor-law-rag/eval/runs/baseline.jsonl`: `id`, câu trả lời, các chunk đã lấy (heading + **content**
      đầy đủ + sim), `cited`, token, chi phí, thời gian.
- [ ] Tách **chạy bot** khỏi **chấm điểm** — vì sao? (Gợi ý: chấm lại bằng giám khảo khác mà không phải chạy lại bot.)

## Bài 2 — Chấm bằng code, không cần LLM (~25ph)

- [ ] **Hit Điều nguồn** (25 câu có `sources`): mỗi Điều trong `sources` có xuất hiện trong top-5 không (so `heading`
      **hoặc** nội dung chứa "Điều N.", Buổi 17 Bài 1) → vd. 22/25.
- [ ] **Từ chối đúng** (5 câu `not_found`): `answer.strip() == NOT_FOUND` → vd. 4/5.
- [ ] **Từ chối nhầm** (25 câu có đáp án): bot trả `NOT_FOUND` dù có đáp án → vd. q20 không dấu.

## Bài 3 — DeepEval 4 metric cho 25 câu (~50ph)

- [ ] Dựng `LLMTestCase` (Buổi 17: `input`, `actual_output`, `expected_output`, `retrieval_context`) từ `baseline.jsonl`
      + `eval_set.jsonl`.
- [ ] 4 metric với `model=<giám khảo>`, ngưỡng **giữ 0.5** cho mọi lần chạy (để so sánh công bằng).
- [ ] Lưu điểm + **`reason`** từng câu, từng metric → `runs/baseline_scores.jsonl`.
- [ ] Ghi chi phí giám khảo thật.

## Bài 4 — `eval-results.md` (~20ph)

- [ ] Tạo `projects/p2-labor-law-rag/eval/eval-results.md`: bảng baseline (trung bình 4 metric, tỷ lệ đạt, hit Điều
      nguồn, từ chối đúng/nhầm, chi phí + thời gian/câu), ghi rõ **cấu hình** (model bot, giám khảo, k, chunk size,
      ngưỡng, ngày, commit).
- [ ] Bảng chia theo **loại câu** (single / multi): loại nào kéo điểm xuống?

## Bài 5 — 5 case tệ nhất (~40ph)

- [ ] Chọn 5 câu điểm thấp nhất → với mỗi câu: đọc chunk đã lấy + câu trả lời + `reason` → **lỗi retrieve hay
      generate** (sơ đồ debug Buổi 16) → buổi nào sẽ sửa (7 chunking, 8 rewrite, 9 hybrid, 10 rerank, 11 hallucination).

## Bài 6 — Chấm tay 20 câu, kiểm giám khảo (~60ph)

- [ ] Chọn 20 câu (trong 25), **tự đọc** câu trả lời + chunk → mỗi câu "bám nguồn: có/không" **trước khi** xem điểm
      faithfulness (tránh bị điểm dắt mũi).
- [ ] So với faithfulness (≥ 0.5 = "có") → **tỉ lệ khớp** (vd. 17/20) → ghi vào `eval-results.md`.
- [ ] Câu nào lệch → đọc `reason` → giám khảo sai hay mình sai?

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Baseline của bạn là bao nhiêu, đo thế nào? Vì sao phải có baseline trước khi cải tiến?
2. Kể 1 case tệ: lỗi ở đâu, bạn phát hiện bằng cách nào?
3. Làm sao biết điểm LLM-as-judge đáng tin?
