# Buổi 24 — Phase 02 Buổi 12: Tổng hợp bảng evals + 1 trang phân tích (4h, T7)

Đề bài: `exercises.md` cùng thư mục.

- [ ] Setup · [ ] Bài 0 sửa lỗi · [ ] Bài 1 chuỗi cấu hình · [ ] Bài 2 giám khảo · [ ] Bài 3 trang phân tích ·
  [ ] Bài 4 Exit criteria · [ ] 4 câu phỏng vấn

## Handoff — dừng ở đây (cập nhật 2026-11-16)

_(Claude ghi để mở session mới — có thể ở **máy khác**. Đọc mục này trước.)_

**Khung buổi 24 vừa tạo** (2026-11-16). Chưa làm bài nào.

**Việc tiếp theo**: Setup (4 quyết định) → Bài 0.

**Máy khác**: DB phải có **446 dòng** `law_chunks_dieu300` (444 luật + 2 chunk `injection-test`) — thiếu thì user chạy
`uv run --env-file .env python projects/p2-labor-law-rag/ingest_test.py --write`. Bài 1 cần cả bảng `law_chunks`
(216 dòng) cho dòng naive.

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nói "write for me" — khi đó viết +
giải thích); user tự làm git + ghi DB; mỗi lần đo đổi 1 thứ; notes tiếng Việt, có bảng + nguồn. Tải model treo →
`HF_HUB_DISABLE_XET=1`. Đọc Notion: xem memory `phase02-notion-syllabus`.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-16.)_

- Git: Buổi 23 đã commit + push (`bf79bb0`).
- Cấu hình cuối Buổi 23: dieu-300 + hybrid tách từ + rerank `mmarco` + guard `min_rerank=-1.5` + `prompt="delimiter"`
  — 39 câu: từ chối nhầm 1/27 (q20; **thật 2/27** vì q25 rỗng), từ chối đúng 5/5, `fact_recall` 0.95, leak 0/5,
  injection 0/2, Khoản đúng 55/55, 3.38 s/câu (`runs/dieu300-final-cite-guard-delim.jsonl`).
- Bảng trước/sau trong `eval/eval-results.md` có đủ dòng nhưng **khác bộ câu** (30 / 37 / 39) + prompt đổi ở Buổi 23;
  faithfulness/relevancy chỉ có ở baseline.

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Số cũ hay đo lại (cùng 37 câu) | |
| Giám khảo (metric, model) | |
| Chạy mấy lần | |
| Chỗ đặt trang phân tích | |

## Bài 0 — Sửa lỗi trước khi đo

- `grade_by_code` đếm câu rỗng:
- q25 (token suy luận? `max_output_tokens` mới):
- Tự trả lời:

## Bài 1 — Chuỗi cấu hình (cùng 37 câu)

| Dòng | Từ chối nhầm | Từ chối đúng | `fact_recall` | Leak | Trích đúng chỗ | Số liệu bám nguồn | s/câu | $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1. naive | | | | | | | | |
| 2. + chunking | | | | | | | | |
| 3. + hybrid | | | | | | | | |
| 4. + rerank | | | | | | | | |
| 5. + guard + delimiter | | | | | | | | |

- So với số cũ:
- Tự trả lời:

## Bài 2 — Giám khảo

| Dòng | Faithfulness | Relevancy | Tiền giám khảo |
| --- | --- | --- | --- |
| 1. naive | | | |
| 2. + chunking | | | |
| 3. + hybrid | | | |
| 4. + rerank | | | |
| 5. + guard + delimiter | | | |

- Câu giám khảo ↔ code nói ngược nhau:
- Tự trả lời:

## Bài 3 — Trang phân tích

- File:
- Đáng nhất:
- Không như kỳ vọng:
- Tự trả lời:

## Bài 4 — Exit criteria

| Tiêu chí (Notion) | Đạt? | Bằng chứng |
| --- | --- | --- |
| Bảng evals trước/sau đầy đủ, giải thích được từng bước nhảy số | | |
| Rebuild test 2h pass | ⏳ Buổi 18 | |
| Trả lời trôi 4 câu (RAG vs fine-tuning, hallucination còn lại, hybrid %, rerank latency) | | |
| Project #2 demo sống + README có số liệu | ⏳ Buổi 13–17 | |
| Leak rate = 0 trong eval set | | |

## Câu phỏng vấn cuối buổi

### 1. Hybrid search cải thiện bao nhiêu %, đo bằng gì

### 2. Rerank đổi lấy bao nhiêu latency

### 3. Hallucination còn lại đến từ đâu

### 4. Khi nào RAG thua fine-tuning
