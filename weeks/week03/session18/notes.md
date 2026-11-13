# Buổi 18 — Phase 02 Buổi 6: Đo Baseline (4h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 chạy 30 câu · [x] Bài 2 chấm bằng code · [x] Bài 3 DeepEval (🚩 giám khảo nghi ngờ) · [x] Bài 4 eval-results.md ·
  [x] Bài 5 5 case tệ nhất · [x] Bài 6 chấm tay 20 câu (Claude chấm — user nên xem lại) · [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-12)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 18 xong** (2026-11-13). Code: `projects/p2-labor-law-rag/rag.py` (bot Buổi 16 y nguyên + trả `chunks`) +
`eval/run_eval.py` (`run_bot`, `grade_by_code`, `grade_deepeval(judge=…)`). Kết quả: `eval/runs/` (`baseline.jsonl`,
`baseline_scores.jsonl` mini, `baseline_scores_gpt-5.4.jsonl`, `baseline_handgrade.md`) + **`eval/eval-results.md`**.
Baseline: từ chối đúng **5/5**, **từ chối nhầm 9/25**, 8/9 gốc ở retrieve (chunking); DeepEval recall **không tin
được** (cả 2 giám khảo); faithfulness khớp 18/20 (Claude chấm — **user nên tự xem lại q03, q07, q13**). Chi phí giám
khảo tổng **$2.00**.

**Việc tiếp theo**: (1) user xem lại 3 câu chấm tay + commit Buổi 18 (`weeks/week03/session18`,
`projects/p2-labor-law-rag/rag.py`, `projects/p2-labor-law-rag/eval/`) + thêm `.deepeval/` vào `.gitignore` + (tuỳ)
`DEEPEVAL_TELEMETRY_OPT_OUT=1` vào `.env`; (2) **Buổi 19 = Phase 02 Buổi 7 — Chunking nâng cao**: chunk theo Điều/Khoản
+ gắn tiêu đề; **trước khi đo**: thêm `key_facts` vào `eval_set.jsonl` + hàm đếm dữ kiện trong top-5; chạy lại eval →
cột mới trong bảng trước/sau; giám khảo `gpt-5.4-mini` (relevancy chỉ tính câu không từ chối).

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + mọi lệnh
ghi DB (hôm nay chỉ đọc); **không sửa RAG** trong lúc đo baseline; notes tiếng Việt, có bảng + nguồn.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-12.)_

- Git: Buổi 17 đã commit (`8159fd7`), working tree sạch. DB `p2-pgvector` Up.
- DeepEval 4.3.4: model giám khảo mặc định `DEFAULT_GPT_MODEL = "gpt-5.4"`
  (`deepeval/models/llms/constants.py:5`); ngưỡng mặc định 0.5. Bảng model của DeepEval có `gpt-6-luna`, `gpt-6-sol`,
  `gpt-6-astra`, `gpt-5.4`… (dòng 367–558).
- Model API key truy cập được (`client.models.list()`, read-only): có `gpt-6-luna`, `gpt-6-sol`, `gpt-6-astra`,
  `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`…
- Giá theo **bảng của DeepEval** ($/1M token vào/ra — _không phải trang giá OpenAI, chưa kiểm_): `gpt-6-luna` 0.10/0.50
  · `gpt-5.4-mini` 0.75/4.50 · `gpt-6-sol` 2.00/10.00 · `gpt-5.4` 2.50/15.00 · `gpt-5.5` 5.00/30.00 · `gpt-6-astra`
  10.00/50.00. Tất cả đều `supports_temperature=False`.

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Chỗ để code bot + runner | `projects/p2-labor-law-rag/rag.py` (bot, chép **y nguyên** Buổi 16) + `projects/p2-labor-law-rag/eval/run_eval.py` (chạy + chấm) — RAG sẽ sửa ở Buổi 19+ và eval chạy lại sau mỗi lần → cần chỗ cố định (user đồng ý 2026-11-12) |
| Model giám khảo | **`gpt-5.4-mini`** — rẻ, khác dòng với bot `gpt-6-luna` (giảm rủi ro tự chấm mình). User lo chi phí → bắt đầu rẻ; **Bài 6 quyết định**: khớp chấm tay cao (≥ 17/20) thì giữ, thấp thì đổi `gpt-5.4` (chỉ chấm lại, không chạy lại bot) |
| Ước chi phí | Giám khảo ~**$1** (rất thô: ~3 lần gọi/metric × ~2,500 token; giá theo bảng DeepEval 0.75/4.50 $/1M, chưa kiểm). Bot 30 câu × ~$0.00024 ≈ **$0.007**. Bài 3: chấm thử **3 câu** đo chi phí thật trước khi chạy 22 câu còn lại |

## Bài 1 — Chạy bot

**Kết quả chạy** (user chạy `run_eval.py` 2026-11-12 → `projects/p2-labor-law-rag/eval/runs/baseline.jsonl`; Claude kiểm
read-only): **30 dòng**, mỗi dòng đủ 5 chunk có `content`; tổng chi phí bot **$0.0068**; thời gian/câu trung bình
**3.55s**, median 2.91s, max 12.27s (q01 — câu đầu, có thể do khởi động kết nối — _giả thuyết_); `bad_cites` = 0.

⚠️ **Phát hiện lớn:** bot trả `NOT_FOUND` cho **14/30** câu: 5 câu `not_found` (q26–q30, đúng) + **9 câu có đáp án**
(**từ chối nhầm**): q03, q05, q09, q16, q17, q20, q22, q23, q25. → Bài 2 kiểm Điều nguồn có trong top-5 không để biết
lỗi retrieve hay generate. **Không sửa** (đang đo baseline). Ví dụ đúng: q19 (tình huống) "Tối đa 60 ngày [1] (Điều
25)." ✅; q20 (không dấu) → `NOT_FOUND` như Buổi 16.

- **Vì sao tách chạy bot khỏi chấm điểm** _(câu mẫu Claude, user nhờ)_:

  | Lý do | Giải thích |
  | --- | --- |
  | **Chấm lại rẻ** | Đổi giám khảo (`gpt-5.4-mini` → `gpt-5.4`), đổi ngưỡng, thêm metric → chỉ chấm lại trên file cũ, **không** chạy lại bot |
  | **Chấm công bằng** | Bot có tính ngẫu nhiên → chạy lại là ra câu trả lời **khác**; muốn so 2 giám khảo thì phải chấm **cùng** 1 bộ câu trả lời |
  | **Bằng chứng để debug** | `baseline.jsonl` giữ nguyên câu trả lời + 5 chunk của từng câu → tuần sau mở lại q25 vẫn thấy đúng thứ đã chấm |
  | **Lỗi không lan** | Bước chấm lỗi giữa chừng → không mất kết quả bot đã chạy |
  | **So sánh các lần chạy** | `runs/baseline.jsonl` vs `runs/chunking-dieu.jsonl`… đặt cạnh nhau từng câu |

  Câu nhớ: **Chạy 1 lần, lưu lại, chấm bao nhiêu lần cũng được — cùng 1 bộ câu trả lời thì so sánh mới công bằng.**

## Bài 2 — Chấm bằng code

| Đo | Kết quả |
| --- | --- |
| Hit Điều nguồn (25 câu) | **21/25** theo code (`source_hit`) — nhưng **lạc quan**, xem bên dưới |
| Từ chối đúng (5 `not_found`) | **5/5** ✅ (kể cả bẫy "luật khác" q27–q29) |
| Từ chối nhầm (25 câu có đáp án) | **9/25** ❌ — q03, q05, q09, q16, q17, q20, q22, q23, q25 |

_(Code `source_hit` + `grade_by_code` Claude viết vào `run_eval.py` theo yêu cầu; chạy 2026-11-12, không gọi API, không
ghi DB.)_

**Đào sâu 9 câu từ chối nhầm** (Claude kiểm thêm: dữ kiện chính có nằm trong 5 chunk không):

| Câu | `hit` | Dữ kiện chính có trong top-5? | Thật ra là lỗi | Vì sao |
| --- | --- | --- | --- | --- |
| q03 (Đ20, "36 tháng") | True | ❌ | **Retrieve** (chunking) | Tiêu đề "Điều 20." nằm **cuối** chunk (vị trí 696/954), thân điều ở chunk sau — không được lấy |
| q09 (Đ107, "200 giờ") | True | ❌ | **Retrieve** (chunking) | Như trên (769/1023) |
| q17 (Đ115, "03 ngày") | True | ❌ | **Retrieve** (chunking) | Như trên (944/1016) |
| q22 (Đ107 + Đ98) | True | ❌ | **Retrieve** (chunking) | Cùng chunk cụt của Điều 107 |
| q05 (Đ35, "45 ngày") | True | ✅ | **Generate** | Đủ dữ kiện mà LLM vẫn từ chối → luật 3 quá chặt? |
| q16 (Đ190, "09 tháng") | True | ✅ | **Generate** | Như trên |
| q20 (không dấu) | False | — | **Retrieve** (câu hỏi) | Như Buổi 16 Q6 → Buổi 8 query rewrite |
| q23 (Đ35 + Đ20) | [False, True] | — | **Retrieve** (multi) | Thiếu Điều 35 |
| q25 (Đ125 + 34 + 46) | [True, False, False] | — | **Retrieve** (multi) | Thiếu 2/3 Điều |

→ **7/9 lỗi retrieve** (4 do **tiêu đề nằm cuối chunk, thân ở chunk sau** = fixed-size chunking → Buổi 7; 1 do không
dấu → Buổi 8; 2 câu multi), **2/9 lỗi generate** (q05, q16 → Buổi 11 / sửa prompt).

⚠️ **`source_hit` lạc quan:** khớp "Điều N." ở **cuối** chunk vẫn tính là hit dù thân điều không có → con số 21/25 cao
hơn thực tế. Context recall của DeepEval (Bài 3) kiểm theo **dữ kiện** nên sẽ chính xác hơn. Cải thiện sau: chỉ tính hit
khi `heading` của chunk là Điều N (tiêu đề "mang theo" từ đầu chunk).

⚠️ **q13 sai mà không từ chối:** bot trả "đủ **13** tuổi … (Điều 145)" — đáp án đúng "đủ **15** tuổi" (Điều 3). Dữ kiện
"đủ 15 tuổi" **có** trong top-5 nhưng Điều 3 không (hit=False). LLM bám **đúng** Điều 145 (nói về người chưa đủ 15 tuổi,
ngưỡng 13 cho nghệ thuật/thể thao) → **faithfulness sẽ cao mà câu trả lời sai** — đúng cái bẫy Buổi 17 Bài 5. Xem DeepEval
chấm câu này thế nào ở Bài 3.

## Bài 3 — DeepEval

| Metric | Trung bình (25) | Đạt ≥ 0.5 |
| --- | --- | --- |
| Contextual recall | **0.94** (16 câu không từ chối: 0.97) | 25/25 |
| Contextual precision | **0.83** | 21/25 |
| Faithfulness | **0.97** (16 câu không từ chối: 0.95) | 24/25 |
| Answer relevancy | **0.77** (16 câu không từ chối: 0.95) | 20/25 |

_(Giám khảo `gpt-5.4-mini`, ngưỡng 0.5, 25 câu; user chạy 2026-11-12; tổng hợp Claude tính từ
`runs/baseline_scores.jsonl`. Theo loại: single recall 0.93 / precision 0.79 / faithfulness 0.96 / relevancy 0.78 ·
multi 1.00 / 0.97 / 1.00 / 0.75.)_

🚩 **Các con số này KHÔNG đáng tin — giám khảo sai có hệ thống** (Claude kiểm bằng tìm chuỗi trong 5 chunk của
`baseline.jsonl`):

| Lỗi giám khảo | Bằng chứng |
| --- | --- |
| **Recall "bịa" ủng hộ** | q03 recall **1.0**, lý do "node 1 … states … no more than 36 months" — chuỗi "36 tháng" **không có** trong cả 5 chunk. q17 recall 1.0 — "nghỉ 03 ngày" không có. q25 recall 1.0 — "trợ cấp thôi việc" không có. q23 recall 1.0 — thiếu "trong thời hạn 30 ngày kể từ ngày hợp đồng lao động hết hạn" |
| **Relevancy không nhất quán với câu từ chối** | 9 câu từ chối nhầm: q03, q16, q17, q20, q23 → relevancy **0.0**; q05, q09, q22, q25 → **1.0** ("directly addresses the question" cho câu "Không tìm thấy…") |
| **Faithfulness quá khắt khe** | q07 faithfulness **0.25**: câu trả lời đúng Điều 98 (150/200/300%), giám khảo bắt bẻ "150% as the general weekday wage instead of weekday overtime" dù câu hỏi đã nói làm thêm giờ |
| **Faithfulness cao cho câu sai / câu từ chối** | q13 (sai "13 tuổi") 1.0; mọi câu từ chối 1.0 |

So với chấm bằng code (Bài 2): bot **từ chối nhầm 9/25**, dữ kiện chính **thiếu** ở ≥ 7 câu — vậy mà recall trung bình
0.94 → bảng DeepEval **đẹp hơn thực tế rất nhiều**.

**Bài 3b — chấm lại cùng 25 câu trả lời bằng giám khảo `gpt-5.4`** (user chọn phương án A; Claude sửa `run_eval.py` thêm
tham số `judge` + chạy 2026-11-12 → `runs/baseline_scores_gpt-5.4.jsonl`, chi phí **$1.5531**):

| Metric | mini: TB / đạt | gpt-5.4: TB / đạt |
| --- | --- | --- |
| Contextual recall | 0.94 / 25 | **0.94 / 24** |
| Contextual precision | 0.83 / 21 | 0.78 / 21 |
| Faithfulness | 0.97 / 24 | 0.96 / 24 |
| Answer relevancy | 0.77 / 20 | **0.62 / 17** |

| Ca kiểm | mini | gpt-5.4 | Kết luận |
| --- | --- | --- | --- |
| Recall q03 / q17 / q23 (dữ kiện **thiếu** thật) | 1.0 / 1.0 / 1.0 | **1.0 / 1.0 / 1.0** | ❌ vẫn "bịa" ủng hộ — vd. q03: chunk có "Điều 20 … 2 loại" + điểm a) nhưng **bị cắt trước** điểm b) "36 tháng" → giám khảo cho đủ |
| Recall q25 (thiếu 2/3 Điều) | 1.0 | **0.5** | ✅ tốt hơn |
| Relevancy 9 câu từ chối nhầm | 4 câu = 1.0 | **8/9 = 0.0** (q20 = 1.0) | ✅ gần như nhất quán |
| Faithfulness q07 (câu đúng) | 0.25 | **1.0** | ✅ sửa được |
| q13 (sai "13 tuổi") | recall 1.0, faith 1.0 | recall 1.0, faith 1.0 | ❌ vẫn cho câu sai điểm tối đa |

→ **gpt-5.4 tốt hơn ở metric "trả lời"** (relevancy, faithfulness câu đúng) nhưng **contextual recall vẫn hỏng** với cả 2
giám khảo → lỗi nằm ở **cách DeepEval chấm recall** trên chunk luật tiếng Việt bị cắt (thấy tiêu đề + 1 phần Điều là cho
"đủ"), không chỉ ở model. **Đề xuất cho Buổi 19+:** đo phần retrieve bằng **code** — thêm trường `key_facts` vào
`eval_set.jsonl` (vd. q03: `["36 tháng", "không xác định thời hạn"]`) và đếm dữ kiện có trong top-5; giữ DeepEval
(`gpt-5.4`) cho faithfulness + relevancy, có kiểm tay (Bài 6).

- **Chi phí giám khảo thật:** **$0.4462** cho 25 câu ($0.0554 thử 3 câu + $0.3907 cho 22 câu) ≈ $0.018/câu.
- **Hệ quả:** (1) chưa đưa số DeepEval vào `eval-results.md` như số "chính thức" — ghi kèm cờ 🚩; (2) Bài 6 chấm tay sẽ
  ra tỉ lệ khớp thấp → **gần như chắc phải đổi giám khảo** (`gpt-5.4`) rồi chấm lại; (3) số **chấm bằng code** (từ chối
  đúng/nhầm, dữ kiện có trong chunk) đang là thước đo **đáng tin nhất** của baseline.

**Chấm thử 3 câu** (user chạy 2026-11-12, giám khảo `gpt-5.4-mini`, ngưỡng 0.5):

| Câu | Bot trả lời | Recall | Precision | Faithfulness | Relevancy | Nhận xét (Claude đọc `reason`) |
| --- | --- | --- | --- | --- | --- | --- |
| q01 | ✅ đúng, đủ 4 mức | 0.50 | 0.45 | 1.00 | 1.00 | Recall 0.5 vì giám khảo **bắt chữ** "Tùy công việc" trong đáp án chuẩn không có trong chunk → chấm **quá máy móc**, thực tế đủ dữ kiện |
| q05 | ❌ **từ chối nhầm** (`NOT_FOUND`) | 0.50 | 0.83 | **1.00** | **1.00** | **Giám khảo sai rõ:** relevancy 1.0 với lý do "fully addresses the question" cho một câu **từ chối**; faithfulness 1.0 vì câu từ chối không có ý nào để sai |
| q13 | ❌ **sai** ("đủ 13 tuổi") | **1.00** | 0.48 | **1.00** | 0.50 | **Bẫy Buổi 17 xác nhận:** faithfulness 1.0 cho câu sai (bám đúng Điều 145). Recall 1.0 với lý do "aligns with expected output" — đáp án chuẩn là **15** tuổi → giám khảo **đọc sai** |

- **Chi phí giám khảo thật:** **$0.0554 / 3 câu** ≈ $0.018/câu → 22 câu còn lại ≈ **$0.41**, cả 25 câu ≈ **$0.46** (ước ở
  Setup ~$1 → thực tế rẻ hơn). Faithfulness tốn nhất (~$0.01/câu).
- **Bài học sớm:** (1) câu **từ chối nhầm** làm **faithfulness + relevancy cao giả** → khi tổng hợp phải tách riêng
  (vd. tính faithfulness chỉ trên câu **không** từ chối, hoặc cho 0); (2) `gpt-5.4-mini` đã chấm sai rõ ở **2/3** câu
  (q05 relevancy, q13 recall) → Bài 6 rất quan trọng, có thể phải đổi `gpt-5.4`.

## Bài 4 — `eval-results.md`

Tạo `projects/p2-labor-law-rag/eval/eval-results.md` (**Claude soạn theo yêu cầu**, 2026-11-12, số liệu từ `runs/`):
cấu hình đầy đủ (bot, dữ liệu, chunking, k, giám khảo, ngưỡng, commit) · chấm bằng code (đáng tin nhất) · DeepEval 2
giám khảo kèm cột "tin được?" · chi phí + thời gian · kết luận · **bảng trước/sau** (dòng baseline, điền dần Buổi 19–23).
Quy ước: mỗi lần chạy = 1 mục mới ở trên, **không sửa số cũ**.

## Bài 5 — 5 case tệ nhất

_(Claude phân tích theo yêu cầu, 2026-11-13, đọc chunk + câu trả lời trong `runs/baseline.jsonl`. "Tệ nhất" chọn theo
**hậu quả thật** cho user, không theo điểm DeepEval — vì giám khảo không đáng tin.)_

| id | Bot làm gì | Lỗi | Vì sao (bằng chứng) | Buổi sửa |
| --- | --- | --- | --- | --- |
| **q13** | Trả lời **sai, tự tin**: "đủ **13** tuổi (Điều 145)" — đúng là đủ **15** tuổi (Điều 3) | Retrieve + Generate | Top-5: Điều 219, 168, 219, 147, 145 — **không có Điều 3** (định nghĩa nằm trong "Giải thích từ ngữ"). LLM lấy ngưỡng 13 tuổi của Điều 145 (ngoại lệ nghệ thuật/thể thao) làm "độ tuổi tối thiểu". Cả 2 giám khảo cho faithfulness 1.0 | **9** (hybrid: cụm "Độ tuổi lao động tối thiểu" có y nguyên trong Điều 3) + **11** (câu trả lời phải khớp câu hỏi) |
| **q05** | Từ chối | Retrieve | Thân **Điều 35** (người lao động báo trước) **không** có trong top-5. Chuỗi "Ít nhất 45 ngày" có trong chunk nhưng là **Điều 36** (người sử dụng lao động báo trước — trùng số 45/30/03!) → LLM từ chối là **đúng**; Bài 2 xếp nhầm q05 vào "generate" | **7** (chunk theo Điều) |
| **q03** | Từ chối | Retrieve (chunking) | Chunk có tiêu đề "Điều 20." + điểm a), **bị cắt trước** điểm b) "36 tháng"; phần sau ở chunk không được lấy | **7** |
| **q20** | Từ chối | Retrieve (câu hỏi) | "thu viec toi da bao lau?" không dấu → Điều 25 không lọt top-5 (như Buổi 16 Q6) | **8** (query rewrite) |
| **q25** | Từ chối | Retrieve (nhiều đoạn) | Có Điều 125 (05 ngày cộng dồn) nhưng **thiếu Điều 34 + 46** (trợ cấp thôi việc) — 1 vector cho câu hỏi 2 ý chỉ kéo về 1 ý | **8** (multi-query) / **10** (rerank) |

**Đáng ghi thêm — q16:** chunk có Điều 190 khoản 1–2 (06 tháng, 09 tháng) nhưng **bị cắt trước** khoản 3 (Tòa án 01
năm) → LLM **từ chối cả câu** thay vì trả lời phần có. Lỗi lai: retrieve (cắt) + chính sách prompt "không đủ thì từ
chối" quá **tất-cả-hoặc-không** → Buổi 7 + 11 (cho phép trả lời phần có, nói rõ phần thiếu).

**Sửa lại phân loại Bài 2:** q05 là **retrieve**, không phải generate (dữ kiện trùng số nhưng của Điều 36). → 9 câu từ
chối nhầm: **8 có gốc ở retrieve** (q16 lai), **0 câu generate thuần**. Kết luận càng rõ: ưu tiên Buổi 7 (chunking).

## Bài 6 — Chấm tay 20 câu

⚠️ **Người chấm: Claude** (user nhờ, 2026-11-13) — không phải chấm tay của người như Notion yêu cầu. Cách chấm có bằng
chứng: mọi con số trong 16 câu trả lời được đối chiếu bằng code với đoạn được trích (0 con số nào thiếu), rồi đọc phần chữ
còn lại. Phiếu: `projects/p2-labor-law-rag/eval/runs/baseline_handgrade.md`. **User nên tự xem lại q03, q07, q13.**

- **Bám nguồn:** 19/20 `có`, 1/20 `không` (**q13** — suy diễn "độ tuổi tối thiểu thông thường là 13" từ Điều 145, ca
  ranh giới). 4 câu từ chối tính `có` (không có ý nào).
- **Đúng câu hỏi:** đúng 11 · thiếu 4 (q01, q18, q21 nhỏ, q24) · sai 1 (q13) · từ chối nhầm 4 (q03, q05, q16, q25).
- **Tỉ lệ khớp với faithfulness (≥ 0.5 = "có"):**

  | Giám khảo | Khớp | Câu lệch |
  | --- | --- | --- |
  | `gpt-5.4-mini` | **18/20** | q07 (0.25 cho câu đúng), q13 (1.0 cho câu suy diễn sai) |
  | `gpt-5.4` | **18/20** | q13 (1.0), q03 (0.0 cho câu **từ chối** — trái quy ước "từ chối = bám nguồn") |

- **Đọc kết quả:** faithfulness của **cả 2** giám khảo khớp 18/20 — đủ dùng cho metric này **trên câu có trả lời**. Nhưng
  (1) faithfulness **không bắt được câu sai** (q13): câu sai vẫn "bám nguồn" → cần thêm metric **đúng câu hỏi** (so
  `reference`); (2) recall vẫn hỏng (Bài 3b) → đo bằng code. **Chốt giám khảo cho Buổi 19+:** `gpt-5.4-mini` cho
  faithfulness/relevancy (khớp ngang `gpt-5.4`, rẻ hơn ~3.5×) — _relevancy của mini không nhất quán với câu từ chối →
  tính relevancy chỉ trên câu **không** từ chối_; retrieve đo bằng code (`key_facts`).

## Câu phỏng vấn cuối buổi

### 1. Baseline + vì sao cần

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

> Baseline là số đo của **bản đơn giản nhất** (naive RAG: chunk cố định 500 token, k=5, 1 lần tìm) trên bộ eval **30 câu**
> có đáp án lấy từ văn bản luật. Mình đo 2 lớp: **bằng code** — từ chối đúng **5/5** câu không có đáp án, nhưng **từ
> chối nhầm 9/25 (36%)** câu có đáp án; và **bằng DeepEval** — nhưng giám khảo LLM cho recall 0.94 trong khi dữ kiện
> thiếu ở nhiều câu, nên mình không lấy số đó, chuyển phần đo retrieve sang kiểm bằng code. Đọc từng lỗi thì **8/9** có
> gốc ở **retrieve**, chủ yếu do chunk cố định cắt rời tiêu đề và thân Điều → ưu tiên sửa chunking trước.
>
> Cần baseline vì nó là **ảnh "trước"**: không có thì không chứng minh được cải tiến nào có ích (vd. "chunk theo Điều làm
> từ chối nhầm giảm từ 9 xuống 3"), không biết nên sửa chỗ nào trước, và không phát hiện được thay đổi làm thứ khác tệ đi
> (vd. bot thôi từ chối câu giá vàng).

Câu nhớ: **Baseline: từ chối đúng 5/5, từ chối nhầm 9/25, 8/9 lỗi do retrieve (chunking) — là ảnh "trước" để chứng
minh mọi cải tiến bằng số.**

### 2. 1 case tệ

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13 — case q13.)_

> Câu hỏi: "Độ tuổi lao động tối thiểu là bao nhiêu?" Đáp án đúng: **đủ 15 tuổi** (Điều 3). Bot trả lời **tự tin**: "đủ
> **13** tuổi (Điều 145)". Tệ nhất là **cả 2 giám khảo LLM cho faithfulness 1.0**, vì câu trả lời đúng là "bám" Điều 145
> — nên nhìn điểm thì không thấy lỗi.
>
> **Phát hiện bằng cách:** chấm bằng code thấy Điều nguồn (Điều 3) **không** có trong top-5; rồi đối chiếu câu trả lời với
> **đáp án chuẩn** khi chấm tay. **Gốc lỗi:** retrieve — định nghĩa nằm trong Điều "Giải thích từ ngữ", câu hỏi lại gần
> nghĩa với các Điều về lao động chưa thành niên (top-5: Điều 219, 168, 147, 145) → LLM lấy ngưỡng 13 tuổi của trường
> hợp **ngoại lệ** làm quy tắc chung. Sửa: hybrid search (cụm "Độ tuổi lao động tối thiểu" có y nguyên trong Điều 3), thêm
> metric **đúng câu hỏi** so với đáp án chuẩn, và siết prompt "đoạn không trả lời trực tiếp thì nói không tìm thấy".
>
> Bài học: **faithfulness cao ≠ đúng** — câu sai nguy hiểm hơn câu từ chối, vì user tin nó.

Câu nhớ: **q13: hỏi tuổi tối thiểu → bot nói 13 (đúng là 15), giám khảo cho 1.0 vì "bám nguồn" Điều sai; phát hiện nhờ
Điều nguồn + đáp án chuẩn; gốc ở retrieve.**

### 3. Điểm LLM-as-judge đáng tin không

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

> Không mặc định tin — phải **kiểm từng metric** bằng thứ không phải LLM. Mình làm 3 bước: (1) **so với bằng chứng
> cứng**: tìm chuỗi trong 5 chunk → giám khảo cho recall **1.0** ở q03 dù "36 tháng" **không có** trong chunk nào; (2)
> **đổi giám khảo mạnh hơn** (`gpt-5.4`) trên **cùng** bộ câu trả lời → relevancy và faithfulness tốt hơn, nhưng recall
> **vẫn bịa** → lỗi ở cách chấm, không chỉ model → chuyển đo retrieve sang **code** (`key_facts`); (3) **chấm mẫu 20
> câu** so với faithfulness → khớp **18/20** → metric này dùng được, chọn giám khảo rẻ (`gpt-5.4-mini`). Thêm: đọc
> `reason` ở câu điểm lạ, cố định giám khảo + ngưỡng giữa các lần chạy, và nhớ **faithfulness cao không có nghĩa là đúng**
> (q13).

Câu nhớ: **Kiểm giám khảo bằng 3 thứ không phải LLM: bằng chứng cứng (code), giám khảo khác trên cùng câu trả lời, và
chấm mẫu → tin theo từng metric, không tin cả bảng.**
