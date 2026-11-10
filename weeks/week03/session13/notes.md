# Buổi 13 — Phase 02 Buổi 1: Embeddings & Vector Space (2h)

Đề bài: `exercises.md` cùng thư mục.

- [ ] Setup · [ ] Bài 1 OpenAI embedding · [ ] Bài 2 cosine · [ ] Bài 3 Việt/Anh, OpenAI vs đa ngữ ·
  [ ] Bài 4 dữ liệu Bộ luật Lao động

## Handoff — dừng ở đây (cập nhật 2026-11-10)

_(Claude ghi để mở session mới. Đọc mục này trước.)_

**Bắt đầu Phase 02.** Domain đã chọn: **Bộ luật Lao động VN** (user quyết định 2026-11-10). Chưa làm bài nào.

**Việc tiếp theo**: Setup → Bài 1.

**Cách làm việc** (giữ từ Phase 01): đi từng câu một; Claude gợi ý + review + chạy test, user tự viết code bài tập
(trừ khi user nhờ viết); user tự làm git commit/push + thao tác dashboard; notes ghi tiếng Việt, mỗi câu có bảng +
nguồn.

## Trạng thái đầu buổi

_(Claude ghi, 2026-11-10.)_

- Phase 01: xong Phần A Buổi 12 + 6 câu Exit criteria (có câu mẫu, `weeks/week02/session12/notes.md`). Rebuild test
  Phase 01: **bỏ** (user quyết định 2026-11-10). Còn treo: hard limit chi tiêu OpenAI.
- Nội dung Phase 02 lấy từ Notion public page (2026-11-10), 18 buổi, 3 tuần. Exit criteria Phase 02: bảng evals
  trước/sau · rebuild test 2h · 4 câu phỏng vấn (RAG vs fine-tuning, hallucination còn lại, hybrid +%, rerank đổi
  latency) · Project #2 demo sống + README có số · leak rate = 0.
- SDK `openai` (gốc repo) liệt kê model embedding: `text-embedding-ada-002`, `text-embedding-3-small`,
  `text-embedding-3-large` (`.venv/.../openai/types/embedding_model.py`); `dimensions` chỉ hỗ trợ từ
  `text-embedding-3` (`embedding_create_params.py`).

## Setup — docs embeddings

| Câu hỏi                                 | Trả lời (nguồn) |
| --------------------------------------- | --------------- |
| Embedding là gì (1 câu của mình)        |                 |
| Model nào, số chiều mặc định            |                 |
| `dimensions` dùng để làm gì, đánh đổi gì |                 |
| Giá / 1M token                          |                 |

## Bài 1 — OpenAI embedding

_(Câu mẫu Claude viết theo yêu cầu, 2026-11-10, từ output thật của `run_bai1` — 3 câu: nghỉ phép (Việt) / bản dịch
(Anh) / thời tiết Hà Nội. Code Bài 1: user viết, Claude sửa phần in `dims` / `usage` / 3 câu theo yêu cầu.)_

| Câu hỏi                          | Trả lời |
| -------------------------------- | ------- |
| Số chiều; câu dài/ngắn có khác   | Luôn **1536** với `text-embedding-3-small`, câu dài ngắn như nhau (cả 3 câu = 1536). Cột vector trong DB có kích thước cố định (vd. `vector(1536)` của pgvector) → mọi chunk và mọi câu hỏi phải dùng **cùng model**, cùng số chiều; đổi model = embed lại toàn bộ |
| 5 số đầu — đọc được nghĩa không  | Không. Từng số riêng lẻ không mang nghĩa ("nghỉ phép", "thời tiết"); nghĩa chỉ hiện ra khi **so cả vector** với nhau (Bài 2) |
| Độ dài vector; đã chuẩn hoá chưa | Docs: "OpenAI embeddings are normalized to length 1" (guide Embeddings, FAQ). **Chưa tự kiểm** → Bài 2 tính √(tổng bình phương) |
| `usage`: token, có output không  | `prompt_tokens=48, total_tokens=48` cho cả 3 câu, **không có output token**: model không sinh chữ, chỉ trả số → chỉ trả tiền input token |
| Gửi list vs gửi từng câu         | Gửi list = **1 request** cho cả 3 (ít round trip, nhanh hơn). Kết quả có `index` → ghép vector với câu gốc theo `index` |

Embedding không phải hỏi–đáp: API biến **bất kỳ văn bản nào** thành vector. Trong RAG cả 2 phía đều được embed: các
chunk luật (1 lần, Buổi 3, lưu pgvector) và câu hỏi của user (mỗi lần hỏi, Buổi 4) → so với chunk → lấy chunk gần
nhất đưa LLM. Chạy được vì câu hỏi và đoạn trả lời nằm gần nhau trong không gian vector (Bài 3 kiểm). Một số model
(vd. multilingual-e5) yêu cầu đánh dấu `query:` / `passage:`.

Quan sát: cùng 1 câu, 2 lần chạy ra số hơi lệch (câu nghỉ phép, số đầu: `0.02442932…` lần Claude chạy vs
`0.02439880…` lần user chạy; "Hôm này là thứ mấy": số thứ 3 `-0.02693176…` vs `-0.02694702…`) → embedding API cũng
không hoàn toàn cố định (nối Buổi 12 câu 4). Lệch rất nhỏ, cosine gần như không đổi, nhưng **đừng so vector bằng
`==`**.

## Bài 2 — Cosine similarity

_(Code `cosine_similarity` + `run_bai2`: Claude viết theo yêu cầu, 2026-11-10 — user viết guard độ dài. Câu mẫu Claude
viết theo yêu cầu, từ output thật của `run_bai2`.)_

| Test                     | Kết quả |
| ------------------------ | ------- |
| Giống nhau → 1.0         | ✅ `[1,0]` vs `[1,0]` = 1.0; `[1,0]` vs `[5,0]` cũng = 1.0 (dài hơn nhưng cùng hướng) |
| Ngược chiều → -1.0       | ✅ `[1,0]` vs `[-1,0]` = -1.0 |
| Vuông góc → 0.0          | ✅ `[1,0]` vs `[0,1]` = 0.0 |
| Khác độ dài → lỗi        | ✅ `ValueError: Lengths must match: 2 != 3`; thêm: vector toàn 0 → `ValueError` (tránh chia cho 0) |
| Lệch so với numpy        | `0.00e+00` (cặp Việt ↔ Anh) → hàm tự viết đúng |

Kiểu tham số: dùng `Sequence[float]` thay `list[float]` — pyright báo `list[int]` không gán được cho `list[float]`
vì `list` là invariant; `Sequence` là covariant nên nhận cả `[1, 0]`.

Áp dụng cho 3 câu Bài 1 (`text-embedding-3-small`):

| Cặp                        | Cosine |
| -------------------------- | ------ |
| Việt ↔ Anh (cùng nghĩa)    | 0.5043 |
| Việt ↔ thời tiết (khác)    | 0.2209 |
| Anh ↔ thời tiết (khác)     | 0.0221 |

| \|v\| (độ dài vector) | Câu |
| --------------------- | --- |
| 1.000160 | Người lao động được nghỉ phép năm 12 ngày. |
| 0.999837 | Employees are entitled to 12 days of annual leave. |
| 1.000179 | Hôm nay trời Hà Nội mưa to. |

- **Cosine đo góc hay khoảng cách:** đo **góc** (hướng) giữa 2 vector, bỏ qua độ dài — `[1,0]` và `[5,0]` vẫn = 1.0.
  Trong embedding, **nghĩa nằm ở hướng**, nên câu cùng nghĩa → cùng hướng → cosine cao. Càng giống càng gần **1**
  (ngược với khoảng cách: càng giống càng gần 0). **Cosine distance = 1 − cosine** — pgvector (Buổi 2) dùng dạng
  distance, càng **nhỏ** càng gần → đừng nhầm chiều.
- **Vector chuẩn hoá thì cosine = tích vô hướng (dot product):** khi `|a| = |b| = 1` thì bước 4
  `dot / (1 × 1) = dot` → bỏ được 2 phép căn, nhanh hơn. Vì vậy vector DB hay có toán tử inner product; với vector độ
  dài 1, xếp hạng theo cosine, inner product hay khoảng cách L2 đều **ra cùng thứ tự**.
- **Ý nghĩa điểm:** cosine dùng để **xếp hạng**, không phải phần trăm (0.50 ≠ "giống 50%"). Mỗi model một thang điểm
  → chỉ so điểm **trong cùng model**. RAG lấy các chunk cosine **cao nhất**.

Quan sát (giả thuyết, Bài 3 kiểm tiếp):

- Cặp cùng nghĩa Việt ↔ Anh chỉ **0.50**, không gần 1. Thứ tự vẫn đúng.
- Việt ↔ thời tiết (0.22) cao gấp **10 lần** Anh ↔ thời tiết (0.02) dù 2 câu Việt không liên quan nghĩa →
  _giả thuyết_: vector mang cả thông tin **ngôn ngữ**, không chỉ nghĩa. Hệ quả RAG: câu hỏi tiếng Việt có thể được
  điểm cao với đoạn tiếng Việt không liên quan → cosine đo "vector gần", **chủ yếu** là nghĩa nhưng không chỉ nghĩa.
- \|v\| ≈ 1 nhưng không đúng tuyệt đối (0.9998–1.0002) → docs "normalized to length 1" đúng gần đúng. _Giả thuyết,
  chưa kiểm_: API trả số đã làm tròn (giá trị kiểu `0.0244293212890625` giống số thực độ chính xác thấp).

## Bài 3 — Cặp câu Việt/Anh

_(Code `run_bai3` + câu mẫu: Claude viết theo yêu cầu, 2026-11-10, từ output thật. `uv add sentence-transformers`:
user chạy → `sentence-transformers` 6.2.0, `torch` 2.15.0.)_

Model đa ngữ đã chọn: **`intfloat/multilingual-e5-small`** (Claude đề xuất, user đồng ý). Lý do: hôm nay cần hiểu
khái niệm, không cần model tốt nhất; nhẹ, tải/chạy nhanh; học thêm tiền tố `query:` / `passage:`. `BAAI/bge-m3`
(Notion gợi ý cho tiếng Việt, nặng hơn) để thử khi có eval set 30 câu (Buổi 6).

Model card e5 (`huggingface.co/intfloat/multilingual-e5-small`, README):

- "12 layers and the embedding size is **384**" (OpenAI: 1536).
- Tiền tố: "Use `query: ` prefix for **symmetric tasks** such as semantic similarity"; `query:` / `passage:` cho
  retrieval → Bài 3 (so cặp câu) dùng `query:` cả 2 phía; RAG (Buổi 4): câu hỏi `query:`, chunk `passage:`.
- Điểm cosine "distribute around **0.7 to 1.0**… what matters is the **relative order**" → so **thứ hạng**, không so
  điểm thô giữa 2 model.
- "truncated to at most **512 tokens**" → chunk 500 token (Buổi 3) vừa sát.

| Loại | Cặp | OpenAI | hạng | e5 | hạng |
| ---- | --- | ------ | ---- | -- | ---- |
| Diễn đạt lại | Nghỉ phép năm 12 ngày ↔ Mỗi năm được nghỉ 12 ngày có lương | 0.7433 | 2 | 0.9384 | 2 |
| Dịch Việt–Anh | Thời gian thử việc tối đa 60 ngày ↔ The probation period is at most 60 days | 0.5240 | 4 | 0.8446 | 5 |
| Cùng chữ, khác nghĩa | Bàn gỗ trong phòng họp ↔ Bàn kế hoạch tăng lương | 0.3073 | 6 | **0.8493** | **4** |
| **Phủ định** | Người lao động được làm thêm giờ ↔ … không được làm thêm giờ | **0.8628** | **1** | **0.9713** | **1** |
| Không dấu | Trợ cấp thôi việc ↔ tro cap thoi viec | 0.4635 | 5 | 0.8430 | 6 |
| Không liên quan | Hợp đồng lao động ↔ Công thức nấu phở bò | 0.2747 | 7 | 0.7817 | 7 |
| Câu hỏi ↔ đoạn | Thử việc được bao lâu? ↔ Thời gian thử việc không quá 60 ngày… | 0.5553 | 3 | 0.9054 | 3 |

Số chiều OpenAI 1536 · e5 384. Embed 14 câu: OpenAI ~1.4s (qua mạng) · e5 ~1.4s (local). OpenAI 196 token.
(Câu chỉ để so độ giống, con số trong câu không phải trích luật.)

- **Trái trực giác:** cặp **phủ định** đứng hạng 1 ở cả 2 model — nghĩa ngược nhau mà "giống nhất". e5 bị chữ "Bàn"
  đánh lừa (hạng 4, cao hơn cả cặp dịch thật); OpenAI xếp đúng ở thấp (hạng 6).
- **Phủ định:** embedding nắm **chủ đề**, không nắm **logic**. Hệ quả RAG: tìm "không được làm thêm giờ" có thể ra
  cả đoạn "được" → LLM phải đọc kỹ (Buổi 11).
- **So điểm 2 model trực tiếp được không:** **không**. e5 dồn trong 0.78–0.97 (đúng model card), OpenAI rải 0.27–0.86
  → chỉ so **thứ hạng** trong từng model.
- **Không dấu:** yếu ở cả 2 (hạng 5–6). User Việt hay gõ không dấu → quan trọng cho Project #2 (Buổi 9 hybrid search
  có thể giúp).
- **Tạm chọn model (chưa chốt): OpenAI** — tách cặp rõ hơn (dải điểm rộng, xử lý đúng "Bàn"), xử lý không dấu tốt hơn
  (xem ví dụ thực tế dưới), deploy dễ (API, không cần chạy torch trên server). _Giả thuyết từ vài cặp câu_ → Buổi 6
  chốt bằng eval set thật.

**Bài 3 để làm gì:** thử "bộ máy tìm kiếm" của RAG trước khi xây. Embedding quyết định LLM **được đọc đoạn luật nào**;
lấy sai đoạn thì LLM giỏi mấy cũng trả lời sai. (1) Chọn model là quyết định khó đổi (cột `vector(1536)` vs
`vector(384)`, đổi = embed lại toàn bộ). (2) Biết điểm mù trước user (phủ định, không dấu, chung chữ) → đưa vào eval
set Buổi 5. (3) Tập thói quen Phase 02: đo rồi mới quyết.

```
câu hỏi user → embed → tìm chunk luật gần nhất → LLM đọc → trả lời
                         ↑ Bài 3 kiểm bước này
```

### Ví dụ thực tế — chatbot luật lao động

_(Claude chạy 2026-11-10: 4 câu hỏi kiểu user × 5 đoạn giả lập điều luật do Claude tự viết, **không phải trích
luật**. Câu hỏi `query:`, đoạn `passage:` cho e5.)_

| Câu hỏi | OpenAI top 2 | e5 top 2 |
| ------- | ------------ | -------- |
| Tôi muốn nghỉ việc thì phải báo trước không? | ✅ A báo trước khi nghỉ việc 0.506 · B nghỉ phép năm 0.443 | ✅ A 0.883 · B 0.841 |
| Công ty có được bắt bà bầu làm thêm giờ không? | ✅ D **không được** làm thêm giờ 0.462 · C **được** làm thêm giờ **0.455** | ✅ D 0.897 · C 0.873 |
| Trợ cấp thôi việc ai trả? | ✅ E trợ cấp thôi việc **0.624** · B 0.428 | ✅ E 0.890 · A 0.839 |
| tro cap thoi viec ai tra? (không dấu) | ✅ E 0.365 · B 0.328 (thắng sát) | ❌ **E không có trong top 3** (B 0.794 · A 0.790 · D 0.787) |

- **Chung chữ "nghỉ":** đúng ở cả 2, nhưng "nghỉ phép" sát nút chỉ vì chung chữ → luật dài, nhiều đoạn "nghỉ" thì đoạn
  đúng có thể bị đẩy xuống.
- **Phủ định:** đoạn đúng "không được" thắng OpenAI chỉ **0.007** — gần hoà. Đảo thứ tự + chỉ lấy top 1 → bot trả lời
  "được" (sai nguy hiểm) → lý do RAG gửi **nhiều đoạn (top-k)** và LLM phải đọc kỹ.
- **Không dấu:** e5 trả **sai đoạn** → bot trả lời sai / "không tìm thấy"; OpenAI vẫn tìm ra nhưng kém chắc. → Lý do
  mạnh nhất tới giờ để nghiêng về OpenAI cho user Việt (test nhỏ, Buổi 6 xác nhận).
- Mỗi ca → 1 câu trong eval set Buổi 5: "nghỉ việc vs nghỉ phép", phủ định, câu không dấu.

## Bài 4 — Dữ liệu Bộ luật Lao động

| Mục                    | Quyết định / số đo (nguồn) |
| ---------------------- | -------------------------- |
| Bản dùng (số hiệu, ngày) | **18/VBHN-VPQH**, Văn phòng Quốc hội ban hành **12/02/2026**, Công báo số 131 ngày 28/02/2026 — hợp nhất BLLĐ 45/2019/QH14 với 3 luật sửa: 71/2025/QH15, 124/2025/QH15 (hiệu lực 01/01/2026), 113/2025/QH15 (Luật Dân số, hiệu lực 01/07/2026). Thay bản cũ 125/VBHN-VPQH (27/8/2025). Nguồn: trang Công báo + reghub.vn (Claude kiểm 2026-11-10) |
| Nguồn tải              | Chính thức: https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-18-vbhn-vpqh-468971.htm (có DOCX + PDF) |
| Định dạng              | **DOCX** (169 KB, file chính — chữ thật, có cấu trúc) + **PDF** (2.3 MB, 88 trang, bản đối chiếu; có 125 object `/Font` → _giả thuyết_: có lớp chữ, không phải scan). Kiểm DOCX (Claude, 2026-11-10): 1383 đoạn, ~191k ký tự, **17 Chương, 220 Điều** (Điều 1 "Phạm vi điều chỉnh" → Điều 220 "Hiệu lực thi hành"), có Điều 112 "Nghỉ lễ, tết", Điều 139 "Nghỉ thai sản"; phần đầu ghi rõ 3 luật sửa đổi |
| Folder                 | `projects/p2-labor-law-rag/data/raw/` — `18-VBHN-VPQH-2026.docx`, `18-VBHN-VPQH-2026.pdf` (Claude tải từ link Công báo, 2026-11-10) |
| Tổng token (`tiktoken`) | **95,759 token** với `cl100k_base` — đúng tokenizer của `text-embedding-3-small/large` (`tiktoken/model.py:47-48`). Cùng text: `o200k_base` (GPT-4o trở đi) = 52,509 → tokenizer cũ tốn gần **gấp đôi** với tiếng Việt. 191,485 ký tự, 41,814 từ → **2.29 token/từ** (cl100k). Đếm trên text trích nhanh từ DOCX (còn 1 đoạn rác XML, lệch không đáng kể). Claude đo 2026-11-10 |
| Ước tính số chunk      | 500 token/chunk, overlap 50 (bước 450): **~213 chunk** (không overlap: 192). 1 chunk 500 token ≈ **218 từ** tiếng Việt — ngắn hơn cảm giác. _Ước tính thô_: Buổi 3 cắt theo Điều (220 Điều, nhiều Điều ngắn) thì số chunk sẽ khác, có thể nhiều hơn |
| Ước tính chi phí embed | Giá (trang pricing, Claude đọc 2026-11-10, https://developers.openai.com/api/docs/pricing): `-3-small` **$0.02/1M**, `-3-large` $0.13/1M, `ada-002` $0.10/1M input token. Cả bộ có overlap (~106.5k token): small **≈ $0.002**, large ≈ $0.014. Embed lại 100 lần vẫn < $0.25 → chi phí embed **không phải** yếu tố chọn model; tiền thật nằm ở bước gọi LLM sinh câu trả lời |
| Kế hoạch tài liệu `internal` |                      |

⚠️ **Sắp có sửa đổi (theo báo chí, chưa xác nhận chính thức — Claude tìm 2026-11-10):** dự án Luật sửa đổi Bộ luật
Lao động (cùng Luật Lưu trữ, Bình đẳng giới, Hoạt động chữ thập đỏ) Quốc hội thảo luận 9/11/2026, **dự kiến biểu
quyết 21/11/2026**, hiệu lực dự kiến 01/3/2027; riêng **Điều 112 (nghỉ lễ, Tết)** có hiệu lực ngay khi thông qua —
đề xuất thêm 24/11 và 27/7, từ 11 lên 13 ngày/năm. → 18/VBHN-VPQH **chưa** gồm sửa đổi này.
Hệ quả: (1) eval set Buổi 5 **tránh** câu về số ngày nghỉ lễ (Điều 112), hoặc ghi rõ "theo bản 18/VBHN-VPQH";
(2) sau 21/11 kiểm Công báo → khi có bản hợp nhất mới = ca test thật cho **vòng đời tài liệu** (Buổi 13–15:
`doc_id`, `content_hash`, chỉ re-embed điều bị đổi).

- Vì sao luật hợp với RAG:
- Luật sửa đổi → Project #2 xử lý thế nào:

## Câu phỏng vấn cuối buổi

### 1. Embedding là gì? Khác gì token ID?

### 2. Vì sao dùng cosine similarity?

### 3. Chọn model embedding cho chatbot tiếng Việt thế nào?
