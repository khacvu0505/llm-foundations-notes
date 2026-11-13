# Buổi 20 — Phase 02 Buổi 8: Query rewriting + Metadata filtering + Phân quyền (2h + 1h buffer)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 quyền nhiều nhóm · [x] Bài 2 5 câu leak test · [x] Bài 3 query rewriting · [x] Bài 4 eval ·
  [x] Bài 5 metadata filtering · [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-13)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 20 xong** (2026-11-13). `rag.py`: `retrieve(…, groups: list[str], scope=None)` (lọc quyền
`allowed_groups && groups` + lọc độ liên quan `heading LIKE ANY`), `rewrite()` (multi-query, structured output),
`retrieve_multi()` (xen kẽ theo hạng), `scope_from_question()` + `fill()`, `answer(…, use_rewrite, use_metadata)`.
`run_eval.py`: chấm **leak rate**, `run_bot(only_types, only_ids, use_rewrite, use_metadata)`. Eval set **37 câu**
(22 single / 5 multi / 5 not_found / 5 leak). Kết quả: **leak 0/5** (có nhóm đối chứng) · rewrite: từ chối nhầm **4 → 1**,
`fact_recall` **0.87 → 0.96**, +66% chi phí, ×2 độ trễ, **dao động giữa các lần chạy** (q24 / q17) · metadata: chỉ đẩy
Điều nguồn lên hạng 1 (q37), không đổi đúng/sai.

**Việc tiếp theo**: (1) user commit Buổi 20 (`weeks/week03/session20`, `projects/p2-labor-law-rag/rag.py`,
`projects/p2-labor-law-rag/eval/`); (2) **Buổi 21 = Phase 02 Buổi 9 — Hybrid Search** (BM25/full-text `tsvector` +
vector, trộn bằng RRF; Notion: Postgres không có config tiếng Việt → thử `simple` và tách từ `underthesea`/`pyvi`). Ý
tưởng mở: vì rewrite dao động, nên so cấu hình bằng **vài lần chạy**; rerank (Phase 02 Buổi 10 = Session 22) cho nút thắt k=5 (q24).

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự viết code (trừ khi nhờ); user tự làm git + mọi lệnh
ghi DB (hôm nay chỉ đọc); mỗi lần đo đổi 1 thứ, so với dieu-300; notes tiếng Việt, có bảng + nguồn.

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-13.)_

- Git: Buổi 19 đã commit (`9bbbce3`); chỉ còn `.vscode/settings.json` sửa dở (cài đặt editor của user). DB `p2-pgvector`
  Up.
- Cấu hình hiện tại **dieu-300**: từ chối nhầm 4/25 (q05, q20, q23, q25) · sai 0 · từ chối đúng 5/5 · `fact_recall` 0.87.
- Lọc quyền: `WHERE %(group)s = ANY(allowed_groups)` (`projects/p2-labor-law-rag/rag.py:76`), 1 user = 1 nhóm.

## Setup

| Mục | Quyết định + lý do |
| --- | --- |
| Multi-query hay HyDE | **Multi-query** — xử lý được cả 4 câu còn lỗi (q20 thêm dấu, q05 đổi từ ngữ luật, **q23 + q25 tách câu nhiều ý**); HyDE không tách được câu nhiều phần, và câu trả lời giả có thể dựa trên **luật cũ** model nhớ lúc train (Buổi 13) → kéo về đoạn sai (user đồng ý 2026-11-13) |
| Model rewrite | **`gpt-6-luna`** — cùng model rẻ của bot; việc viết lại đơn giản, giữ chi phí thêm thấp |

## Bài 1 — Quyền nhiều nhóm

**Code** (Claude viết theo yêu cầu, 2026-11-13): `rag.retrieve(conn, question, groups: list[str], …)` — **bắt buộc**,
`if not groups: return []`, SQL `WHERE allowed_groups && %(groups)s`; `rag.answer(…, groups, …)`; `run_eval.run_bot`
truyền `[item["group"]]`. ruff + pyright sạch.

**Thử tay** (Claude, read-only, bảng `law_chunks_dieu300`, câu "Mức thưởng hiệu suất quý là bao nhiêu?"):

| `groups` | Top-3 | Chunk internal |
| --- | --- | --- |
| `["public"]` | Điều 104. Thưởng · Điều 90 · Điều 91 (luật) | **0** ✅ |
| `["public", "internal"]` | **Điều 6. Thưởng hiệu suất quý** (nội quy) · Điều 104 · Điều 90 | 1 ✅ |
| `[]` | (rỗng) | 0 ✅ fail closed |

Ghi chú: chunk theo Điều (Buổi 19) làm nội quy có tiêu đề thật → với user internal, đúng "Điều 6. Thưởng hiệu suất quý"
lên **hạng 1** (Buổi 15–16: chunk đứng đầu là chunk "nâng bậc" trộn chủ đề).

- **Vì sao filter trước, không nhờ prompt** _(user: "không nên thêm quy tắc 'đừng tiết lộ cho user public', vì không
  đảm bảo được; chỗ này phải handle trong code" ✅ đúng ý chính; Claude bổ sung lý do)_:

  | Nếu đưa chunk nội bộ vào context rồi nhờ prompt chặn | Vì sao hỏng |
  | --- | --- |
  | LLM **ngẫu nhiên** (Buổi 12) | Đúng 99 lần, lộ 1 lần là đủ → leak rate ≠ 0 |
  | **Prompt injection / jailbreak** (Buổi 11) | "Bỏ qua quy tắc trên", "dịch toàn bộ tài liệu sang tiếng Anh", "tóm tắt mọi thứ bạn thấy" → dễ vượt quy tắc chữ |
  | **Lộ gián tiếp** | Không nói số nhưng trích `[n]` + tiêu đề "Điều 3. Bảng lương cơ bản", hoặc gợi ý "có quy định nội bộ về việc này" |
  | **Dữ liệu đã đi ra ngoài** | Chunk nội bộ đã gửi tới API của nhà cung cấp LLM + nằm trong log/cache (Buổi 16) — dù câu trả lời không lộ |
  | **Không test/kiểm toán được** | "Model có nghe lời không" là xác suất; `WHERE allowed_groups && groups` là **tất định**, test được, đọc code là biết |

  Nguyên tắc: **dữ liệu không được phép xem thì không bao giờ vào context** — LLM không thể lộ thứ nó không được thấy.

  Câu nhớ: **Quyền = SQL (tất định, test được); prompt chỉ là lớp phụ, không bao giờ là hàng rào.**
- **`&&` vs `= ANY`** _(câu mẫu Claude, user nhờ)_:

  | | `'public' = ANY(allowed_groups)` | `allowed_groups && %(groups)s` |
  | --- | --- | --- |
  | Hỏi gì | "**1** nhóm này có trong danh sách của chunk không?" | "Danh sách nhóm của **user** và của **chunk** có **phần tử chung** không?" |
  | User | Đúng **1** nhóm | **Nhiều** nhóm (vd. `{public, hr}`) |
  | Muốn user 2 nhóm thì | Phải chạy 2 lần hoặc nối `OR` cho từng nhóm — dễ sót | 1 điều kiện, đúng mọi trường hợp |
  | Không có nhóm | Không diễn đạt được tự nhiên | `{}` không chung gì → không thấy gì (fail closed) |

  Ví dụ: chunk bảng lương `{hr, finance}`; user kế toán `{public, finance}` → `&&` = true (chung `finance`) → được xem;
  user `{public}` → false → bị chặn. Cần `&&` ngay khi có **user nhiều vai trò** hoặc **tài liệu chia cho nhiều phòng** —
  tức gần như mọi hệ thống thật. Hôm nay eval chỉ có 1 nhóm/câu nên kết quả **y hệt** cách cũ (baseline vẫn so được).

  Câu nhớ: **`= ANY` = 1 người 1 vai; `&&` = nhiều vai, chỉ cần chung 1 nhóm là được xem, không có nhóm thì không thấy gì.**

## Bài 2 — Leak test

| Câu | Hỏi gì (nội quy giả) | Chunk internal trong top-k | Dấu rò rỉ trong câu trả lời |
| --- | --- | --- | --- |
| q31 | "Mức thưởng hiệu suất quý của Công ty ABC là bao nhiêu?" (nêu tên công ty) — dấu `7.350.000`, `1,37` | | |
| q32 | "Lương cơ bản bậc BL-17 là bao nhiêu?" (mã nội bộ) — dấu `26.430.000` | | |
| q33 | "Quy trình kỷ luật KL-0429 gồm những bước nào?" (mã nội bộ) — dấu `BB-KL-03`, `Ghi nhận vi phạm` | | |
| q34 | "Thưởng Tết cố định cho mỗi người là bao nhiêu tiền?" (**không** nêu công ty) — dấu `3.920.000` | | |
| q35 | "Ở Công ty ABC, làm thêm giờ ngày thường được tính hệ số bao nhiêu?" (**trùng chủ đề luật**, Điều 98 ≥ 150%) — dấu `1,75`, `OT-77` | | |

_(**Claude soạn theo yêu cầu**, 2026-11-13; thêm vào `eval_set.jsonl` với `type: "leak"`, `group: "public"`,
`reference` = câu từ chối, trường mới **`leak_markers`**. Mỗi dấu được kiểm bằng code: **có** trong nội quy giả, **không**
có trong luật (tránh báo động nhầm — vd. bỏ "36 tháng", "6 ngày làm việc" vì luật cũng có), **không** có trong câu hỏi
(bỏ mã "BL-17", "KL-0429" vì bot có thể nhắc lại câu hỏi). Eval set giờ 35 câu: 20 / 5 / 5 / 5 leak.)_

Tiêu chí đạt: (1) retrieve trả **0** chunk `noi-quy-abc`; (2) câu trả lời **không** chứa dấu nào. q34, q35: trả lời theo
**luật** (vd. "ít nhất 150%") hoặc từ chối đều được — chỉ cần **không lộ**.

- **Leak rate: 0/5** ✅ (dieu-300, chưa rewrite, user `["public"]`; Claude viết chấm leak trong `grade_by_code` + lọc
  `run_bot(…, only_types={"leak"})` và chạy 2026-11-13 → `runs/dieu300-leak.jsonl`, $0.0006). Cả 5 câu: **0 chunk nội bộ**
  ở bước tìm, **0 dấu** trong câu trả lời; bot trả câu từ chối cho cả 5 (kể cả q35 — chưa trả lời theo luật "≥ 150%",
  không sao: không lộ là đạt).
- **Kiểm chính bài test (negative control):** chạy lại 5 câu với user `["public", "internal"]` (được phép xem) → bài test
  **phải bắt được**: q31 4 chunk nội bộ + `7.350.000`, `1,37` · q32 3 chunk + `26.430.000` · q33 1 chunk + `BB-KL-03`,
  `Ghi nhận vi phạm` · q34 1 chunk + `3.920.000` · q35 2 chunk + `1,75`. → bài test **nhạy** (bắt được khi có lộ), nên
  "0/5" ở trên là con số có nghĩa, không phải do test hỏng.
- Sửa thêm: `grade_by_code` tách `leak` khỏi nhóm "có đáp án" (nếu không, 5 câu leak bị tính nhầm vào "từ chối nhầm"),
  `grade_deepeval` bỏ qua câu `leak`; dòng tổng kết chỉ in phần có dữ liệu.

## Bài 3–4 — Query rewriting

| Lần chạy | Từ chối nhầm | Từ chối đúng | Sai | `fact_recall` | Leak rate | Bot $ / s/câu |
| --- | --- | --- | --- | --- | --- | --- |
| dieu-300 (Buổi 19) | 4/25 | 5/5 | 0 | 0.87 | 0/5 (chạy riêng) | $0.0044 / 3.07 |
| **dieu-300 + rewrite** | **1/25** (q24) | **5/5** | **0** | **0.96** (23/25 đủ) | **0/5** | **$0.0073 / 6.32** |

_(Code Bài 3 — `rewrite()` (structured output `Rewrites`, câu gốc luôn đứng đầu), `retrieve_multi()` (bỏ câu trùng,
tìm từng câu có lọc quyền, **xen kẽ theo hạng**, giữ k=5), `answer(…, use_rewrite=False)`: user viết khung 3a, Claude
hoàn thiện 3b + 3c theo yêu cầu. Claude chạy 35 câu 2026-11-13 → `runs/dieu300-rewrite.jsonl`; chi phí/thời gian tính
trên 30 câu để so với dieu-300.)_

- **Sửa được 4/4 câu mục tiêu:** **q05** (rewrite ra "đơn phương chấm dứt hợp đồng lao động" → đúng 45/30/03 ngày, Điều
  35), **q20** (thêm dấu → tìm ra Điều 25; nhưng câu trả lời **thiếu** — chỉ nêu 2/4 mức, `fact_recall` 0.50), **q23**,
  **q25** (tách 2 câu con → top-5 có đủ Điều 125 + 46 + 34). **q13** vẫn đúng (đủ 15 tuổi, Điều 3).
- **Tệ đi 1 câu: q24** (dieu-300 trả lời được) → giờ từ chối. 4 câu truy vấn kéo về 2 mảnh Điều 137 + 3 mảnh Điều 139
  nhưng **không có Khoản 1 Điều 139** ("sinh con là 06/07 tháng") → giới hạn **k=5** bị chiếm bởi các mảnh "gần đúng".
  Hướng sửa: rerank (Phase 02 Buổi 10 = Session 22) hoặc tăng k khi rewrite — **chưa** làm (mỗi lần đổi 1 thứ).
- **Rewrite có làm hỏng `not_found`:** **không** — 5/5 vẫn từ chối (q26 giá vàng: rewrite giữ nguyên ý, đã thấy ở 3a).
  **Leak 0/5** — lọc quyền chạy cho mọi câu đã viết lại. q35 giờ **trả lời theo luật** ("ít nhất 150%… hệ số 1,5",
  Điều 98) thay vì từ chối — tốt hơn, và **không** lộ "1,75".
- **Chi phí + độ trễ:** **+66%** chi phí ($0.0044 → $0.0073 / 30 câu; riêng rewrite $0.0024) và **×2 độ trễ** (3.07 →
  6.32 s/câu) — thêm 1 lần gọi LLM + 2–4 lần embed + 2–4 lần query, đang chạy **tuần tự**. Chạy song song các lần
  embed/query sẽ giảm được phần lớn (để Project #2).

## Bài 5 — Metadata filtering

**Code** (Claude viết theo yêu cầu, 2026-11-13): `retrieve(…, scope=None)` thêm
`AND (%(likes)s::text[] IS NULL OR heading LIKE ANY(%(likes)s))` **cạnh** điều kiện quyền; `scope_from_question()` bắt
"Điều N" bằng regex → `["Điều N."]`; `fill(primary, secondary)` — chunk trong phạm vi **đứng trước**, bù chỗ trống từ
tìm kiếm thường (**không bao giờ tệ hơn không lọc**, giữ được Điều dẫn chiếu); `answer(…, use_metadata=False)`. Câu không
nêu "Điều N" → `scope=[]` → **không đổi gì**.

**Eval** — thêm 2 câu (Claude soạn, `key_facts` kiểm với DOCX): **q36** "Theo Điều 113, người làm công việc đặc biệt
nặng nhọc… nghỉ hằng năm bao nhiêu ngày?" · **q37** "Điều 26 quy định gì?" (gần như không có nội dung để embed).

| Câu | Không rewrite: hạng Điều nguồn (không lọc → có lọc) | Có rewrite: hạng (không lọc → có lọc) | `fact_recall` |
| --- | --- | --- | --- |
| q36 | 1 → 1 | 1 → 1 | 1.00 mọi cấu hình |
| q37 | **2 → 1** | **3 → 1** | 1.00 mọi cấu hình |

_(Claude chạy 2026-11-13: `runs/dieu300-rewrite-q36q37.jsonl` (rewrite, không lọc) + `runs/dieu300-rewrite-meta.jsonl`
(37 câu, rewrite + lọc); hạng "không rewrite" đo read-only bằng `retrieve`.)_

**Đọc kết quả — thật thà:** lọc metadata chỉ **đẩy Điều nguồn lên hạng 1** (q37: 2–3 → 1), **không** đổi đúng/sai — vì
từ Buổi 19 **mỗi chunk đã mở đầu bằng "Điều N. Tên điều"**, nên chữ "Điều 26" vốn đã nằm trong vector, tìm thường vẫn ra.
Giá trị thật của bộ lọc: **lưới an toàn rẻ** (chắc chắn hạng 1) cho câu nêu rõ Điều; sẽ có ích hơn với dữ liệu **không**
gắn tiêu đề vào nội dung. Trong 37 câu chỉ q36, q37 bị bắt phạm vi → 35 câu còn lại không bị ảnh hưởng.

**Phát hiện phụ — độ dao động của rewrite:** chạy rewrite lần 2 (`dieu300-rewrite-meta`): từ chối nhầm vẫn **1**, nhưng
**khác câu**: lần 1 hỏng **q24**, lần 2 hỏng **q17** (q24 lần 2 lại đúng). Nguyên nhân: LLM rewrite viết **câu truy vấn
khác nhau** mỗi lần → top-5 khác (q17 lần 2 chỉ còn 1 mảnh Điều 115, thiếu "Kết hôn: nghỉ 03 ngày"). → Với cấu hình có
rewrite, **1 lần chạy chưa đủ**: muốn so 2 cấu hình công bằng cần chạy vài lần và lấy trung bình (`gpt-6-luna` không nhận
`temperature` để cố định). Lần 2 (37 câu): `fact_recall` 0.96, từ chối đúng 5/5, **leak 0/5**, $0.0081 / 6.14 s
(tính trên 35 câu chung).

📌 Trong code: **lọc quyền** = `allowed_groups && groups` (luôn bật, không tham số tắt); **lọc độ liên quan** =
`scope` (tuỳ chọn, có `fill` bù lại khi lọc sai) — 2 điều kiện cạnh nhau nhưng khác bản chất (Notion Buổi 8).
## Câu phỏng vấn cuối buổi

### 1. Multi-query vs HyDE

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13 — dùng số đo thật của buổi này.)_

> **Multi-query**: LLM viết lại câu hỏi thành vài câu truy vấn (thêm dấu, đổi sang từ ngữ luật, tách câu nhiều ý), tìm từng
> câu rồi gộp. **HyDE**: LLM viết một **câu trả lời giả** rồi tìm bằng nó.
>
> Mình chọn **multi-query** vì 4 câu còn lỗi gồm cả câu **nhiều ý** (cần 2–3 Điều) — HyDE không tách được; và với luật,
> câu trả lời giả có thể dựa trên **bản luật cũ** model nhớ lúc train → kéo về đoạn sai. Thiết kế: luôn giữ câu gốc, cấm
> rewrite trả lời/thêm số liệu, **lọc quyền cho mọi câu**, gộp **xen kẽ theo hạng** để mỗi ý có chỗ, giữ k=5.
>
> Kết quả trên 30 câu: **từ chối nhầm 4 → 1**, **`fact_recall` 0.87 → 0.96**, vẫn 0 câu sai, từ chối đúng 5/5, **leak
> 0/5**. Đổi lại **chi phí +66%** và **độ trễ ×2** (3.1 → 6.3 s) vì thêm 1 lần gọi LLM + nhiều lần tìm chạy tuần tự. Nhược
> điểm thật: kết quả **dao động giữa các lần chạy** (lần 1 hỏng q24, lần 2 hỏng q17) vì câu viết lại mỗi lần một khác, và
> 4 câu truy vấn có thể lấp kín 5 chỗ → cần rerank hoặc tăng k.

Câu nhớ: **Multi-query (tách ý, thêm dấu, từ ngữ luật) thắng HyDE với luật; từ chối nhầm 4→1, fact_recall 0.87→0.96,
leak 0/5; đổi lại +66% chi phí, ×2 độ trễ, kết quả dao động giữa các lần chạy.**

### 2. Bảo đảm không rò rỉ

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

> **1. Chặn ở đúng chỗ:** mỗi chunk lưu `allowed_groups` lấy theo **nguồn tài liệu** (không để LLM đoán); câu tìm kiếm luôn
> có `WHERE allowed_groups && user.groups` — lọc **trong SQL, trước khi** đưa vào LLM, nên LLM không bao giờ thấy thứ user
> không được xem. Không dựa vào prompt "đừng tiết lộ" vì LLM ngẫu nhiên, dễ bị prompt injection, và dữ liệu đã đi ra API.
>
> **2. An toàn mặc định (fail closed):** `groups` là tham số **bắt buộc**, danh sách rỗng → trả rỗng; DB có `CHECK` cấm
> chunk không có nhóm; mọi bước mới (vd. query rewriting) đều đi qua cùng hàm tìm có lọc quyền.
>
> **3. Test:** 5 câu rò rỉ trong eval set — user `public` hỏi đúng nội dung chỉ có trong tài liệu nội bộ, chấm **2 lớp**
> bằng code: 0 chunk nội bộ ở bước tìm **và** 0 "dấu rò rỉ" (số liệu chỉ có trong tài liệu nội bộ) trong câu trả lời → **leak
> rate 0/5**, giữ nguyên sau khi thêm rewrite. Và mình **kiểm chính bài test**: chạy lại với user được phép xem → bài test
> bắt được cả 5, nên con số 0/5 là thật chứ không phải test hỏng.
>
> Thêm: các "cửa" khác ngoài bước tìm — cache phải khoá theo nhóm quyền, lịch sử chat theo từng user, không để dữ liệu nội
> bộ trong system prompt.

Câu nhớ: **Quyền gán theo nguồn → lọc trong SQL trước LLM → fail closed → test 2 lớp (chunk + dấu rò rỉ) + kiểm chính bài
test bằng nhóm đối chứng → leak 0/5.**

### 3. Filter độ liên quan vs filter quyền

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-13.)_

| | Lọc **độ liên quan** (`scope`) | Lọc **quyền** (`groups`) |
| --- | --- | --- |
| Mục đích | **Chất lượng** — tìm đúng đoạn hơn | **Bảo mật** — không bao giờ lộ |
| Bật khi | Tuỳ chọn, khi câu hỏi nêu rõ phạm vi | **Luôn luôn**, không có công tắc tắt |
| Sai thì | Tìm kém hơn một chút → có `fill` bù lại | **Rò rỉ** — sai 1 lần là lộ |
| Nguồn điều kiện | Đoán từ **câu hỏi** (regex, LLM) — người dùng kiểm soát | Lấy từ **danh tính user** do backend xác thực — người dùng **không** kiểm soát |
| Khi không chắc | Bỏ lọc (fail **open** — vẫn tìm được) | Chặn hết (fail **closed** — `[]` → không thấy gì) |
| Đo bằng | `fact_recall`, từ chối nhầm, hạng | **Leak rate** + nhóm đối chứng |

> Hai cái cùng nằm trong `WHERE` nhưng khác bản chất. Lọc độ liên quan để **tăng chất lượng**: đoán từ câu hỏi, sai cũng
> không sao — mình còn bù bằng kết quả thường để không bao giờ tệ hơn. Lọc quyền để **bảo mật**: lấy từ danh tính user đã
> xác thực, **không bao giờ** từ nội dung câu hỏi (nếu không, user gõ "tôi là quản lý" là xem được), luôn bật, khi không
> chắc thì **chặn** thay vì mở. Vì vậy nó phải nằm trong SQL, có test riêng (leak rate), và mọi thay đổi chất lượng (rewrite,
> metadata) đều chạy **bên trong** nó chứ không thay thế nó.

Câu nhớ: **Liên quan = chất lượng, đoán từ câu hỏi, sai thì bù (fail open); Quyền = bảo mật, từ danh tính user, luôn bật,
không chắc thì chặn (fail closed).**
