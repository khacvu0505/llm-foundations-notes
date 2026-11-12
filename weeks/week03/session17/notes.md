# Buổi 17 — Phase 02 Buổi 5: Xây Eval Set (2h)

Đề bài: `exercises.md` cùng thư mục.

- [x] Setup · [x] Bài 1 schema · [x] Bài 2 20 câu trả lời được · [x] Bài 3 5 câu nhiều đoạn ·
  [x] Bài 4 5 câu không có · [x] Bài 5 RAGAS → DeepEval · [x] 3 câu phỏng vấn (câu mẫu — còn tập nói to)

## Handoff — dừng ở đây (cập nhật 2026-11-12)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Buổi 17 xong** (2026-11-12). Eval set **30 câu** (20 single / 5 multi / 5 not_found) ở
`projects/p2-labor-law-rag/eval/eval_set.jsonl` — **Claude soạn nháp toàn bộ theo yêu cầu** từ nguyên văn DOCX (helper
`show_dieu` trong `exercises.py`), **user cần duyệt lại** cách diễn đạt. Công cụ chấm: **DeepEval 4.3.4** (ragas 0.4.3
xung đột `openai`, xem Bài 5).

**Việc tiếp theo**: (1) user commit Buổi 17 + `projects/p2-labor-law-rag/eval/` + `pyproject.toml` / `uv.lock`
(`deepeval`); (2) user duyệt 30 câu (nhất là q09, q15, q23, q25); (3) **Buổi 18 = Phase 02 Buổi 6 — Đo Baseline (4h)**:
chạy 30 câu qua naive RAG Buổi 16 → 4 metric DeepEval cho 25 câu + tỷ lệ từ chối 5 câu `not_found` + hit `sources` bằng
code → `eval-results.md`; đọc 5 case tệ nhất (retrieve hay generate?); **chọn model giám khảo** (khác `gpt-6-luna`);
chấm tay 20 câu so với faithfulness.

**Cách làm việc**: đi từng câu một; Claude gợi ý + review, user tự soạn câu hỏi + đáp án (trừ khi nhờ); đáp án chuẩn
phải **lấy từ DOCX**; user tự làm git + `uv add`; notes tiếng Việt, có bảng + nguồn, mỗi câu phỏng vấn có "Câu nhớ".

## Trạng thái đầu buổi

_(Claude kiểm, 2026-11-12.)_

- Git: Buổi 16 đã commit (`e64777f`). ruff còn 3 lỗi E501 trong `INSTRUCTIONS` Buổi 16 (dòng dài, không ảnh hưởng chạy).
- Notion Phase 02 đã lên **version 46**: Buổi 5 ghi rõ cơ cấu **20 / 5 / 5** và 4 metric RAGAS; Buổi 6 thêm "tự chấm tay
  20 câu so với faithfulness"; Buổi 8 thêm 5 câu rò rỉ; Buổi 11 thêm 2 câu prompt injection.
- PyPI: `ragas` **0.4.3** (2026-01-13), `deepeval` 4.3.4 (2026-11-11). → Cuối buổi dùng **DeepEval** (xem Bài 5).
- RAGAS docs (Claude đọc 2026-11-12, các trang metric):
  - **Faithfulness**: "measures how factually consistent a `response` is with the `retrieved context`" — số ý trong
    câu trả lời được context ủng hộ / tổng số ý; 0–1. Cần `user_input`, `response`, `retrieved_contexts`.
  - **Answer (Response) Relevancy**: "measures how relevant a response is to the user input" — LLM sinh ~3 câu hỏi từ
    câu trả lời, so cosine với câu hỏi gốc bằng **embedding**. Cần `user_input`, `response`.
  - **Context Precision**: "evaluates the retriever's ability to rank relevant chunks higher than irrelevant ones" —
    trung bình precision@k; cần `user_input`, `reference`, `retrieved_contexts`.
  - **Context Recall**: "measures how many of the relevant documents … were successfully retrieved" — tách `reference`
    thành các ý, đếm ý nào được context ủng hộ. Cần `user_input`, `retrieved_contexts`, `reference`.

## Setup

| Mục                 | Quyết định + lý do |
| ------------------- | ------------------ |
| Chỗ lưu eval set    | `projects/p2-labor-law-rag/eval/eval_set.jsonl` — cạnh dữ liệu, Project #2 dùng lại; Buổi 18 thêm `eval-results.md` cạnh đó (user đồng ý 2026-11-12) |
| Định dạng           | **JSONL** — mỗi dòng 1 câu (1 object JSON), thêm/sửa từng câu dễ, git diff rõ từng dòng; Python đọc bằng `json.loads` từng dòng |

## Bài 1 — Schema 1 dòng eval

- **Các trường đã chọn:** `id`, `question`, `reference`, `sources`, `type`, `group`, `notes` (theo bảng gợi ý trong đề).
  Dòng mẫu q01 (đáp án theo Điều 25, đã đối chiếu DOCX ở Buổi 14):

  ```json
  {"id": "q01", "question": "Thử việc tối đa bao lâu?", "reference": "Tùy công việc: không quá 180 ngày với người quản lý doanh nghiệp; không quá 60 ngày với công việc cần trình độ từ cao đẳng trở lên; không quá 30 ngày với trình độ trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ; không quá 06 ngày làm việc với công việc khác. Chỉ được thử việc một lần cho một công việc.", "sources": ["Điều 25"], "type": "single", "group": "public", "notes": ""}
  ```

- **Vì sao cần cả `reference` và `sources`** _(câu mẫu Claude, user nhờ)_:

  | Trường | Trả lời câu hỏi | Chấm bước | Cách chấm |
  | --- | --- | --- | --- |
  | `sources` (`["Điều 25"]`) | Đoạn đúng **có được lấy ra** không? | **Retrieve** | So với `heading`/nội dung các chunk trong top-k → **không cần LLM**, rẻ, chắc chắn (hit / không hit) |
  | `reference` (đáp án) | Câu trả lời cuối **có đúng, đủ** không? | **Generate** (+ context recall) | So nội dung → thường cần **LLM-as-judge** (RAGAS) |

  Có cả 2 → **định vị lỗi** như Buổi 16: `sources` trượt → lỗi retrieve; `sources` trúng mà câu trả lời sai → lỗi
  generate. Chỉ có `reference` thì biết **sai** nhưng không biết **sai ở đâu**.
  Lưu ý khi so `sources`: 1 Điều có thể nằm vắt 2 chunk (Điều 25: tiêu đề ở chunk 23, thân ở chunk 24 — `heading` chunk
  23 là "Điều 22") → so bằng **`heading` hoặc nội dung chứa "Điều 25."**, không chỉ `heading`.

  Câu nhớ: **`sources` chấm tìm (rẻ, không cần LLM), `reference` chấm trả lời; có cả 2 mới biết sai ở bước nào.**
- **Câu `not_found` thì `reference` ghi gì** _(câu mẫu Claude, user nhờ)_: `reference` = **đúng câu `NOT_FOUND`** của
  Buổi 16 ("Không tìm thấy thông tin này trong tài liệu."); `sources` = **`[]`** (không đoạn nào được phép làm căn cứ).

  ```json
  {"id": "q26", "question": "Giá vàng hôm nay bao nhiêu?", "reference": "Không tìm thấy thông tin này trong tài liệu.", "sources": [], "type": "not_found", "group": "public", "notes": "ngoài lề hoàn toàn"}
  ```

  Chấm nhóm này **riêng bằng code**: đạt khi `answer.strip() == NOT_FOUND` → **tỷ lệ từ chối đúng** (vd. 5/5). Các
  metric RAGAS không hợp với câu từ chối: context recall so với đáp án "không tìm thấy" không có nghĩa; câu từ chối gần
  như không có "ý" để chấm faithfulness (_suy luận, chưa chạy thử — kiểm ở Buổi 18_). → Bảng baseline nên tách: **25
  câu chấm RAGAS** + **5 câu chấm từ chối**.

  Câu nhớ: **Câu không có đáp án: `reference` = câu từ chối cố định, `sources` = rỗng, chấm bằng so sánh chuỗi.**
- **Vì sao đáp án lấy từ DOCX** _(user: "cần độ chính xác, bắt buộc trích từ tài liệu **còn hiệu lực**" ✅ — đúng ý
  chính, nhất là "còn hiệu lực"; Claude bổ sung 3 loại "trí nhớ")_:

  | Lấy đáp án từ… | Rủi ro |
  | --- | --- |
  | **Trí nhớ của mình** | Nhớ sai / nhớ bản cũ; luật có nhiều mức (Điều 25: 4 mức) dễ nhớ thiếu |
  | **LLM (ChatGPT…)** | Học từ **bản luật cũ** lúc train (Buổi 13) — vd. thai sản: bản hợp nhất 2026 có "**con thứ hai 07 tháng**" (Luật Dân số 113/2025) mà bản cũ không có |
  | **Câu trả lời của chính bot** | **Vòng tròn**: bot luôn "đúng" với chính nó → điểm cao giả, eval vô dụng |
  | ✅ **DOCX 18/VBHN-VPQH** | Đúng **bản mà bot đang dùng** → đo đúng thứ cần đo |

  Hệ quả: đáp án chuẩn **gắn với phiên bản tài liệu** — luật sửa (vd. sau 21/11/2026) thì phải **cập nhật cả dữ liệu
  lẫn `reference`** cùng lúc, nếu không bot đúng mà eval chấm sai.

  Câu nhớ: **Đáp án chuẩn lấy từ đúng bản tài liệu bot dùng — không từ trí nhớ người, LLM hay chính bot.**

## Bài 2–4 — Bộ 30 câu

| Nhóm | Mục tiêu | Đã có | Ghi chú |
| --- | --- | --- | --- |
| `single` (trả lời được) | 20 | **20** ✅ | q01 Đ25 · q02 Đ139 · q03 Đ20 · q04 Đ26 · q05 Đ35 · q06 Đ97 · q07 Đ98 · q08 Đ105 · q09 Đ107 · q10 Đ113 · q11 Đ124 · q12 Đ123 · q13 Đ3 · q14 Đ146 · q15 Đ169 · q16 Đ190 · q17 Đ115 · q18 Đ91 · q19 Đ25 (tình huống) · q20 Đ25 (không dấu) |
| `multi` (nhiều đoạn) | 5 | **5** ✅ | q21 Đ25+26 · q22 Đ107+98 · q23 Đ35+20 · q24 Đ137+139 · q25 Đ125+34+46 (3 Điều, khó nhất) |
| `not_found` | 5 | **5** ✅ | q26 giá vàng (ngoài lề) · q27 thủ tục đăng ký kết hôn · q28 tỷ lệ đóng BHXH · q29 biểu thuế TNCN · q30 hạn nộp báo cáo tài chính (4 câu "luật khác") |

_(**Claude soạn nháp toàn bộ 30 câu theo yêu cầu**, 2026-11-12; mọi `reference` lấy từ nguyên văn DOCX qua `show_dieu`;
câu `not_found` kiểm bằng grep DOCX — không có "giá vàng", "đăng ký kết hôn", "tỷ lệ đóng", "mức đóng", "báo cáo tài
chính"; "thuế thu nhập cá nhân" chỉ xuất hiện 1 lần như khoản bị trích lương. File kiểm: 30 dòng JSON hợp lệ, id không
trùng, 20/5/5, `not_found` có `sources=[]`. **User cần duyệt lại** cách diễn đạt đáp án.)_

- **Rải theo Chương:** I (q13) · III hợp đồng (q01, q03, q04, q05, q19, q20) · VI tiền lương (q06, q07, q18) · VII
  thời giờ (q08, q09, q10, q17 — **tránh Điều 112**) · VIII kỷ luật (q11, q12) · X lao động nữ (q02) · XI chưa thành
  niên + hưu (q14, q15) · XIV tranh chấp (q16). Biến thể: tình huống (q19, q23), không dấu (q20).
- **Dự đoán naive RAG với câu `multi`** _(giả thuyết của Claude, Buổi 18 kiểm)_: q21 dễ (Điều 25, 26 nằm sát nhau, có thể
  cùng/kề chunk); q23, q25 khó — 2–3 Điều **cách xa nhau**, 1 câu hỏi chỉ embed thành **1 vector** → top-5 có thể chỉ
  chứa 1 trong các Điều cần → context recall thấp. Đây là lý do Buổi 8 có query rewriting (multi-query: tách câu hỏi).
- **Loại `not_found` khó nhất** _(giả thuyết)_: câu **"luật khác" gần chủ đề** (q28 BHXH, q29 thuế) — retrieve vẫn ra
  chunk có chữ "bảo hiểm xã hội", "thuế thu nhập cá nhân" → LLM thấy context "na ná" + **đã biết** đáp án từ lúc train
  (vd. tỷ lệ đóng BHXH) → dễ trả lời bằng kiến thức ngoài thay vì từ chối. q26 giá vàng thì dễ (top-1 sim chỉ 0.33 ở
  Buổi 16).

## Bài 5 — RAGAS → đổi sang **DeepEval**

**Vì sao đổi** (Claude kiểm 2026-11-12): user `uv add ragas` → uv cài **ragas 0.3.1** (không phải 0.4.3) và `import
ragas` lỗi `ModuleNotFoundError: No module named 'langchain_community.chat_models.vertexai'`. `uv pip install --dry-run
ragas==0.4.3` cho thấy bản mới kéo `instructor` → **hạ `openai` 3.19.2 → 3.3.0**, xung đột `openai>=3.19.2` của project
→ uv lặng lẽ chọn bản cũ hỏng. Notion cho phép "RAGAS (hoặc DeepEval)" → user chọn **DeepEval**: `uv remove ragas` +
`uv add deepeval` → **deepeval 4.3.4**, `openai` giữ 3.19.2 ✅.

| Metric (DeepEval) | Đo gì | Cần trường (`_required_params`) | Chấm bước | Cần đáp án chuẩn? |
| --- | --- | --- | --- | --- |
| `ContextualRecallMetric` | Context lấy được có chứa **đủ các ý** của đáp án chuẩn không | `input`, `retrieval_context`, `expected_output` | Retrieve (đủ) | ✅ |
| `ContextualPrecisionMetric` | Chunk **liên quan** có được xếp **trên** chunk không liên quan không | `input`, `retrieval_context`, `expected_output` | Retrieve (thứ hạng) | ✅ |
| `FaithfulnessMetric` | Mọi ý trong câu trả lời có được **context ủng hộ** không (không bịa) | `input`, `actual_output`, `retrieval_context` | Generate | ❌ |
| `AnswerRelevancyMetric` | Câu trả lời có **đúng trọng tâm** câu hỏi không | `input`, `actual_output` | Generate | ❌ |

_(Tên + trường đọc từ code deepeval 4.3.4 đã cài; DeepEval docs: các metric RAG đều dùng LLM-as-a-judge. Ý nghĩa 4
metric giống RAGAS — RAGAS docs đọc ở đầu buổi. DeepEval còn có `ContextualRelevancyMetric`.)_

- **Metric nào không cần đáp án chuẩn, chấm bước nào** _(câu mẫu Claude, user nhờ)_:

  | Nhóm | Metric | So cái gì với cái gì | Vì sao (không) cần đáp án |
  | --- | --- | --- | --- |
  | **Generate**, không cần đáp án | Faithfulness | câu trả lời ↔ **context** | Chỉ hỏi "có bám context không" — không cần biết đáp án đúng |
  | | Answer relevancy | câu trả lời ↔ **câu hỏi** | Chỉ hỏi "có trả lời đúng câu được hỏi không" |
  | **Retrieve**, cần đáp án | Contextual recall | **đáp án chuẩn** ↔ context | Phải biết đáp án gồm ý nào mới kiểm context có **đủ** không |
  | | Contextual precision | **đáp án chuẩn** ↔ thứ hạng chunk | Phải biết chunk nào **hữu ích** mới chấm thứ hạng |

  Bẫy: **faithfulness cao ≠ câu trả lời đúng.** Nếu retrieve đưa nhầm Điều 36, bot trả lời **bám đúng** Điều 36 →
  faithfulness ~1.0 nhưng **sai câu hỏi**. Phải xem kèm contextual recall (ở đây sẽ thấp) → không metric nào đủ một
  mình. Ích lợi: 2 metric không cần đáp án chạy được trên **câu hỏi thật của user** (giám sát khi chạy thật), 2 metric
  cần đáp án chỉ chạy trên **eval set**.

  Câu nhớ: **Không cần đáp án = chấm "trả lời" (bám context, đúng trọng tâm); cần đáp án = chấm "tìm" (đủ ý, xếp
  đúng). Faithfulness cao vẫn có thể sai.**

- **Ghép trường mình ↔ DeepEval** (`LLMTestCase`): `question` → `input` · câu trả lời bot → `actual_output` ·
  `reference` → `expected_output` · `content` 5 chunk → `retrieval_context` (list[str]). Giám khảo: tham số `model` của
  metric (mặc định `None` → model mặc định của DeepEval — **chọn rõ ở Buổi 18**, vì chi phí: 25 câu × 4 metric × vài lần
  gọi LLM).
- **Rủi ro LLM-as-judge** _(user: "giám khảo có thể không có thông tin mới nhất, và có thể tự bịa" ✅ — đúng 2 rủi ro;
  Claude bổ sung)_:

  | Rủi ro | Ví dụ | Giảm bằng |
  | --- | --- | --- |
  | **Kiến thức cũ** (user) | Giám khảo "biết" thai sản là 6 tháng cho mọi trường hợp → chấm sai câu đúng "con thứ hai 07 tháng" | Bắt giám khảo chấm **chỉ theo** `expected_output` / context, không theo trí nhớ |
  | **Tự bịa / chấm sai** (user) | Tách sai các ý trong câu trả lời, hoặc cho "được ủng hộ" khi context không có | Đọc **lý do** (`reason`) metric trả về ở các câu điểm lạ |
  | **Ngẫu nhiên** | Chạy 2 lần cùng câu → điểm khác nhau | Cố định model giám khảo; chạy vài lần, xem độ dao động |
  | **Thiên vị chính mình** | Giám khảo **cùng model** với bot (`gpt-6-luna`) dễ "hợp gu" với câu của chính nó (_rủi ro hay được nhắc, chưa kiểm_) | Dùng model giám khảo **khác** (và mạnh hơn) bot |
  | **Tiếng Việt + văn bản luật** | Diễn đạt khác chữ ("không quá 60 ngày" vs "tối đa 60 ngày") có thể bị chấm lệch | Kiểm tay vài câu tiếng Việt |
  | **Chi phí** | 25 câu × 4 metric × nhiều lần gọi | Chọn model giám khảo rõ ràng, chạy theo lô |

  → Vì vậy Notion Buổi 6: **tự chấm tay 20 câu**, so với điểm faithfulness → ghi **tỷ lệ khớp** (vd. 17/20). Khớp thấp →
  chưa tin bảng số, sửa giám khảo trước.

  Câu nhớ: **Giám khảo LLM cũng là LLM: có thể cũ, bịa, ngẫu nhiên, thiên vị → phải kiểm nó bằng chấm tay trước khi tin
  con số.**

## Câu phỏng vấn cuối buổi

### 1. Xây eval set cho RAG

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-12.)_

| Loại | Số câu | Kiểm cái gì |
| --- | --- | --- |
| **single** — trả lời được từ 1 Điều | 20 | Chất lượng cơ bản; rải đều các Chương; có biến thể **tình huống** (q19) + **không dấu** (q20) |
| **multi** — cần ≥ 2 Điều | 5 | Retrieve có lấy **đủ** nhiều đoạn xa nhau không (q25: 3 Điều) |
| **not_found** — không có trong tài liệu | 5 | Bot có **từ chối** thay vì bịa không; gồm câu "luật khác" gần chủ đề (BHXH, thuế) |
| _Thêm sau:_ rò rỉ quyền / prompt injection | 5 / 2 | Buổi 8 / Buổi 11 (Notion) |

> Mỗi câu gồm: câu hỏi, **đáp án chuẩn lấy từ đúng bản tài liệu bot dùng** (không từ trí nhớ người/LLM/chính bot),
> **Điều nguồn** (để chấm retrieve bằng code, rẻ), loại câu, nhóm quyền. Mình soạn **30 câu**: 20 trả lời được (rải đều
> các chương, có câu tình huống và câu gõ không dấu), 5 câu cần ghép nhiều Điều, 5 câu không có trong tài liệu để test
> từ chối — trong đó có câu thuộc luật khác mà model "biết" từ lúc train, đây là loại dễ bịa nhất. Câu không có đáp án
> chấm riêng bằng so sánh chuỗi với câu từ chối cố định; còn lại chấm bằng 4 metric. Đáp án chuẩn **gắn với phiên bản
> luật** — luật sửa thì cập nhật cùng lúc.

Câu nhớ: **Eval set = đề thi có đáp án lấy từ tài liệu thật, đủ 3 loại: trả lời được, cần ghép nhiều đoạn, không có
đáp án — mỗi câu ghi cả Điều nguồn để biết sai ở bước nào.**

### 2. 4 metric RAGAS (dùng bản DeepEval)

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-12 — bản ngắn của Bài 5 câu 1.)_

> Có 4 metric, chia 2 nhóm. **Chấm bước tìm** (cần đáp án chuẩn): **context recall** — context lấy được có chứa đủ các
> ý của đáp án chuẩn không; **context precision** — đoạn hữu ích có được xếp lên trên không. **Chấm bước trả lời**
> (không cần đáp án): **faithfulness** — mọi ý trong câu trả lời có được context ủng hộ không, tức có bịa không;
> **answer relevancy** — câu trả lời có đúng trọng tâm câu hỏi không. Cả 4 đều dùng LLM làm giám khảo. Phải đọc **cùng
> nhau**: faithfulness cao vẫn có thể sai nếu retrieve đưa nhầm đoạn — context recall thấp sẽ lộ ra. Hai metric không
> cần đáp án còn chạy được trên câu hỏi thật để giám sát.

Câu nhớ: **Recall + precision chấm "tìm" (cần đáp án); faithfulness + relevancy chấm "trả lời" (không cần); đọc cả 4
cùng lúc.**

### 3. Vì sao không tin tuyệt đối LLM-as-judge

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-12 — bản ngắn của Bài 5 câu 2.)_

> Giám khảo cũng là một LLM nên mang đủ lỗi của LLM: **kiến thức cũ** (có thể chấm sai câu đúng theo luật mới, vd. thai
> sản con thứ hai 07 tháng), **tự bịa / chấm sai** (tách sai ý, cho "được ủng hộ" khi context không có), **ngẫu nhiên**
> (chạy lại ra điểm khác), **thiên vị** nếu cùng model với bot, và dễ lệch với cách diễn đạt tiếng Việt. Cách xử lý:
> giám khảo là model **khác, mạnh hơn** bot; chỉ chấm theo đáp án chuẩn/context; đọc **lý do** ở các câu điểm lạ; và
> quan trọng nhất là **chấm tay một mẫu** (Notion: 20 câu) rồi so với giám khảo — tỷ lệ khớp cao (vd. 17/20) mới tin
> bảng số.

Câu nhớ: **Giám khảo LLM cũng là LLM → kiểm nó bằng chấm tay trước khi tin con số.**
