# Buổi 17 — Phase 02 Buổi 5: Xây Eval Set (2h)

Phase 02 — RAG + Evals. Nguồn: Notion "Phase 02 — RAG + Evals", **page version 46** (Claude đọc lại 2026-11-12 — có
thêm chi tiết so với bản đọc 2026-11-10).

Checklist Notion Buổi 5 ("Xây Eval Set — bước phân loại ứng viên"):

- Soạn **30 câu hỏi + đáp án chuẩn (ground truth)** từ dữ liệu domain: **20** câu trả lời được, **5** câu cần tổng hợp
  **nhiều đoạn**, **5** câu **KHÔNG** có trong tài liệu (test từ chối trả lời)
- Setup **RAGAS** (hoặc DeepEval): hiểu 4 metrics — **faithfulness, answer relevancy, context precision, context
  recall**

Ghi chú từ Notion bản mới:

- Buổi 4 có dòng "Chạy thử 10 câu hỏi, ghi cảm nhận chất lượng (chưa cần số)" — Buổi 16 mình chạy **6** câu.
- **Buổi 6** (4h) mới **chạy** eval → bảng baseline, đọc 5 case tệ nhất, tạo `eval-results.md`, tự chấm tay 20 câu để
  kiểm độ tin của RAGAS. Hôm nay chỉ **soạn bộ câu** + **hiểu metric**.
- **Buổi 8** thêm **5 câu test rò rỉ** (public hỏi nội dung internal); **Buổi 11** thêm **2 câu** prompt injection →
  hôm nay **chưa** cần câu quyền (Q4/Q5 Buổi 16 để dành Buổi 8).

| Phần                                          | Thời lượng | Làm ở đâu                    |
| --------------------------------------------- | ---------- | ---------------------------- |
| Setup: chỗ lưu + định dạng                    | ~10ph      | terminal                     |
| Bài 1: thiết kế 1 dòng eval (schema)           | ~15ph      | `notes.md`                   |
| Bài 2: 20 câu trả lời được                     | ~40ph      | file eval set                |
| Bài 3: 5 câu tổng hợp nhiều đoạn               | ~20ph      | file eval set                |
| Bài 4: 5 câu không có trong tài liệu           | ~10ph      | file eval set                |
| Bài 5: RAGAS — 4 metric + cài đặt              | ~25ph      | `notes.md` + terminal        |

---

## Setup (~10ph)

- [ ] Chỗ lưu — gợi ý `projects/p2-labor-law-rag/eval/eval_set.jsonl` (Project #2 dùng lại; Buổi 6 thêm
      `eval-results.md` cạnh đó). Tự quyết, ghi lý do.
- [ ] Định dạng: **JSONL** (mỗi dòng 1 câu, dễ thêm/sửa, git diff rõ) hay CSV/YAML? Ghi lý do.

## Bài 1 — Thiết kế 1 dòng eval (~15ph)

- [ ] Chọn trường cho mỗi câu, gợi ý:

  | Trường           | Ví dụ                                                    | Dùng để                               |
  | ---------------- | -------------------------------------------------------- | ------------------------------------- |
  | `id`             | `q01`                                                    | trỏ tới câu (không đổi theo thời gian) |
  | `question`       | "Thử việc tối đa bao lâu?"                                | đầu vào                               |
  | `reference`      | "Tối đa 180 ngày (quản lý DN), 60 ngày (cao đẳng+)…"     | đáp án chuẩn — RAGAS gọi là `reference` |
  | `sources`        | `["Điều 25"]`                                            | đoạn **phải** được tìm thấy (debug retrieve) |
  | `type`           | `single` / `multi` / `not_found`                          | đếm theo nhóm 20/5/5                  |
  | `group`          | `public`                                                 | quyền khi chạy                        |
  | `notes`          | "biến thể không dấu của q01"                              | ghi chú                               |

- [ ] Đáp án chuẩn **lấy từ DOCX**, không từ trí nhớ (của mình hay của LLM) — vì sao?

Tự trả lời:

1. Vì sao cần cả `reference` (đáp án) **và** `sources` (Điều nguồn)? Mỗi cái giúp chấm bước nào (retrieve / generate)?
2. Câu `not_found` thì `reference` ghi gì?

## Bài 2 — 20 câu trả lời được (~40ph)

- [ ] Rải đều nhiều **Chương** (hợp đồng, tiền lương, thời giờ làm việc, kỷ luật, lao động nữ, tranh chấp…), không dồn 1
      chỗ.
- [ ] Mỗi câu: đọc **đúng Điều** trong DOCX → viết `reference` ngắn gọn, đủ ý (vd. Điều 25 phải đủ **4 mức**).
- [ ] Trộn kiểu hỏi: hỏi thẳng, hỏi theo tình huống ("Tôi làm kế toán trình độ cao đẳng, thử việc được bao lâu?"), 1–2
      câu **không dấu** (như Q6 Buổi 16).
- [ ] **Tránh Điều 112** (nghỉ lễ, Tết): Quốc hội dự kiến biểu quyết sửa ngày 21/11/2026 (Buổi 13) → đáp án sắp đổi.
- [ ] Dùng lại câu Buổi 16: thử việc (Điều 25), thai sản (Điều 139), "thu viec toi da bao lau?".

## Bài 3 — 5 câu tổng hợp nhiều đoạn (~20ph)

- [ ] Câu cần **≥ 2 Điều** mới trả lời đủ, vd. so sánh 2 trường hợp, hoặc điều kiện ở Điều này + hệ quả ở Điều khác.
      `sources` ghi đủ các Điều.
- [ ] Dự đoán: naive RAG (k=5, chunk 500) có làm tốt loại câu này không? Vì sao?

## Bài 4 — 5 câu không có trong tài liệu (~10ph)

- [ ] Gợi ý trộn: hoàn toàn ngoài lề (giá vàng), **gần chủ đề nhưng thuộc luật khác** (mức đóng BHXH, thuế TNCN), chi
      tiết luật **không quy định** cụ thể. `reference` = câu `NOT_FOUND` của Buổi 16.
- [ ] Loại nào **khó** nhất cho bot? (Gợi ý: model "biết" câu trả lời từ lúc train.)

## Bài 5 — RAGAS: 4 metric + cài đặt (~25ph)

- [ ] Đọc docs 4 metric (https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/), điền bảng trong
      `notes.md`: đo gì, cần trường nào, chấm bước nào.
- [ ] `uv add ragas` (user tự chạy) — PyPI `ragas` 0.4.3 (phát hành 2026-01-13; Claude kiểm 2026-11-12).
- [ ] Ghép trường của mình ↔ trường RAGAS: `question` → `user_input`, câu trả lời bot → `response`, chunk lấy được →
      `retrieved_contexts`, `reference` → `reference`.
- [ ] (Nếu kịp) chạy thử RAGAS trên **1–2 câu** để biết API chạy được — chạy đủ 30 câu là việc Buổi 6.

Tự trả lời:

1. Metric nào **không cần** đáp án chuẩn? Metric nào chấm **retrieve**, metric nào chấm **generate**?
2. RAGAS dùng **LLM làm giám khảo** (LLM-as-judge) — rủi ro gì? (Notion Buổi 6: tự chấm tay 20 câu để kiểm.)

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Bạn xây eval set cho RAG thế nào? Gồm những loại câu nào, vì sao?
2. Giải thích 4 metric của RAGAS. Metric nào chấm retrieve, metric nào chấm generate?
3. Vì sao không tin tuyệt đối điểm LLM-as-judge?
