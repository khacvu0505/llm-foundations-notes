# Buổi 24 — Phase 02 Buổi 12: Tổng hợp bảng evals + 1 trang phân tích (4h, T7)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · ~~Bài 0~~ · ~~Bài 1~~ · ~~Bài 2~~ (bỏ — bản rút gọn) · [x] Bài 3 trang phân tích ·
  ~~Bài 4~~ (bỏ — bản rút gọn) · [x] 4 câu phỏng vấn

## Handoff — dừng ở đây (cập nhật 2026-11-16)

_(Claude ghi để mở session mới — có thể ở **máy khác**. Đọc mục này trước.)_

**Buổi 24 xong — bản rút gọn** (2026-11-16): Setup + `projects/p2-labor-law-rag/ANALYSIS.md` + 4 câu phỏng vấn. Bỏ
Bài 0/1/2/4 (không chạy lại, không giám khảo LLM). ANALYSIS + câu phỏng vấn là **bản Claude viết** theo yêu cầu → user
nên đọc lại và sửa cho đúng giọng mình (dùng cho blog + phỏng vấn).

**Việc tiếp theo**: Phase 02 Buổi 13–15 = **Project #2** (repo session 25–27): app hoàn chỉnh upload/ingest → chat có
citation → UI Next.js streaming; trang admin (xem chunks, chạy lại evals); multi-turn (viết lại câu hỏi theo lịch sử);
vòng đời tài liệu (content_hash, xoá tài liệu → xoá chunks). Nguồn: Notion v46.

**Nợ mang theo**: q25 rỗng (token cap 600) + `grade_by_code` chưa đếm câu rỗng là lỗi; cột faithfulness/relevancy trống
từ sau baseline; test injection yếu.

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

**Đổi kế hoạch (2026-11-16, user chọn): bản rút gọn ~1h.** Giữ: bảng có sẵn trong `eval-results.md` + **1 trang
`ANALYSIS.md`** + 4 câu phỏng vấn. **Bỏ**: Bài 0 (ghi tay "q25 rỗng = lỗi"), giám khảo LLM (tiết kiệm ~$3.7 — cột
faithfulness/relevancy để trống, giải thích bằng số đo code), chạy lại. Lý do: Notion Exit criteria chỉ cần bảng +
giải thích từng bước nhảy; README Buổi 17 dùng lại. Bảng Setup dưới đây là quyết định **trước** khi rút gọn — giữ để
tham khảo.

| Mục | Quyết định + lý do |
| --- | --- |
| Số cũ hay đo lại (cùng 37 câu) | **Dùng số cũ** (user chọn) — $0 LLM bot, không chạy lại. Bù nhiễu bằng: (1) chấm lại run cũ bằng `grade_by_code` đã sửa (Bài 0) — $0; (2) giám khảo chỉ chấm **câu có đáp án chung** cho mọi dòng (q01–q25) → cột giám khảo so được. Ghi rõ hạn chế (30/37/39 câu, prompt đổi Buổi 23) trong trang phân tích |
| Giám khảo (metric, model) | **`gpt-5.4`**, faithfulness + relevancy (recall/precision LLM đã loại từ baseline) — khớp cột relevancy 0.62 cũ |
| Chạy mấy lần | User chọn "2 lần, giám khảo 1 lần" — nhưng dùng số cũ thì **không có lần chạy mới** → giám khảo chấm **1 lần** trên run có sẵn (_Claude diễn giải, chờ user xác nhận_) |
| Chỗ đặt trang phân tích | **`projects/p2-labor-law-rag/ANALYSIS.md`** + mục ngắn trỏ tới ở đầu `eval-results.md` |

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

- File: `projects/p2-labor-law-rag/ANALYSIS.md` (Claude viết theo "write for me", 2026-11-16, số liệu từ
  `eval-results.md` + notes Buổi 19–23; tự kiểm lại → sửa 1 câu sai về q25 ở bước rerank).
- Đáng nhất: **chunking** — từ chối nhầm 9/25 → 4/25, `fact_recall` 0.69 → 0.87, tiền bot −35%. Thứ hai: rerank
  (3/27 → 1/27, +13% độ trễ).
- Không như kỳ vọng: hybrid chỉ +1 câu; rewrite dao động + ×1.66 $ + ×2 độ trễ (không giữ); test injection quá yếu.
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

_(Câu mẫu Claude viết theo yêu cầu; số từ `eval-results.md` mục Buổi 21.)_

**Ít — và nói thẳng là ít.** Cùng bảng dieu-300, cùng 37 câu, chỉ đổi vector → hybrid (vector + từ khoá đã tách từ,
trộn RRF): từ chối nhầm **4/27 → 3/27** (14.8% → 11.1%, −1 câu), `fact_recall` **0.88 → 0.89**, độ trễ 2.89 → 3.18 s
(+10%). Đo **bằng code**: câu có đáp án mà bot từ chối + tỷ lệ dữ kiện bắt buộc có trong top-5. Thực chất là **+2 / −1**:
sửa q05 ("nghỉ việc" kéo đúng Điều 35–36) và q23, làm hỏng q02. Ít vì bộ eval chủ yếu câu đời thường, chunk theo Điều đã
có tiêu đề rõ nên vector tìm tốt; từ khoá mạnh nhất ở mã số / thuật ngữ hiếm — bộ eval chưa có nhiều câu loại đó. Giữ
hybrid vì nó là **nền cho rerank** (lấy top-20 rộng hơn).

### 2. Rerank đổi lấy bao nhiêu latency

_(Câu mẫu Claude viết theo yêu cầu; số từ `session22/notes.md` + `session23/notes.md`.)_

Thử 2 cross-encoder chạy local (Apple M2, GPU `mps`), lấy hybrid top-20 → chấm lại → giữ top-5. **`mmarco` (118M)**:
rerank **~0.56 s/câu** (median 0.46, max 1.18) → tổng **3.18 → 3.58 s (+13%)**; **`bge` (568M)**: ~3.0 s/câu → 5.93 s
(**+86%**). Đổi lại: từ chối nhầm **3/27 → 1/27** (`mmarco`) / 2/27 (`bge`), `fact_recall` 0.89 → 0.95, tiền LLM gần
như không đổi ($0.0055 → $0.0061) vì model chạy local. **Đáng** với `mmarco` — 2 câu đúng thêm cho +0.4 s; `bge` thì
không (gần gấp đôi độ trễ, không hơn). Lời thêm: điểm rerank **dùng lại được** làm guard → chặn 10/39 câu trước LLM
(0.47 s thay vì ~4.2 s), nên độ trễ trung bình cấu hình cuối còn **3.38 s** — thấp hơn cả lúc mới thêm rerank. Lưu ý:
`mmarco` 1/27 hơi "đẹp" vì q25 bị cắt ở 600 token, thực tế ngang `bge`.

### 3. Hallucination còn lại đến từ đâu

_(Câu mẫu Claude viết theo yêu cầu; số từ `session23/notes.md`, `ANALYSIS.md`.)_

Trên bộ eval, cấu hình cuối có **0 câu sai** đo được — phần còn lại nằm ở **4 chỗ**: (1) **retrieve hụt** → bot thiếu
dữ kiện: q20 (không dấu) không có đoạn đúng trong top-20 — may là guard từ chối; q25 (nhiều Điều) thiếu 1/3 dữ kiện → nguy
cơ trả lời **thiếu mà như đủ**; (2) **LLM không ổn định**: cùng q25, 4 lần chạy (Buổi 22 → 23) ra trả lời bị cắt / rỗng / từ
chối / rỗng — chạy 1 lần không thấy được; (3) **bộ kiểm có điểm mù**: code chỉ kiểm số liệu + Khoản **có trong** đoạn trích — số đúng nhưng gán
sai đối tượng, sai ý nghĩa, trích nhầm khoản cạnh bên đều lọt; giám khảo LLM thì cho faithfulness 1.0 cả câu sai q13;
(4) **nguồn sai**: bot "bám nguồn" một tài liệu sai / bị đầu độc thì vẫn sai — faithfulness cao không cứu được. → Tỷ lệ
bịa thật ≠ 0; nó nằm ở chỗ **bộ đo chưa nhìn tới**, nên cần thêm câu khó, chạy nhiều lần và đọc tay mẫu.

### 4. Khi nào RAG thua fine-tuning

_(Câu mẫu Claude viết theo yêu cầu. ⚠️ Phần so sánh là **kiến thức chung**, dự án này **chưa đo** fine-tuning — chỉ
các số về dự án là đo thật.)_

RAG giỏi đưa **kiến thức** vào lúc hỏi; fine-tuning giỏi dạy **hành vi**. RAG thua khi: (1) cần đổi **cách làm**, không
phải **biết thêm** — giọng văn, định dạng đầu ra cố định, phân loại / trích xuất theo schema: nhét tài liệu vào prompt
không dạy được kỹ năng; (2) kiến thức cần **tổng hợp từ rất nhiều nơi** hoặc là "lối suy luận" của ngành — không nằm gọn
trong 5 đoạn retrieve được; (3) **ngôn ngữ chuyên ngành / cách nói** mà model nền hiểu sai — retrieve đúng đoạn nhưng đọc
sai; (4) ràng buộc **độ trễ / chi phí / chạy offline** — mỗi câu RAG thêm bước retrieve + ~1–2 nghìn token context (dự án:
~1,000–1,800 token vào/câu). RAG **thắng** khi dữ liệu **hay đổi** (luật được hợp nhất lại), cần **trích dẫn**, cần
**phân quyền** (`allowed_groups`, leak 0/5) và **xoá được** tài liệu — đúng bài toán này. Thường không phải chọn 1: có thể
fine-tune **phần retrieve** (embedding / reranker — vd. cho câu không dấu như q20) mà vẫn giữ RAG.
