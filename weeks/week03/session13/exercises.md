# Buổi 13 — Phase 02 Buổi 1: Embeddings & Vector Space (2h)

Phase 02 — RAG + Evals (Tuần 3–5). Nguồn: Notion "Phase 02 — RAG + Evals" (đọc 2026-11-10).

Checklist Notion Buổi 1:

- Embeddings là gì; thử OpenAI embedding + 1 model đa ngữ (multilingual-e5 / BGE-M3 — quan trọng cho tiếng Việt)
- Tự viết cosine similarity, so sánh độ tương đồng các cặp câu Việt/Anh
- Chốt dữ liệu domain, gom về 1 folder

**Domain đã chọn (2026-11-10): Bộ luật Lao động Việt Nam.** Bộ dữ liệu này dùng suốt Phase 02 (chunk → pgvector →
eval set 30 câu → chia quyền public/internal → Project #2), nên Bài 4 quan trọng không kém phần code.

| Phần                                        | Thời lượng | Làm ở đâu      |
| ------------------------------------------- | ---------- | -------------- |
| Setup + đọc docs embeddings                 | ~15ph      | mục Setup      |
| Bài 1: gọi OpenAI embedding, nhìn vector    | ~20ph      | `exercises.py` |
| Bài 2: tự viết cosine similarity            | ~20ph      | `exercises.py` |
| Bài 3: so cặp câu Việt/Anh, OpenAI vs đa ngữ | ~40ph      | `exercises.py` |
| Bài 4: chốt dữ liệu Bộ luật Lao động        | ~25ph      | `notes.md`     |

Bài 3 phần model đa ngữ nặng (tải model vài trăm MB → vài GB). Không kịp thì làm OpenAI trước, model đa ngữ để buổi
sau — nhưng **phải** làm trước Buổi 6 (đo baseline), vì chọn model embedding ảnh hưởng mọi con số sau đó.

---

## Setup (tự làm)

- [ ] Đọc docs: https://developers.openai.com/api/docs/guides/embeddings — embedding là gì, model nào, số chiều,
      `dimensions` để rút gọn, giá. Ghi vào `notes.md` mục Setup.
- [ ] Code bài tập viết ở `exercises.py` cùng thư mục (tự tạo, theo mẫu các buổi trước). Chạy:
      `uv run python weeks/week03/session13/exercises.py`.
- [ ] Không cần key mới: dùng `OPENAI_API_KEY` trong `.env` ở gốc repo như Phase 01.

---

## Bài 1 — Gọi OpenAI embedding, nhìn vector (~20ph)

Gọi `client.embeddings.create(...)` với `model="text-embedding-3-small"` cho 3 câu, ví dụ:

- "Người lao động được nghỉ phép năm 12 ngày."
- "Employees are entitled to 12 days of annual leave."
- "Hôm nay trời Hà Nội mưa to."

Tự trả lời (ghi bảng trong `notes.md`):

1. Mỗi vector có bao nhiêu số? 3 câu dài ngắn khác nhau thì số chiều có khác không? Vì sao điều này quan trọng khi
   lưu vào DB?
2. In 5 số đầu của mỗi vector — đọc được nghĩa gì từ từng số không?
3. Tính độ dài vector (căn bậc hai tổng bình phương). Ra bao nhiêu? Docs nói gì về việc vector đã **chuẩn hoá**?
4. `response.usage` báo bao nhiêu token? Có `output_tokens` không — vì sao?
5. Gửi 1 lần 3 câu (list) hay 3 lần mỗi lần 1 câu — khác gì (số request, thứ tự kết quả)?

Nối với Phase 01 (Buổi 12 câu 5c): token → **vector** là bước đầu của transformer. Embedding API trả về một vector
cho **cả câu**, không phải từng token. Đây là điểm khác cần ghi lại.

## Bài 2 — Tự viết cosine similarity (~20ph)

- [ ] `def cosine_similarity(a: list[float], b: list[float]) -> float` — **Python thuần**, không numpy.
- [ ] Test tay (pytest hoặc `assert`): vector giống nhau → `1.0`; ngược chiều → `-1.0`; vuông góc → `0.0`; 2 vector
      khác độ dài → báo lỗi rõ ràng (không trả số sai).
- [ ] So với `numpy` (có sẵn vì `pandas` kéo về) — kết quả lệch bao nhiêu? Lệch nhỏ cỡ `1e-16` có sao không?

Tự trả lời:

1. Cosine đo cái gì: **góc** hay **khoảng cách**? Vì sao bỏ qua độ dài vector?
2. Nếu vector đã chuẩn hoá (Bài 1 câu 3) thì cosine = phép tính nào đơn giản hơn? Vì sao vector DB hay dùng điều
   này (gợi ý cho Buổi 2: pgvector có toán tử cho inner product / cosine / L2)?

## Bài 3 — So cặp câu Việt/Anh: OpenAI vs model đa ngữ (~40ph)

Dùng câu theo chủ đề luật lao động (khớp domain). Gợi ý 6 loại cặp — tự viết thêm:

| Loại cặp                     | Ví dụ                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| Diễn đạt lại (Việt–Việt)     | "Nghỉ phép năm 12 ngày" ↔ "Mỗi năm được nghỉ 12 ngày có lương"                        |
| Dịch (Việt–Anh)              | "Thời gian thử việc tối đa 60 ngày" ↔ "The probation period is at most 60 days"      |
| Cùng chữ, khác nghĩa         | "Bàn gỗ trong phòng họp" ↔ "Bàn kế hoạch tăng lương"                                  |
| Phủ định                     | "Người lao động được làm thêm giờ" ↔ "Người lao động không được làm thêm giờ"         |
| Không dấu                    | "Trợ cấp thôi việc" ↔ "tro cap thoi viec"                                             |
| Không liên quan              | "Hợp đồng lao động" ↔ "Công thức nấu phở bò"                                          |

Các con số trong ví dụ chỉ là câu để so độ giống, **không** phải trích luật — đừng chép làm đáp án eval.

- [ ] Chạy với `text-embedding-3-small` → bảng điểm cosine.
- [ ] Chạy cùng các cặp với **1 model đa ngữ chạy local**. Tự chọn và ghi lý do vào `notes.md`:
  - `intfloat/multilingual-e5-small` (nhẹ) hoặc `BAAI/bge-m3` (nặng hơn, Notion gợi ý cho tiếng Việt)
  - Đọc **model card** trước khi dùng: model có yêu cầu thêm tiền tố vào câu không (vd. e5 dùng `query:` /
    `passage:` — tự kiểm)? Số chiều bao nhiêu? Chạy local cần thư viện gì (`uv add ...`)?
- [ ] Đặt 2 bảng cạnh nhau trong `notes.md`.

Tự trả lời:

1. Cặp nào điểm cao/thấp **trái với trực giác**? Đặc biệt cặp **phủ định** — điểm có cao không? Hệ quả gì cho RAG
   (search "không được" có thể ra đoạn "được")?
2. Điểm tuyệt đối của 2 model có so trực tiếp được không (vd. 0.8 của model A vs 0.8 của model B)? Nên so cái gì?
3. Câu không dấu: model nào chịu được tốt hơn? User Việt hay gõ không dấu → quan trọng cho Project #2.
4. So 2 model theo: chất lượng (bảng trên), chi phí, tốc độ, chạy ở đâu (API vs local), số chiều. Tạm chọn model
   nào cho Phase 02? (Chưa chốt — Buổi 6 có số đo thật mới chốt.)

## Bài 4 — Chốt dữ liệu Bộ luật Lao động (~25ph)

- [ ] **Bản nào?** Bộ luật Lao động 2019 (số 45/2019/QH14, hiệu lực 01/01/2021) **đã bị sửa** bởi nhiều luật sau
      (vd. Luật Dân số 113/2025/QH15 sửa Điều 139 thai sản, hiệu lực 01/7/2026 — theo kết quả tìm kiếm của Claude
      2026-11-10, **tự kiểm lại**). Dùng **văn bản hợp nhất mới nhất** (Claude tìm thấy 18/VBHN-VPQH ngày
      12/02/2026 — tự kiểm còn là bản mới nhất không). Dùng bản gốc 2019 → đáp án eval sai.
- [ ] **Lấy ở đâu?** Ưu tiên nguồn chính thức: Cơ sở dữ liệu quốc gia về văn bản pháp luật (vbpl.vn), Công báo.
      Trang thứ ba (thuvienphapluat, luatvietnam) tiện đọc nhưng có điều khoản sử dụng riêng → ghi rõ nguồn đã dùng.
      Văn bản quy phạm pháp luật **không** thuộc đối tượng bảo hộ quyền tác giả (Luật SHTT Điều 15 — tự kiểm câu
      chữ), nên đưa vào demo công khai được.
- [ ] **Định dạng?** PDF / DOC / HTML — ghi lại. Buổi 3 phải đọc + làm sạch file này (PDF scan = ảnh thì không
      lấy được chữ → tránh).
- [ ] **Gom về 1 folder.** Đề xuất: `projects/p2-labor-law-rag/data/raw/` (Project #2 ở Tuần 5 dùng lại). Tự quyết,
      ghi vào `notes.md`.
- [ ] **Đo kích thước:** đếm token cả bộ luật bằng `tiktoken` (như Buổi 12 câu 5a) → ước tính số chunk (500 token /
      chunk ở Buổi 3) và **chi phí embed** cả bộ (giá lấy từ trang pricing OpenAI, ghi nguồn).
- [ ] **Chuẩn bị chia quyền (dùng ở Buổi 3, Buổi 8):** Bộ luật = nhóm `public`. Cần thêm 1 tài liệu nhóm `internal`
      để test rò rỉ — vd. tự viết 2–3 trang "Nội quy lao động Công ty ABC (nội bộ)": mức thưởng, lương theo bậc,
      quy trình kỷ luật. **Toàn bộ là giả**, ghi rõ trong file. Chưa cần viết hôm nay, chỉ cần ghi kế hoạch.

Tự trả lời:

1. Vì sao domain luật hợp với RAG (cấu trúc Chương → Mục → Điều → Khoản; hỏi đáp có đáp án rõ; hay bị sửa đổi)?
2. Luật bị sửa thường xuyên → Project #2 phải làm gì khi có bản hợp nhất mới (nối với "vòng đời tài liệu", Buổi
   13–15: `doc_id`, `content_hash`)?

---

## Câu phỏng vấn cuối buổi (tự trả lời 3–5 dòng, không nhìn notes)

1. Embedding là gì? Khác gì token ID?
2. Vì sao dùng cosine similarity mà không dùng khoảng cách thông thường?
3. Chọn model embedding cho chatbot tiếng Việt thế nào?
